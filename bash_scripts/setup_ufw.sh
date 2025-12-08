#!/bin/bash

# UFW Auto-Configuration Script
# Usage: sudo ./setup_ufw.sh

set -e

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

HOSTNAME=$(hostname)
echo "================================================"
echo "UFW AUTO-SETUP FOR: $HOSTNAME"
echo "================================================"
echo ""

# Install UFW if not present
if ! command -v ufw &> /dev/null; then
    echo "📦 Installing UFW..."
    apt update
    apt install ufw -y
fi

# Disable UFW temporarily to configure safely
echo "⚙️  Configuring UFW..."
ufw --force disable

# Set defaults
ufw default deny incoming
ufw default allow outgoing

echo ""
echo "🔍 Detected Services & Adding Rules:"
echo ""

# Always allow SSH (critical!)
SSH_PORT=$(grep "^Port" /etc/ssh/sshd_config 2>/dev/null | awk '{print $2}' || echo "22")
echo "  ✅ SSH on port $SSH_PORT"
ufw allow $SSH_PORT/tcp comment 'SSH'

# Detect and allow Prometheus Node Exporter
if systemctl is-active --quiet prometheus-node-exporter 2>/dev/null || pgrep node_exporter &>/dev/null; then
    echo "  ✅ Prometheus Node Exporter (9100)"
    # Get monitoring server IP from environment or use common subnets
    MONITOR_IP="${PROMETHEUS_SERVER:-192.168.0.0/24}"
    ufw allow from $MONITOR_IP to any port 9100 proto tcp comment 'Prometheus Node Exporter'
fi

# Detect and allow MySQL/MariaDB
if systemctl is-active --quiet mysql 2>/dev/null || systemctl is-active --quiet mariadb 2>/dev/null; then
    echo "  ✅ MySQL/MariaDB (3306)"
    # Allow from local network only
    ufw allow from 192.168.0.0/16 to any port 3306 proto tcp comment 'MySQL'
    ufw allow from 10.0.0.0/8 to any port 3306 proto tcp comment 'MySQL'
fi

# Detect and allow PostgreSQL
if systemctl is-active --quiet postgresql 2>/dev/null; then
    echo "  ✅ PostgreSQL (5432)"
    ufw allow from 192.168.0.0/16 to any port 5432 proto tcp comment 'PostgreSQL'
    ufw allow from 10.0.0.0/8 to any port 5432 proto tcp comment 'PostgreSQL'
fi

# Detect and allow Samba
if systemctl is-active --quiet smbd 2>/dev/null; then
    echo "  ✅ Samba (139, 445)"
    ufw allow from 192.168.0.0/16 to any port 139,445 proto tcp comment 'Samba'
    ufw allow from 10.0.0.0/8 to any port 139,445 proto tcp comment 'Samba'
    ufw allow from 192.168.0.0/16 to any port 137,138 proto udp comment 'Samba NetBIOS'
    ufw allow from 10.0.0.0/8 to any port 137,138 proto udp comment 'Samba NetBIOS'
fi

# Detect and allow Jenkins
if systemctl is-active --quiet jenkins 2>/dev/null; then
    JENKINS_PORT=$(grep "HTTP_PORT=" /etc/default/jenkins 2>/dev/null | cut -d= -f2 || echo "8080")
    echo "  ✅ Jenkins ($JENKINS_PORT)"
    ufw allow from 192.168.0.0/16 to any port $JENKINS_PORT proto tcp comment 'Jenkins'
    ufw allow from 10.0.0.0/8 to any port $JENKINS_PORT proto tcp comment 'Jenkins'
fi

# Detect and allow Prometheus Server
if systemctl is-active --quiet prometheus 2>/dev/null; then
    echo "  ✅ Prometheus (9090)"
    ufw allow from 192.168.0.0/16 to any port 9090 proto tcp comment 'Prometheus'
    ufw allow from 10.0.0.0/8 to any port 9090 proto tcp comment 'Prometheus'
fi

# Detect and allow Grafana
if systemctl is-active --quiet grafana-server 2>/dev/null; then
    echo "  ✅ Grafana (3000)"
    ufw allow from 192.168.0.0/16 to any port 3000 proto tcp comment 'Grafana'
    ufw allow from 10.0.0.0/8 to any port 3000 proto tcp comment 'Grafana'
fi

# Detect and allow Nginx/Apache
if systemctl is-active --quiet nginx 2>/dev/null || systemctl is-active --quiet apache2 2>/dev/null; then
    echo "  ✅ Web Server (80, 443)"
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
fi

# Detect and allow Docker
if systemctl is-active --quiet docker 2>/dev/null; then
    echo "  ⚠️  Docker detected - allowing docker0 interface"
    ufw allow in on docker0
fi

# Allow Tailscale
if command -v tailscale &> /dev/null; then
    echo "  ✅ Tailscale detected"
    ufw allow in on tailscale0
fi

echo ""
echo "🚫 Blocking Known Attackers:"
ufw deny from 45.159.97.0/24 comment 'NetActuate Madrid attackers'
ufw deny from 45.159.98.0/24 comment 'NetActuate Poland attackers'
ufw deny from 5.161.218.0/24 comment 'Hetzner suspicious'
echo "  ✅ Blocked attacking networks"

echo ""
echo "⚡ Enabling UFW..."
ufw --force enable

echo ""
echo "================================================"
echo "✅ UFW CONFIGURATION COMPLETE"
echo "================================================"
echo ""
ufw status verbose

echo ""
echo "📊 Summary of Open Ports:"
ufw status numbered | grep ALLOW | awk '{print "  " $0}'

echo ""
echo "⚠️  IMPORTANT: If you can't connect, disable UFW with:"
echo "     sudo ufw disable"
echo ""
