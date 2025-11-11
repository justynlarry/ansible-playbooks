import pandas as pd

def parse(lines, hostname, date, uuid):
    data = []
    for line in lines:
        if not line.startswith("---") and not line.startswith("0 loaded units"):
            data.append({
                "UUID": uuid,
                "Hostname": hostname,
                "Date": date,
                "Critical Log": line
            })
    return pd.DataFrame(data)