 Jellyfin Analytics Pipeline

End-to-end data engineering project extracting play history from Jellyfin's 
REST API, transforming with dbt, and visualizing in Grafana.

## Stack
- **Ingestion**: Python, Jellyfin REST API
- **Storage**: PostgreSQL
- **Transformation**: dbt
- **Visualization**: Grafana
- **Infrastructure**: Oracle Cloud, Ubuntu, Nginx

## Architecture
Jellyfin API → Python → PostgreSQL → dbt → Grafana

## Setup
1. Clone the repo
2. Copy `.env.example` to `.env` and fill in your values
3. Run `pip install -r requirements.txt`
4. Run `python3 extract.py`
5. Run `dbt run`
