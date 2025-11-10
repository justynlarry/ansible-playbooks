import pandas as pd
import io
import re
"""Import Modules"""
import parse_storage_report
import parse_services_report 

def parse_output(filename):
    """Parses concatenated df -h output, handling headers and host tags."""
    data = []
    current_hostname = "N/A"
    current_date = "N/A"

    """Set mode to help parser delineate between report segments"""
    mode = None

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
                mode = 'df'
                parse_storage_report()
            elif line.startswith('--- FAILED SERVICES ---'):
                mode = 'services'
                parse_services_report()

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