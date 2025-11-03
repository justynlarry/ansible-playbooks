# Ansible Playbook Library – Server Automation Toolkit

This repository contains a modular collection of Ansible playbooks, roles, and templates used to bootstrap, configure, and maintain Linux servers across a small lab or home environment.
It automates key tasks such as creating management users, applying OS-specific network configurations, performing updates, and managing system logs.

Repository Structure
```
.
├── ansible.cfg                      # Global Ansible configuration
├── bootstrap.yml                    # Bootstrap ansible management user (ansbl-user)
├── controlled_reboot.yml             # Rolling system-wide controlled reboot
├── daily_tasks.yml                  # Daily updates and log collection
├── db_setup.yml                     # MySQL server installation and setup
├── docker_debian_setup.yml          # Docker installation and management user setup (Debian-based)
├── update_upgrade.yml               # System update and upgrade tasks
├── site.yml                         # Aggregator playbook for orchestration
├── files/                           # Supporting configuration and key files
│   ├── 50-cloud-init.j2             # Ubuntu netplan template for static IP
│   ├── ansible_management_user.pub  # SSH key for ansbl-user
│   ├── default_site.html            # Example Apache index file
│   ├── docker_user_key.pub          # SSH key for docker-user
│   ├── ifcfg-eth0.j2                # RHEL/Fedora static IP template
│   ├── interfaces.j2                # Debian /etc/network/interfaces template
│   └── sudoer_ansbl-user            # Passwordless sudo file for ansbl-user
├── host_vars/                       # Encrypted host-specific variables (Ansible Vault)
│   └── <IP>/vault.yml
├── inventories/
│   ├── bootstrap.ini                # Inventory for bootstrapping new hosts
│   └── production.ini               # Inventory for production environments
├── roles/
│   ├── common/                      # Common role: package install, user setup
│   ├── debian/                      # Debian role: static IP configuration
│   ├── ubuntu/                      # Ubuntu role: netplan configuration
│   ├── fedora/                      # Fedora role: nmcli-based static IP config
│   └── templates/                   # Role-specific templates
└── README.md
```

# Requirements

- Ansible 2.14+
- Python 3.x installed on control and target hosts
- SSH access to all managed nodes
- Ansible Vault for securing sensitive host variables (e.g., passwords)

# Inventory Layout
inventories/bootstrap.ini
  - Used during initial provisioning.
  - Defines per-host login users (before ansbl-user is deployed).

inventories/production.ini
  - Used for day-to-day operations.
  - All hosts use the central ansbl-user with SSH key authentication.

# Hosts are grouped as:
- web-servers
- file-servers
- db-servers
- system-monitors
- dev-servers
- test

# Host Variables (host_vars/)

Each host IP folder contains an encrypted vault.yml file with credentials and secrets:
```
host_vars/192.168.0.xxx/vault.yml
```

## Typical variables stored include:
- vault_ansible_ssh_pass
- mysql_root_pass
- db_user, db_pass, db_name

## Encrypt/decrypt with:
```
ansible-vault edit host_vars/<IP>/vault.yml
```

# Playbooks Overview
## 1. Bootstrap Management User
```bootstrap.yml```

## Bootstraps a new server with a management user (ansbl-user):
- Installs essential packages (sudo, python3, curl, git, htop, net-tools, wget)
- Creates ansbl-user with SSH key authentication
- Configures passwordless sudo
- Converts DHCP → Static IP:
- Ubuntu → /etc/netplan/50-cloud-init.yaml
- Debian → /etc/network/interfaces
- Fedora → nmcli via NetworkManager
- Adds current primary user to the sudo group
- Supports per-distro roles (roles/ubuntu, roles/debian, roles/fedora)

Run:
```
ansible-playbook -i inventories/bootstrap.ini bootstrap.yml --vault-password-file ~/.vault_pass.txt
```
## 2. Daily Tasks & Health Checks
```daily_tasks.yml```

- Performs daily maintenance and collects system logs:
- Updates packages (APT/DNF)
- Runs journalctl -p 3 -xb and stores logs locally on control node
- Generates /tmp/final_problem_logs_report_<DATE>.txt
- Detects /var/run/reboot-required flag and alerts

Run:
```
ansible-playbook -i inventories/production.ini daily_tasks.yml
```
## 3. Controlled Reboot
```
controlled_reboot.yml
```
Safely reboots all hosts sequentially (serial: 1) to avoid service interruption.

Run:
```
ansible-playbook -i inventories/production.ini controlled_reboot.yml
```
## 4. MySQL Setup
```
db_setup.yml
```
Automates MySQL installation and configuration:
- Installs mysql-server, mysql-client, dependencies
- Sets root password
- Creates database user & database (using vault vars)
- Enables remote access
- Configures /etc/mysql/mysql.conf.d/mysqld.cnf
- Restarts MySQL via handler

Run:
```
ansible-playbook -i inventories/production.ini db_setup.yml --vault-password-file ~/.vault_pass.txt
```
## 5. Docker Setup (Debian)
```
docker_debian_setup.yml
```
Installs and configures Docker using the modern keyring approach:
- Adds Docker GPG key & repository
- Installs core Docker packages
- Creates a docker-user and adds SSH key (files/docker_user_key.pub)
- Ensures docker service is enabled and running

Run:
```
ansible-playbook -i inventories/production.ini docker_debian_setup.yml
```
## 6. Update & Upgrade
```
update_upgrade.yml
```
Performs system-wide APT updates and upgrades across all Debian/Ubuntu hosts.
Recommended as part of regular maintenance or prior to major deployments.

Run:
```
ansible-playbook -i inventories/production.ini update_upgrade.yml
```
# Roles Breakdown
Role        Purpose
common      Installs base packages, creates ansbl-user, sets up SSH & sudo
debian      Configures /etc/network/interfaces for static IP
ubuntu      Applies netplan config (50-cloud-init.yaml)
fedora      Uses nmcli to convert DHCP → static IP
templates/	Houses distro-specific config templates (.j2 files)


# Security Practices
- All sensitive data (passwords, API keys) stored via Ansible Vault
- Passwordless sudo restricted to required automation tasks
- SSH keys for authentication (no plain passwords)
- Playbooks idempotent — safe for repeated runs

# Example Workflow
## 1️. Bootstrap all new servers
```ansible-playbook -i inventories/bootstrap.ini bootstrap.yml --vault-password-file ~/.vault_pass.txt```

## 2. Run daily maintenance tasks
```ansible-playbook -i inventories/production.ini daily_tasks.yml```

## 3. Apply updates
```ansible-playbook -i inventories/production.ini update_upgrade.yml```

## 4. Reboot safely across cluster
```ansible-playbook -i inventories/production.ini controlled_reboot.yml```

# License
This project is licensed under the MIT License.

# Contributions
- Pull requests and suggestions are welcome — whether for:
- New roles (e.g., Nginx, Prometheus)
- Improved network or log handling
- Better inventory management
- General documentation enhancements
