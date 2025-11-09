import pandas as pd
import io
import re


def parse_df_output(filename):
    """Parses concatenated df -h output, handling headers and host tags."""
    data = []
    current_hostname = "N/A"
    current_date = "N/A"

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith('--- Host:'):
                parts = line.split(':')
                
                if len(parts) > 1:
                    current_hostname = parts[1].strip().split()[0]
                continue

            if line.startswith('--- Date:'):
                parts = line.split(':')
                
                if len(parts) > 1:
                    current_date = parts[1].strip().split()[0]
                continue

            if line.startswith('--- UUID'):
                parts = line.split(':')
                
                if len(parts) > 1:
                    vm_uuid = parts[1].strip().split()[0]
                continue

            if line.startswith('Filesystem'):
                continue

            fields = line.split()

            if len(fields) >=6:
                data.append({
                    'UUID' : vm_uuid,
                    'Hostname' : current_hostname,
                    'Date' : current_date,
                    'Filesystem' : fields[0],
                    'Size' : fields[1],
                    'Used' : fields[2],
                    'Avail' : fields[3],
                    'Use%' : fields[4],
                    'Mounted on' : fields[5],
                })

    return pd.DataFrame(data)

log_path = '../system_reports/system_health.log'
df = parse_df_output(log_path)

if not df.empty:
    file_date = df['Date'].iloc[0]
else:
    file_date = "NO-Date"

output_filename = f"disk_storage_output_{file_date}.txt"

with open(output_filename, "w") as file:
    file.write(df.to_string())