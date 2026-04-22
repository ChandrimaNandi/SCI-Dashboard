"""
InfluxDB Data Viewer with Export to JSON and TXT
Display all data stored in InfluxDB and export to JSON/TXT files
"""

from influxdb_client import InfluxDBClient
import os
import pandas as pd
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "demo_token_please_change")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "demo_org")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "demo_bucket")

def main():
    print("\n" + "#"*120)
    print("# INFLUXDB DATA VIEWER")
    print("#"*120)
    print(f"\nConnecting to: {INFLUXDB_URL}")
    print(f"Organization: {INFLUXDB_ORG}")
    print(f"Bucket: {INFLUXDB_BUCKET}\n")
    
    # Collect all data
    all_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'url': INFLUXDB_URL,
            'organization': INFLUXDB_ORG,
            'bucket': INFLUXDB_BUCKET
        },
        'sci_metrics': [],
        'instance_metrics': [],
        'statistics': {}
    }
    
    try:
        client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        query_api = client.query_api()
        
        # === SCI METRICS ===
        print("="*120)
        print(" 1. SCI_METRICS - Software Carbon Intensity")
        print("="*120 + "\n")
        
        query = '''
from(bucket: "demo_bucket")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sci_metrics")
  |> keep(columns: ["app", "protocol", "environment", "_field", "_value"])
'''
        
        data = []
        tables = query_api.query(query)
        for table in tables:
            for record in table.records:
                item = {
                    'App': record['app'],
                    'Protocol': record['protocol'],
                    'Environment': record['environment'],
                    'Avg SCI': record.get_value()
                }
                data.append(item)
                all_data['sci_metrics'].append(item)
        
        if data:
            df = pd.DataFrame(data)
            df = df.drop_duplicates()
            df = df.sort_values(['App', 'Protocol', 'Environment'])
            # Format for display
            df_display = df.copy()
            df_display['Avg SCI'] = df_display['Avg SCI'].apply(lambda x: f"{x:.6f}")
            print(df_display.to_string(index=False))
            print(f"\nTotal Records: {len(df)}\n")
        
        # === INSTANCE METRICS ===
        print("\n" + "="*120)
        print(" 2. INSTANCE_METRICS - Energy Breakdown per Instance")
        print("="*120 + "\n")
        
        query = '''
from(bucket: "demo_bucket")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "instance_metrics")
  |> keep(columns: ["app", "protocol", "environment", "instance", "_field", "_value"])
  |> sort(columns: ["app", "protocol", "environment", "instance", "_field"])
'''
        
        data = []
        tables = query_api.query(query)
        for table in tables:
            for record in table.records:
                item = {
                    'app': record['app'],
                    'protocol': record['protocol'],
                    'environment': record['environment'],
                    'instance': record['instance'],
                    'field': record['_field'],
                    'value': record.get_value() if isinstance(record.get_value(), (int, float)) else str(record.get_value())
                }
                data.append(item)
                all_data['instance_metrics'].append(item)
        
        if data:
            df = pd.DataFrame(data)
            df = df.sort_values(['app', 'protocol', 'environment', 'instance', 'field'])
            
            # Print by instance for better readability
            current_key = None
            for idx, row in df.iterrows():
                key = f"{row['app']}-{row['protocol']}-{row['environment']}-{row['instance']}"
                if key != current_key:
                    current_key = key
                    print(f"\n▶ {key}")
                    print("  " + "─"*100)
                value_str = f"{row['value']:.6f}" if isinstance(row['value'], float) else str(row['value'])
                print(f"  {row['field']:20s} → {value_str:>20s}")
            
            print(f"\n\nTotal Records: {len(df)}")
            print(f"Unique combinations: {df.groupby(['app', 'protocol', 'environment', 'instance']).ngroups}")
        
        # === STATISTICS ===
        print("\n" + "="*120)
        print(" 3. SUMMARY STATISTICS")
        print("="*120 + "\n")
        
        query_stats = '''
from(bucket: "demo_bucket")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "sci_metrics")
  |> filter(fn: (r) => r["_field"] == "avg_sci")
  |> keep(columns: ["_value"])
'''
        
        values = []
        tables = query_api.query(query_stats)
        for table in tables:
            for record in table.records:
                values.append(record.get_value())
        
        if values:
            print(f"SCI Statistics:")
            print(f"  Minimum: {min(values):.6f}")
            print(f"  Maximum: {max(values):.6f}")
            print(f"  Average: {sum(values)/len(values):.6f}")
            print(f"  Count: {len(values)}\n")
            
            all_data['statistics']['sci'] = {
                'minimum': min(values),
                'maximum': max(values),
                'average': sum(values)/len(values),
                'count': len(values)
            }
        
        # Get energy consumed stats
        query_energy = '''
from(bucket: "demo_bucket")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "instance_metrics")
  |> filter(fn: (r) => r["_field"] == "Energy consumed")
  |> keep(columns: ["_value"])
'''
        
        energy_values = []
        tables = query_api.query(query_energy)
        for table in tables:
            for record in table.records:
                energy_values.append(record.get_value())
        
        if energy_values:
            print(f"Energy Consumed Statistics:")
            print(f"  Minimum: {min(energy_values):.6f} g CO2")
            print(f"  Maximum: {max(energy_values):.6f} g CO2")
            print(f"  Average: {sum(energy_values)/len(energy_values):.6f} g CO2")
            print(f"  Total: {sum(energy_values):.6f} g CO2")
            print(f"  Count: {len(energy_values)}\n")
            
            all_data['statistics']['energy_consumed'] = {
                'minimum': min(energy_values),
                'maximum': max(energy_values),
                'average': sum(energy_values)/len(energy_values),
                'total': sum(energy_values),
                'count': len(energy_values),
                'unit': 'g CO2'
            }
        
        # === SAVE TO FILES ===
        print("="*120)
        print("💾 SAVING DATA TO FILES")
        print("="*120 + "\n")
        
        # Save to JSON
        json_file = "influxdb_data.json"
        with open(json_file, 'w') as f:
            json.dump(all_data, f, indent=2)
        print(f"✅ JSON exported: {json_file}")
        
        # Save to text file
        txt_file = "influxdb_data.txt"
        with open(txt_file, 'w') as f:
            f.write("#" * 120 + "\n")
            f.write("# INFLUXDB DATA EXPORT\n")
            f.write("#" * 120 + "\n\n")
            f.write(f"Timestamp: {all_data['metadata']['timestamp']}\n")
            f.write(f"URL: {all_data['metadata']['url']}\n")
            f.write(f"Organization: {all_data['metadata']['organization']}\n")
            f.write(f"Bucket: {all_data['metadata']['bucket']}\n\n")
            
            f.write("=" * 120 + "\n")
            f.write(" 1. SCI_METRICS\n")
            f.write("=" * 120 + "\n\n")
            
            if all_data['sci_metrics']:
                sci_df = pd.DataFrame(all_data['sci_metrics']).drop_duplicates()
                f.write(sci_df.to_string(index=False) + "\n\n")
            
            f.write("=" * 120 + "\n")
            f.write(" 2. INSTANCE_METRICS\n")
            f.write("=" * 120 + "\n\n")
            
            if all_data['instance_metrics']:
                inst_df = pd.DataFrame(all_data['instance_metrics'])
                for key, group in inst_df.groupby(['app', 'protocol', 'environment', 'instance']):
                    f.write(f"\n▶ {key[0]}-{key[1]}-{key[2]}-{key[3]}\n")
                    f.write("─" * 100 + "\n")
                    for idx, row in group.iterrows():
                        f.write(f"  {row['field']:20s} → {row['value']}\n")
            
            f.write("\n" + "=" * 120 + "\n")
            f.write(" 3. STATISTICS\n")
            f.write("=" * 120 + "\n\n")
            
            if 'sci' in all_data['statistics']:
                sci_stats = all_data['statistics']['sci']
                f.write(f"SCI Statistics:\n")
                f.write(f"  Minimum: {sci_stats['minimum']:.6f}\n")
                f.write(f"  Maximum: {sci_stats['maximum']:.6f}\n")
                f.write(f"  Average: {sci_stats['average']:.6f}\n")
                f.write(f"  Count: {sci_stats['count']}\n\n")
            
            if 'energy_consumed' in all_data['statistics']:
                energy_stats = all_data['statistics']['energy_consumed']
                f.write(f"Energy Consumed Statistics:\n")
                f.write(f"  Minimum: {energy_stats['minimum']:.6f} {energy_stats['unit']}\n")
                f.write(f"  Maximum: {energy_stats['maximum']:.6f} {energy_stats['unit']}\n")
                f.write(f"  Average: {energy_stats['average']:.6f} {energy_stats['unit']}\n")
                f.write(f"  Total: {energy_stats['total']:.6f} {energy_stats['unit']}\n")
                f.write(f"  Count: {energy_stats['count']}\n")
        
        print(f"✅ Text export: {txt_file}")
        
        print("\n" + "="*120)
        print("✅ Data successfully retrieved and exported!")
        print("="*120 + "\n")
        
        client.close()
        
    except Exception as e:
        print(f"\n Error: {e}\n")
        print("Make sure:")
        print("  1. InfluxDB container is running: docker ps")
        print("  2. Connected to correct URL: http://localhost:8086")
        print("  3. Your .env credentials are correct\n")

if __name__ == "__main__":
    main()
