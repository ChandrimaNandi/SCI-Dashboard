import pandas as pd
import numpy as np
import os
import glob
import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "demo_token_please_change")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "demo_org")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "demo_bucket")
METRICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Final Metrics")

# GEF Configuration
USE_WEB_GEF = os.getenv("USE_WEB_GEF", "False").lower() == "true"
GEF_API_URL = os.getenv("GEF_API_URL", "https://api.electricitymap.org/v3/carbon-intensity/latest")
GEF_API_TOKEN = os.getenv("GEF_API_TOKEN", "")

def calculate_pactive(cpu_util):
    conditions = [
        (cpu_util >= 0.0) & (cpu_util < 0.1),
        (cpu_util >= 0.1) & (cpu_util < 0.5),
        (cpu_util >= 0.5) & (cpu_util < 1.0),
        (cpu_util >= 1.0)
    ]
    choices = [
        0.00121 + (cpu_util * 0.0184),
        0.00305 + ((cpu_util - 0.1) * 0.010275),
        0.00716 + ((cpu_util - 0.5) * 0.0056),
        0.00996 
    ]
    return np.select(conditions, choices, default=0)

def fetch_gef_from_web(city):
    """
    Fetch Grid Emission Factor (GEF) values from web API.
    
    Args:
        city (str): City name ('Mumbai' or 'Bengaluru')
        
    Returns:
        float: GEF value in grams of CO2 per kWh, or None if fetch fails
    """
    try:
        # Map city names to API country codes
        city_mapping = {
            'Mumbai': 'IN-WE',  # Western India
            'Bengaluru': 'IN-SO',  # Southern India
            'India': 'IN'
        }
        
        country_code = city_mapping.get(city, 'IN')
        
        headers = {}
        if GEF_API_TOKEN:
            headers['auth-token'] = GEF_API_TOKEN
        
        # Query the API
        params = {'countryCode': country_code}
        response = requests.get(GEF_API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract carbon intensity (in grams CO2/kWh)
        if 'carbonIntensity' in data:
            gef_value = data['carbonIntensity']
            print(f"Fetched GEF for {city}: {gef_value:.4f}")
            return gef_value
        else:
            print(f"Warning: Could not extract GEF from API response for {city}")
            return None
            
    except Exception as e:
        print(f"Error fetching GEF for {city} from web: {e}")
        return None


def calculate_sci(file_path):
    df = pd.read_excel(file_path)
    
    # Drop rows without an instance and standardize WA app names
    df = df.dropna(subset=['Instance'])
    if os.path.basename(file_path).startswith("WA-"):
        df['Instance'] = df['Instance'].replace('Frontend', 'Web')

    # --- GEF VALUES HANDLING ---
    if USE_WEB_GEF:
        print("Fetching GEF values from web API...")
        gef_mumbai = fetch_gef_from_web('Mumbai')
        gef_bengaluru = fetch_gef_from_web('Bengaluru')

        # Override per-row GEF columns with web-fetched scalar if fetch succeeded
        if gef_mumbai is not None:
            print(f"Using GEF_Mumbai from web: {gef_mumbai}")
            df['GEF_Mumbai'] = gef_mumbai
        else:
            print("Web fetch failed for Mumbai, falling back to Excel GEF_Mumbai column.")

        if gef_bengaluru is not None:
            print(f"Using GEF_Bengaluru from web: {gef_bengaluru}")
            df['GEF_Bengaluru'] = gef_bengaluru
        else:
            print("Web fetch failed for Bengaluru, falling back to Excel GEF_Bengaluru column.")

    # Ensure GEF columns exist (fallback default if missing from Excel)
    if 'GEF_Mumbai' not in df.columns:
        print("GEF_Mumbai column not found in Excel, defaulting to 0.73")
        df['GEF_Mumbai'] = 0.73
    if 'GEF_Bengaluru' not in df.columns:
        print("GEF_Bengaluru column not found in Excel, defaulting to 0.73")
        df['GEF_Bengaluru'] = 0.73

    # --- 1. INTERVAL CALCULATIONS ---
    df['p_active'] = calculate_pactive(df['CPU_Utilization'])
    df['E_CPU'] = (0.00121 + df['p_active']) * (5/60)
    df['E_NET'] = ((df['Nw_In'] + df['Nw_Out']) / (1024**3)) * 0.0065 * df['GEF_Mumbai']
    df['E_EU'] = (0.045 * (5/60)) * df['GEF_Bengaluru']
    df['E_DC'] = 0.792 + (df['E_CPU'] * 1.15 * df['GEF_Mumbai'])
    df['Interval_Emissions'] = df['E_NET'] + df['E_DC'] + df['E_EU']

    # --- 2. INSTANCE & ITERATION SUMMARIES ---
    # Sum intervals to get Instance Totals
    instance_summary = df.groupby(['Iteration', 'Instance'])[['Interval_Emissions', 'E_DC', 'E_EU', 'E_NET']].sum().reset_index()
    instance_summary.rename(columns={'Interval_Emissions': 'Total_Instance_Emissions'}, inplace=True)

    # Sum instances to get Iteration Totals and SCI
    iteration_summary = instance_summary.groupby('Iteration')['Total_Instance_Emissions'].sum().reset_index()
    iteration_summary.rename(columns={'Total_Instance_Emissions': 'Total_Iteration_Emissions'}, inplace=True)
    iteration_summary['Iteration_SCI'] = iteration_summary['Total_Iteration_Emissions'] / 1000

    # Calculate Average SCI
    avg_sci = iteration_summary['Iteration_SCI'].mean()
    
    # Calculate per-instance averages across iterations (including energy components)
    instance_avg = instance_summary.groupby('Instance')[['Total_Instance_Emissions', 'E_DC', 'E_EU', 'E_NET']].mean().reset_index()
    return avg_sci, instance_avg

def main():
    excel_files = glob.glob(os.path.join(METRICS_DIR, "*.xlsx"))
    if not excel_files:
        print(f"No files found in {METRICS_DIR}")
        return

    print(f"Found {len(excel_files)} files to process.")

    # Initialize InfluxDB Client
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    points = []
    
    for file_path in excel_files:
        basename = os.path.basename(file_path).replace('.xlsx', '')
        parts = basename.split('-')
        if len(parts) == 3:
            app, protocol, env = parts
        else:
            print(f"Skipping {basename}: Unrecognized format.")
            continue
            
        try:
            avg_sci, instance_metrics_df = calculate_sci(file_path)
            print(f"Processed {basename} -> Avg SCI: {avg_sci:.6f}")
            
            # Create Point
            point = Point("sci_metrics") \
                .tag("app", app) \
                .tag("protocol", protocol) \
                .tag("environment", env) \
                .tag("protocol_env", f"{protocol}-{env}") \
                .field("avg_sci", float(avg_sci))
            points.append(point)
            
            # Create Instance Points
            for _, row in instance_metrics_df.iterrows():
                instance_name = str(row['Instance'])
                energy_consumed = float(row['Total_Instance_Emissions'])
                e_dc = float(row['E_DC'])
                e_eu = float(row['E_EU'])
                e_net = float(row['E_NET'])
                # Publish the metrics per instance
                inst_point = Point("instance_metrics") \
                    .tag("app", app) \
                    .tag("protocol", protocol) \
                    .tag("environment", env) \
                    .tag("instance", instance_name) \
                    .field("Energy consumed", energy_consumed) \
                    .field("E_DC", e_dc) \
                    .field("E_EU", e_eu) \
                    .field("E_NET", e_net) \
                    .field("Average SCI", energy_consumed/1000) 
                points.append(inst_point)
        except Exception as e:
            print(f"Error processing {basename}: {e}")

    if points:
        try:
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)
            print(f"Successfully wrote {len(points)} records to InfluxDB.")
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")
    else:
        print("No valid data to write.")

    client.close()

if __name__ == "__main__":
    main()