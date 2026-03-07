import pandas as pd
import numpy as np
import os
import glob
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "demo_token_please_change")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "demo_org")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "demo_bucket")
METRICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Final Metrics")

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

def calculate_sci(file_path):
    df = pd.read_excel(file_path)
    # --- 1. INTERVAL CALCULATIONS ---
    df['p_active'] = calculate_pactive(df['CPU_Utilization'])
    df['E_CPU'] = (0.00121 + df['p_active']) * (5/60)
    df['E_NET'] = ((df['Nw_In'] + df['Nw_Out']) / (1024**3)) * 0.0065 * df['GEF_Mumbai']
    df['E_EU'] = (45 * (5/60)) * df['GEF_Bengaluru']
    df['E_DC'] = 0.792 + (df['E_CPU'] * 1.15 * df['GEF_Mumbai'])
    df['Interval_Emissions'] = df['E_NET'] + df['E_DC'] + df['E_EU']

    # --- 2. INSTANCE & ITERATION SUMMARIES ---
    instance_summary = df.groupby(['Iteration', 'Instance'])['Interval_Emissions'].sum().reset_index()
    instance_summary.rename(columns={'Interval_Emissions': 'Total_Instance_Emissions'}, inplace=True)

    iteration_summary = instance_summary.groupby('Iteration')['Total_Instance_Emissions'].sum().reset_index()
    iteration_summary.rename(columns={'Total_Instance_Emissions': 'Total_Iteration_Emissions'}, inplace=True)
    iteration_summary['Iteration_SCI'] = iteration_summary['Total_Iteration_Emissions'] / 1000

    # Calculate Average SCI
    return iteration_summary['Iteration_SCI'].mean()

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
            avg_sci = calculate_sci(file_path)
            print(f"Processed {basename} -> Avg SCI: {avg_sci:.6f}")
            
            # Create Point
            point = Point("sci_metrics") \
                .tag("app", app) \
                .tag("protocol", protocol) \
                .tag("environment", env) \
                .tag("protocol_env", f"{protocol}-{env}") \
                .field("avg_sci", float(avg_sci))
            points.append(point)
        except Exception as e:
            print(f"Error processing {basename}: {e}")

    if points:
        try:
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)
            print(f"✅ Successfully wrote {len(points)} records to InfluxDB.")
        except Exception as e:
            print(f"❌ Error writing to InfluxDB: {e}")
    else:
        print("No valid data to write.")

    client.close()

if __name__ == "__main__":
    main()
