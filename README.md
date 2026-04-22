# SCI Visualization Dashboard

Automate the processing of SCI metrics from Excel files, store them in InfluxDB, and visualize them on a Grafana dashboard.

## Project Structure

- `Final Metrics/`: Folder containing Excel files with SCI data.
- `grafana-dashboards/`: Provisioned Grafana dashboard JSON.
- `grafana-provisioning/`: Configuration for Grafana datasources and dashboards.
- `sci_db_publisher.py`: Python script to process Excel files and push data to InfluxDB.
- `docker-compose.yml`: Docker configuration for InfluxDB and Grafana.

## Prerequisites

- Docker and Docker Compose
- Python 3.x
- Required Python packages: `pandas`, `numpy`, `influxdb-client`, `openpyxl`, `python-dotenv`
- Electricity Map API key (for fetching real-time Grid Emission Factor data)

## How to Run the Pipeline

### 1. Setup Environment Variables

Copy the example environment file and update it with your Electricity Map API key:

```bash
cp .env.example .env
```

Edit `.env` and add your Electricity Map API token (obtain from https://www.electricitymap.org/):

```env
GEF_API_TOKEN=your_api_token_here
USE_WEB_GEF=true
```

**Note:** The GEF (Grid Emission Factor) values are fetched for:
- **Mumbai** (IN-WE): Western India region
- **Bengaluru** (IN-SO): Southern India region

### 2. Start the Database and Dashboard Services

Run the following command in the project root:

```bash
docker compose up -d
```

*This starts InfluxDB on port `8086` and Grafana on port `3000`.*

**Note on Permissions:** If Grafana fails to load dashboards, ensure that the `grafana-provisioning` and `grafana-dashboards` directories have appropriate read permissions:
```bash
sudo chmod -R 755 grafana-provisioning grafana-dashboards
```

### 3. Process Data and Push to InfluxDB

Install dependencies and run the publisher script. This will read all Excel files in the `Final Metrics/` folder, calculate the SCI averages, fetch region-specific GEF values from the Electricity Map API, and write the records to InfluxDB.

```bash
pip install pandas numpy influxdb-client openpyxl python-dotenv requests
python3 sci_db_publisher.py
```

*You should see a success message indicating `Successfully wrote records to InfluxDB.`*

**GEF Values:** The script fetches real-time carbon intensity data for:
- Mumbai region (IN-WE) 
- Bengaluru region (IN-SO)

If the API is unavailable or `USE_WEB_GEF` is false, the script falls back to GEF values in the Excel files.

### 4. Stopping Services and Removing Data

To shut down all services, run 
```bash
docker compose down -v
```
Note that this will also remove the InfluxDB data.


### 5. View the Dashboards

1. Open your browser and navigate to **http://localhost:3000**
2. **Log in** using the default credentials:
   - Username: `admin`
   - Password: `admin`
3. In the left-hand menu, navigate to **Dashboards**.
4. Open the **Sustainability** folder.
5. Open the **SCI Comparative Dashboard**.

## Customization

- **InfluxDB credentials**: Update the `.env` file and restart services.
- **GEF API**: Configure `GEF_API_TOKEN` in `.env` to fetch real-time carbon intensity data from Electricity Map.
- **Web GEF fetching**: Set `USE_WEB_GEF=true` to enable web API calls; set to `false` to use Excel fallback values.
- The dashboard is automatically provisioned from `grafana-dashboards/sci_dashboard.json`.
