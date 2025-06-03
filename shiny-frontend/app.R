# app.R
library(shiny)
library(shinydashboard)
library(DT)
library(plotly)
library(httr)
library(jsonlite)
library(dplyr)

# UI
ui <- dashboardPage(
  dashboardHeader(title = "TFTChamp - R Shiny"),
  
  dashboardSidebar(
    sidebarMenu(
      id = "sidebar",
      menuItem("Feature Importances", tabName = "featureImportance", icon = icon("chart-bar")),
      # menuItem("Augments", tabName = "augment", icon = icon("align-left")),
      menuItem("Items", tabName = "item", icon = icon("box")),
      menuItem("Compositions", tabName = "comp", icon = icon("timeline")),
      menuItem("All Matches", tabName = "allMatch", icon = icon("table")),
      menuItem("Recent Matches", tabName = "recentMatch", icon = icon("list"))
      # menuItem("Predict", tabName = "predict", icon = icon("brain"))
    ),
    
    # Region/League selectors
    selectInput("region", "Region:",
                choices = list("NA1" = "na1", "KR" = "kr", "EUW1" = "euw1"),
                selected = "na1"),
    
    selectInput("league", "League:",
                choices = list("Challengers" = "challengers", 
                               "Grandmasters" = "grandmasters", 
                               "Masters" = "masters"),
                selected = "challengers")
  ),
  
  dashboardBody(
    tabItems(
      # 1) Feature Importance
      tabItem(tabName = "featureImportance",
        fluidRow(
          box(width = 12, title = "Feature Importances",
              plotlyOutput("featureImportancePlot", height = "600px")
          )
        )
      ),
      
      # 2) Augments section
      # tabItem(tabName = "augment",
      #   fluidRow(
      #     box(width = 12, title = "Augments",
      #         uiOutput("augmentCards")
      #     )
      #   )
      # ),
      
      # 3) Items section
      tabItem(tabName = "item",
        fluidRow(
          box(width = 12, title = "Items",
              uiOutput("itemCards")
          )
        )
      ),
      
      # 4) Compositions section
      tabItem(tabName = "comp",
        fluidRow(
          box(width = 12, title = "Compositions",
              uiOutput("compCards")
          )
        )
      ),
      
      # 5) All Matches table
      tabItem(tabName = "allMatch",
        fluidRow(
          box(width = 12, title = "All Matches",
              DT::dataTableOutput("matchTable")
          )
        )
      ),
      
      # 6) Recent Matches table
      tabItem(tabName = "recentMatch",
        fluidRow(
          box(width = 12, title = "Recent Matches",
              DT::dataTableOutput("recentMatchTable")
          )
        )
      )
      
      # 7) Predict tab (placeholder)
      # tabItem(tabName = "predict",
      #   fluidRow(
      #     box(width = 12, title = "Predict",
      #         h3("Work in Progress"),
      #         textOutput("versionInfo")
      #     )
      #   )
      # )
    )
  )
)

