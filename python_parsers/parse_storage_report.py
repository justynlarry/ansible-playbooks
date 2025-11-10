import pandas as pd

def parse(filename):
    """Parses df -h log into a DataFrame."""
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

            fields = line.split()
            if len(fields) >= 6 and not line.startswith('Filesystem'):
                data.append({
                    'UUID': uuid,
                    'Hostname': hostname,
                    'Date': date,
                    'Filesystem': fields[0],
                    'Size': fields[1],
                    'Used': fields[2],
                    'Avail': fields[3],
                    'Use%': fields[4],
                    'Mounted on': fields[5],
                })

    return pd.DataFrame(data)
