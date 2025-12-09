#!/bin/bash

grep 'ansible_host=' /home/blue-user/ansible-playbooks/inventories/production.ini | awk -F'ansible_host=' '{print $2}' | awk '{print $1}' | grep -E '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$' > /home/blue-user/ansible-playbooks/inventories/prod_hosts_to_exclude.txt
