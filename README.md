# Ansible Playbooks for Server Management

This repository contains Ansible playbooks and configuration files used to manage, bootstrap, and maintain servers in a small lab/home environment. The playbooks automate tasks such as creating management users, setting up SSH keys, performing system updates, and collecting system logs for monitoring.

---

## Repository Structure
```
.
├── ansible.cfg # Ansible configuration file
├── bootstrap.yml # Playbook to bootstrap ansible management user
├── daily_tasks.yml # Playbook for daily maintenance and log collection
├── site.yml # (Optional) Main playbook to include all tasks
├── controlled_reboot.yml # Playbook for Rolling System-wide Reboot
├── db_setup.yml # Install MySQL Server on Debian
├── docker_debian_setup.yml # Install Docker on Debian
├── update_upgrade.yml # Playbook for updates and upgrades
├── inventories # Inventory files for hosts
│ ├── bootstrap.ini # Inventory for bootstrapping new hosts
│ └── production.ini # Inventory for production servers
├── host_vars # Host-specific variables, encrypted with Ansible Vault
│ └── <host_ip>/vault.yml
├── files # Supporting files
│ ├── ansible_management_user.pub # Public SSH key for Ansible user
│ ├── default_site.html # Sample default web page
│ └── sudoer_ansbl-user # Sudoers configuration for Ansible user
```

---

## Requirements

- Ansible 2.9+  
- Python 3 on the control node and target hosts  
- SSH access to all managed hosts  
- Optional: Ansible Vault for encrypted host variables

---

## Configuration

### ansible.cfg

The configuration file specifies default inventory location and SSH private key:

```ini
[defaults]
inventory = inventory
private_key_file = ~/.ssh/ansible
```

# Inventories
- bootstrap.ini – Inventory for initial bootstrapping of servers, with per-host users defined.
- production.ini – Inventory for ongoing management, using the centralized ansbl-user.

# Files
- 50-cloud-init.j2 - Netplan configuration file for Ubuntu Server to switch from DHCP to static IP Address.
- interfaces.js - Interfaces configuration file for Debian Server to switch from DHCP to Static IP Address


# Playbooks
1. Bootstrap Ansible User (bootstrap.yml)
This playbook sets up the Ansible management user (ansbl-user) on all hosts:
- Installs system updates (Ubuntu/Debian)
- Creates ansbl-user
- Adds SSH public key for secure access
- Adds sudoers file for passwordless sudo
- Sets Static IP Address for Ubuntu & Debian
- Installs sudo, python3, curl, htop, wget, git, net-tools

Run example:

```bash
ansible-playbook -i inventories/bootstrap.ini bootstrap.yml --ask-become-pass
```

2. Daily Maintenance (daily_tasks.yml)
Automates daily server maintenance:
- Installs system updates
- Collects logs via journalctl -p 3 -xb for errors
- Stores problematic logs on the Ansible control node for review
- Checks for /var/run/reboot-required file to see if reboot is necessary."


Run example:
```bash
ansible-playbook -i inventories/production.ini daily_tasks.yml --ask-become-pass
```
Logs will be saved to ```/tmp/problem_logs_report_<DATE>.txt``` on the control node.

3. Update & Upgrade (update_upgrade.yml)
Performs system-wide updates and upgrades on all managed hosts. Typically run as part of maintenance or pre-deployment steps.

Host Variables (host_vars/)
Each host has a dedicated folder containing encrypted variables using Ansible Vault:

```bash
host_vars/<host_ip>/vault.yml
```
Contains sensitive information like SSH passwords or API tokens.

Usage
Clone the repository:

```bash
git clone <repository_url>
cd ansible-playbooks
```
Bootstrap new hosts:

```bash
ansible-playbook -i inventories/bootstrap.ini bootstrap.yml --ask-become-pass
```
Run daily maintenance:
```bash
ansible-playbook -i inventories/production.ini daily_tasks.yml --ask-become-pass
```

Perform updates/upgrades:

```bash
ansible-playbook -i inventories/production.ini update_upgrade.yml --ask-become-pass
```
# Security
- All sensitive host variables are encrypted with Ansible Vault.
- SSH keys are used for authentication instead of passwords wherever possible.
- Sudoers for ansbl-user are configured with minimal privileges required.

Contributing
Feel free to submit pull requests or open issues for:
- Bug fixes
- Additional playbooks or roles
- Inventory enhancements or documentation improvements

License
This project is licensed under the MIT License.
