import pandas as pd

def parse(lines, hostname, date, uuid):
    """Parse FAILED SERVICES section lines."""
    data = []
    for line in lines:
        if not line.startswith("---") and not line.startswith("0 loaded units"):
            data.append({
                "UUID": uuid,
                "Hostname": hostname,
                "Date": date,
                "Service": line
            })
    return pd.DataFrame(data)
