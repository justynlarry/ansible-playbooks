import pandas as pd
import parse_storage_report
import parse_logs


def parse_output(filename):
    """Splits a combined system report into storage and service sections."""
    mode = None
    storage_sections = []
    service_sections = []
    critical_sections = []
    ssh_sections = []
    pending_sections = []
    section_lines = []

    current_hostname = current_date = vm_uuid = "N/A"

    def flush_section():
        """Save the current section based on mode."""
        nonlocal section_lines, mode
        if not section_lines:
            return
        if mode == 'df':
            storage_sections.append((section_lines, current_hostname, current_date, vm_uuid))
        elif mode == 'services':
            service_sections.append((section_lines, current_hostname, current_date, vm_uuid))
        elif mode == 'critical':
            critical_sections.append((section_lines, current_hostname, current_date, vm_uuid))
        elif mode == 'ssh':
            ssh_sections.append((section_lines, current_hostname, current_date, vm_uuid))
        elif mode == 'pending':
            pending_sections.append((section_lines, current_hostname, current_date, vm_uuid))
        section_lines=[]

        


    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # --- Metadata lines ---
            if line.startswith('--- Host:'):
                flush_section()
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
                flush_section()
                mode = 'df'
                continue

            elif line.startswith('--- FAILED SERVICES'):
                flush_section()
                mode = 'services'
                continue

            elif line.startswith('--- CRITICAL LOGS'):
                flush_section()
                mode = 'critical'
                continue

            elif line.startswith('--- PENDING UPDATES'):
                flush_section()
                mode = 'pending'
                continue

            elif line.startswith('--- RECENT FAILED SSH'):
                flush_section()
                mode = 'ssh'
                continue

            # --- Add content to current section ---
            section_lines.append(line)
        
        flush_section()

    # --- Send sections to sub-parsers ---
    storage_frames = [
        parse_storage_report.parse(lines, host, date, uuid)
        for lines, host, date, uuid in storage_sections
    ]

    service_frames = [
        parse_logs.parse(lines, host, date, uuid)
        for lines, host, date, uuid in service_sections
    ]

    critical_frames = [
        parse_logs.parse(lines, host, date, uuid)
        for lines, host, date, uuid in critical_sections
    ]

    ssh_frames = [
        parse_logs.parse(lines, host, date, uuid)
        for lines, host, date, uuid in ssh_sections
    ]

    pending_frames = [
        parse_logs.parse(lines, host, date, uuid)
        for lines, host, date, uuid in pending_sections
    ]

    df_storage  = pd.concat(storage_frames, ignore_index=True) if storage_frames else pd.DataFrame()
    df_services = pd.concat(service_frames, ignore_index=True) if service_frames else pd.DataFrame()
    df_critical = pd.concat(critical_frames, ignore_index=True) if critical_frames else pd.DataFrame()
    df_ssh      = pd.concat(ssh_frames, ignore_index=True) if ssh_frames else pd.DataFrame() 
    df_pending  = pd.concat(pending_frames, ignore_index=True) if pending_frames else pd.DataFrame()

    return df_storage, df_services, df_critical, df_ssh, df_pending


# -------------------------------
# Run parser and save outputs
# -------------------------------
log_path = "../system_reports/system_health.log"
df_storage, df_services, df_critical, df_ssh, df_pending = parse_output(log_path)

file_date = "NO-Date"
if not df_storage.empty:
    file_date = df_storage["Date"].iloc[0]
elif not df_services.empty:
    file_date = df_services["Date"].iloc[0]
elif not df_critical.empty:
    file_date = df_critical["Date"].iloc[0]
elif not df_ssh.empty:
    file_date = df_ssh["Date"].iloc[0]
elif not df_pending.empty:
    file_date = df_pending["Date"].iloc[0]


output_storage = f"disk_storage_output_{file_date}.txt"
output_services = f"services_output_{file_date}.txt"
output_critical = f"critical_output_{file_date}.txt"
output_ssh = f"ssh_output_{file_date}.txt"
output_pending = f"pending_output_{file_date}.txt"

if not df_storage.empty:
    df_storage.to_csv(output_storage, sep="\t", index=False)
if not df_services.empty:
    df_services.to_csv(output_services, sep="\t", index=False)
if not df_critical.empty:
    df_critical.to_csv(output_critical, sep="\t", index=False)
if not df_ssh.empty:
    df_ssh.to_csv(output_ssh, sep="\t", index=False)
if not df_pending.empty:
    df_pending.to_csv(output_pending, sep="\t", index=False)

print(f"Storage report -- {output_storage}")
print(f"Services report -- {output_services}")
print(f"Critical Logs report -- {output_critical}")
print(f"SSH Logs report -- {output_ssh}")
print(f"Pending Updates Logs report -- {output_pending}")