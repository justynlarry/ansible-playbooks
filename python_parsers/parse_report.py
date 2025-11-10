import pandas as pd
import parse_storage_report
import parse_services_report


def parse_output(filename):
    """Splits a combined system report into storage and service sections."""
    mode = None
    storage_sections = []
    service_sections = []
    section_lines = []

    current_hostname = current_date = vm_uuid = "N/A"

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # --- Metadata lines ---
            if line.startswith('--- Host:'):
                current_hostname = line.split(':', 1)[1].strip().split()[0]
                continue
            if line.startswith('--- Date:'):
                current_date = line.split(':', 1)[1].strip().split()[0]
                continue
            if line.startswith('--- UUID'):
                vm_uuid = line.split(':', 1)[1].strip().split()[0]
                continue

            # --- Section control ---
            if line.startswith('Filesystem'):
                # finished collecting services section
                if section_lines and mode == 'services':
                    service_sections.append((section_lines, current_hostname, current_date, vm_uuid))
                section_lines = []
                mode = 'df'
                continue

            elif line.startswith('--- FAILED SERVICES'):
                # finished collecting df section
                if section_lines and mode == 'df':
                    storage_sections.append((section_lines, current_hostname, current_date, vm_uuid))
                section_lines = []
                mode = 'services'
                continue

            # --- Add content to current section ---
            section_lines.append(line)

        # Handle last section after file ends
        if section_lines:
            if mode == 'df':
                storage_sections.append((section_lines, current_hostname, current_date, vm_uuid))
            elif mode == 'services':
                service_sections.append((section_lines, current_hostname, current_date, vm_uuid))

    # --- Send sections to sub-parsers ---
    storage_frames = [
        parse_storage_report.parse(lines, host, date, uuid)
        for lines, host, date, uuid in storage_sections
    ]
    service_frames = [
        parse_services_report.parse(lines, host, date, uuid)
        for lines, host, date, uuid in service_sections
    ]

    df_storage = pd.concat(storage_frames, ignore_index=True) if storage_frames else pd.DataFrame()
    df_services = pd.concat(service_frames, ignore_index=True) if service_frames else pd.DataFrame()

    return df_storage, df_services


# -------------------------------
# Run parser and save outputs
# -------------------------------
log_path = "../system_reports/system_health.log"
df_storage, df_services = parse_output(log_path)

file_date = "NO-Date"
if not df_storage.empty:
    file_date = df_storage["Date"].iloc[0]
elif not df_services.empty:
    file_date = df_services["Date"].iloc[0]

output_storage = f"disk_storage_output_{file_date}.txt"
output_services = f"services_output_{file_date}.txt"

if not df_storage.empty:
    df_storage.to_csv(output_storage, sep="\t", index=False)
if not df_services.empty:
    df_services.to_csv(output_services, sep="\t", index=False)

print(f"Storage report → {output_storage}")
print(f"Services report → {output_services}")