# Server
server <- function(input, output, session) {
  
  # 3.1) Base URL for API (change host/port if needed)
    api_base <- reactive({
    Sys.getenv("API_BASE_URL", "http://localhost:8000")
    })

  
  # 3.2) Fetch metadata (latest_version / latest_patch)
  metadata <- reactive({
    req(input$region, input$league)
    tryCatch({
      res <- GET(paste0(api_base(), "/metadata"))
      if (status_code(res) == 200) {
        content(res, "parsed")
      } else {
        list(latest_version = "", latest_patch = "")
      }
    }, error = function(e) {
      list(latest_version = "", latest_patch = "")
    })
  })
  
  # 3.3) Feature Importance Plot
  output$featureImportancePlot <- renderPlotly({
    req(input$region, input$league)
    meta <- metadata()
    query_params <- list(
      platform = input$region,
      league = input$league,
      version = meta$latest_version,
      patch   = meta$latest_patch
    )
    
    tryCatch({
      res <- GET(paste0(api_base(), "/feature_importance"), query = query_params)
      if (status_code(res) == 200) {
        data <- content(res, "parsed")
        if (length(data$results) > 0) {
          df <- data.frame(
            label = sapply(data$results, function(x) x$label),
            feature_importance = sapply(data$results, function(x) x$feature_importance),
            stringsAsFactors = FALSE
          )
          
          p <- plot_ly(
            df,
            y = ~reorder(label, feature_importance),
            x = ~feature_importance,
            type = 'bar',
            orientation = 'h',
            marker = list(color = '#387908'),
            text = ~round(feature_importance, 2),
            textposition = 'outside'
          ) %>%
            layout(
              title = paste("Feature Importances (", input$region, input$league, ")"),
              xaxis = list(title = "Feature Importance"),
              yaxis = list(title = "Features"),
              margin = list(l = 280, r = 50, t = 50, b = 50)
            )
          
          return(p)
        }
      }
      plot_ly() %>% layout(title = "No data available")
    }, error = function(e) {
      plot_ly() %>% layout(title = paste("Error loading data:", e$message))
    })
  })
  
  # 3.4) Helper to build “media cards” for augment / item / comp
  create_media_cards <- function(card_type) {
    req(input$region, input$league)
    meta <- metadata()
    query_params <- list(
      platform = input$region,
      league = input$league,
      version = meta$latest_version,
      patch   = meta$latest_patch
    )
    
    tryCatch({
      res <- GET(paste0(api_base(), "/image/"), query = query_params)
      if (status_code(res) == 200) {
        data <- content(res, "parsed")
        
        # Filter only those whose URI contains card_type string
        # (e.g. “augment”, “item” or “comp”)
        all_uris <- sapply(data$results, function(x) tolower(x$uri))
        keep_idx <- grepl(card_type, all_uris)
        filtered_images <- data$results[keep_idx]
        
        if (length(filtered_images) > 0) {
          card_list <- lapply(filtered_images, function(image) {
            # Build the image URL (append query params so the backend can sign or serve it)
            img_src <- paste0(
              api_base(), "/image/", image$uri, "?",
              paste(names(query_params), query_params, sep = "=", collapse = "&")
            )
            # A Bootstrap‐style card
            div(class = "col-md-4",
                div(class = "card mb-3",
                    img(src = img_src,
                        class = "card-img-top",
                        style = "max-height: 200px; object-fit: contain;"),
                    div(class = "card-body",
                        h5(class = "card-title", image$uri),
                        p(class = "card-text", image$description)
                    ),
                    div(class = "card-footer",
                        actionButton(
                          inputId = paste0("learn_", gsub("[^A-Za-z0-9]", "_", image$uri)),
                          label = "Learn More",
                          class = "btn btn-sm btn-secondary",
                          onclick = paste0("window.open('", img_src, "', '_blank')")
                        )
                    )
                )
            )
          })
          return(div(class = "row", card_list))
        }
      }
      return(div("No images available"))
    }, error = function(e) {
      return(div(paste("Error loading images:", e$message)))
    })
  }
  
  output$augmentCards <- renderUI({ create_media_cards("augment") })
  output$itemCards    <- renderUI({ create_media_cards("item") })
  output$compCards    <- renderUI({ create_media_cards("comp") })
  
  # 3.5) Match data (All Matches and Recent Matches)
  match_data <- reactive({
    req(input$region, input$league)
    query_params <- list(
      platform = input$region,
      league   = input$league,
      skip     = 0,
      limit    = 100
    )
    
    tryCatch({
      res <- GET(paste0(api_base(), "/match"), query = query_params)
      if (status_code(res) == 200) {
        data <- content(res, "parsed")
        if (length(data$results) > 0) {
          # Convert list elements to a data.frame; drop Mongo _id
          rows <- lapply(data$results, function(x) {
            x[names(x) != "_id"]
          })
          return(bind_rows(rows))
        }
      }
      return(tibble::tibble())  # empty tibble if no results
    }, error = function(e) {
      return(tibble::tibble())
    })
  })
  
  output$matchTable <- DT::renderDataTable({
    df <- match_data()
    if (nrow(df) > 0) {
      DT::datatable(
        df,
        options = list(
          pageLength = 25,
          scrollX    = TRUE,
          dom        = 'Bfrtip'
        ),
        caption = htmltools::tags$caption(
          style = 'caption-side: bottom; text-align: left;',
          paste("Recent Matches (", input$region, input$league, ")")
        )
      )
    } else {
      DT::datatable(data.frame(Message = "No data available"))
    }
  })
  
  output$recentMatchTable <- DT::renderDataTable({
    df <- match_data()
    if (nrow(df) > 0) {
      recent_df <- head(df, 50)
      DT::datatable(
        recent_df,
        options = list(
          pageLength = 10,
          scrollX    = TRUE
        ),
        caption = htmltools::tags$caption(
          style = 'caption-side: bottom; text-align: left;',
          paste("Recent Matches (", input$region, input$league, ")")
        )
      )
    } else {
      DT::datatable(data.frame(Message = "No data available"))
    }
  })
  
  # 3.6) Version info for Predict tab
  output$versionInfo <- renderText({
    meta <- metadata()
    paste("Current version:", meta$latest_version, "| Patch:", meta$latest_patch)
  })
}

# Run the app
shinyApp(ui = ui, server = server)

