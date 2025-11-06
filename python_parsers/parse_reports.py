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

            if line.startswith('Filesystem'):
                continue

            fields = line.split()

            if len(fields) >=6:
                data.append({
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
df = parse_df_output('system_health_2025-11-06.log')

with open("output.txt", "w") as file:
    file.write(df.to_string())