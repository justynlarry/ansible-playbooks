import pandas as pd
import io
import re

def parse_svc_output(filename):
    """Parses concatenated 'systemctl --failed || true' output"""
    data = []
    current_hostname = "N/A"
    current_date = "N/A"

    """Set 'section' flags to help parser delineate between report segments"""
    in_df_section = False
    in_service_section = False

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith('--- Host'):
                parts = line.split(':')

                if len(parts) > 1:
                    current_hostname = parts[1].strip().split()[0]
                continue

            if line.startswith('--- Date'):
                parts = line.split(':')

                if len(parts) > 1:
                    current_date = 