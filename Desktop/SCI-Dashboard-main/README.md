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
- Required Python packages: `pandas`, `numpy`, `influxdb-client`, `openpyxl`

## How to Run the Pipeline

### 1. Setup Environment Variables

Copy the example environment file and update it if necessary:

```bash
cp .env.example .env
```

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

Install dependencies and run the publisher script. This will read all Excel files in the `Final Metrics/` folder, calculate the SCI averages, and write the records to InfluxDB.

```bash
pip install pandas numpy influxdb-client openpyxl
python3 sci_db_publisher.py
```

*You should see a success message indicating `✅ Successfully wrote 16 records to InfluxDB.`*

### 4. View the Dashboards

1. Open your browser and navigate to **http://localhost:3000**
2. **Log in** using the default credentials:
   - Username: `admin`
   - Password: `admin`
3. In the left-hand menu, navigate to **Dashboards**.
4. Open the **Sustainability** folder.
5. Open the **SCI Comparative Dashboard**.

## Customization

- To change InfluxDB credentials, update the `.env` file and restart the services.
- The dashboard is automatically provisioned from `grafana-dashboards/sci_dashboard.json`.
