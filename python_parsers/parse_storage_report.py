import pandas as pd

def parse(lines, hostname, date, uuid):
    """Parse df -h section lines."""
    data = []
    for line in lines:
        fields = line.split()
        if len(fields) >= 6 and not line.startswith("Filesystem"):
            data.append({
                "UUID": uuid,
                "Hostname": hostname,
                "Date": date,
                "Filesystem": fields[0],
                "Size": fields[1],
                "Used": fields[2],
                "Avail": fields[3],
                "Use%": fields[4],
                "Mounted on": fields[5],
            })
    return pd.DataFrame(data)
