import pandas as pd
import parse_storage_report
import parse_services_report

storage_log_path = '../system_reports/df_report.log'
services_log_path = '../system_reports/services_report.log'

df = parse_storage_report.parse(storage_log_path)
svc = parse_services_report.parse(services_log_path)

file_date = "NO-Date"
if not df.empty:
    file_date = df['Date'].iloc[0]
elif not svc.empty:
    file_date = svc['Date'].iloc[0]

output_storage = f"disk_storage_output_{file_date}.txt"
output_services = f"services_output_{file_date}.txt"

if not df.empty:
    df.to_csv(output_storage, sep='\t', index=False)
if not svc.empty:
    svc.to_csv(output_services, sep='\t', index=False)

print(f"Storage report written to: {output_storage}")
print(f"Services report written to: {output_services}")