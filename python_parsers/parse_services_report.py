import pandas as pd

def parse(filename):
    """Parses FAILED SERVICES log into a DataFrame."""
    data = []
    hostname = date = uuid = "N/A"

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith('--- Host:'):
                hostname = line.split(':')[1].strip().split()[0]
                continue
            if line.startswith('--- Date:'):
                date = line.split(':')[1].strip().split()[0]
                continue
            if line.startswith('--- UUID'):
                uuid = line.split(':')[1].strip().split()[0]
                continue

            # Only record non-header service lines
            if not line.startswith('---') and not line.startswith('0 loaded units'):
                data.append({
                    'UUID': uuid,
                    'Hostname': hostname,
                    'Date': date,
                    'Service': line
                })

    return pd.DataFrame(data)
