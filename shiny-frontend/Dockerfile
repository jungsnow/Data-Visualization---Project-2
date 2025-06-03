FROM rocker/shiny:latest

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install R packages
RUN R -e "install.packages(c('shiny', 'shinydashboard', 'DT', 'plotly', 'httr', 'jsonlite', 'dplyr'), repos='https://cran.rstudio.com/')"

# Remove the default shiny app
RUN rm -rf /srv/shiny-server/*

# Copy our app
COPY app.R /srv/shiny-server/

# Make sure the app is owned by shiny user
RUN chown -R shiny:shiny /srv/shiny-server

# Expose port
EXPOSE 3838

# Run shiny server
CMD ["/usr/bin/shiny-server"]
