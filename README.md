# Data-Visualization---Project-2
## COMP4010/5120 Spring 2025 — Project 2 Proposal

### Project Title
Data Pipeline & Visualization for eSports Metrics: Teamfight Tactics / League of Legends

---

### 1. High-Level Goal (One Sentence)
Build a fully reproducible R-based data pipeline that ingests real-time match and champion statistics from the Riot Games API, stores it in PostgreSQL, and produces interactive visualizations to explore performance trends in TFT and LoL.

---

### 2. Motivation & Objectives (1–2 Paragraphs)
**Motivation:**
Many players—especially newcomers—struggle to make optimal in-game decisions around champion selection, item builds, and rune choices. By centralizing live match and champion statistics from the Riot API into a user-friendly visualization system, we can deliver actionable suggestions at key decision points: which champion to pick, what items to buy, which runes to set, etc. This empowers both novice and experienced players to refine their strategies and improve performance as they play.

**Objectives:**
1. **Automated Ingestion:** Periodically pull match histories, champion stats, and meta-data from Riot’s REST API.  
2. **Data Cleaning & Transformation:** Use tidyverse tools in R to normalize fields, handle missing values, and compute derived metrics (e.g., win rates by patch, average gold per minute).  
3. **Storage:** Persist raw and cleaned tables in PostgreSQL for efficient querying and version control.  
4. **Scheduling:** Leverage Apache Airflow (or Apache Kafka) to orchestrate daily or hourly pipeline runs.  
5. **Visualization:** Develop interactive/quasi-interactive dashboards and static reports in RMarkdown/Quarto, showcasing meta shifts over time, champion performance distributions, and player progression.

---

### 3. Data Collection & Metadata
- **Source:** Riot Games Developer API (https://developer.riotgames.com).  
- **Endpoints:**  
  - Match V5 (match lists, timelines)  
  - League V4 (ranked stats)  
  - Static Data (champion info, patches)  
- **Collection Method:**  
  - `httr`/`curl` in R to authenticate with API key and retrieve JSON.  
  - Rate-limiting handled via retry/backoff in the pipeline.  
- **Metadata Tracked:**  
  - Request timestamp, region, patch version, response code  
  - Data schema versions for reproducibility (lock via `renv`)  
- **Volume Estimate:**  
  - ~10,000 matches per day across NA/EUW servers  
  - Champion metadata ~200 records per patch  

---

### 4. Weekly Plan & Team Assignments
| Week               | Dates            | Tasks                                                                                                      |
|--------------------|------------------|------------------------------------------------------------------------------------------------------------|
| **Week 1**         | 21/04 – 27/04    | ‑ Form team & define roles<br>‑ Finalize endpoints & data schema<br>‑ Draft proposal (this document)<br>‑ Create GitHub repo with README | 
| **Week 2**         | 27/04 – 04/05    | ‑ Peer reviews on two repos (issues on GitHub)<br>‑ Begin API ingestion module in R<br>‑ Set up `renv`<br>‑ Start Dockerized PostgreSQL service    | 
| **Week 3**         | 05/05 – 15/05    | ‑ Address peer-review feedback on proposal<br>‑ Implement cleaning/`tidyr` workflows<br>‑ Define `targets` pipeline<br>‑ Design initial viz prototypes        | 
| **Week 4**         | 16/05 – 30/05    | ‑ Finalize data-loading DAG in Airflow (or Kafka connectors)<br>‑ Build interactive dashboards in Quarto/Shiny<br>‑ Polish write‑up & code documentation<br>‑ Prepare slides  |
---


