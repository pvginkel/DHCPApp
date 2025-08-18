mkdir -p $(pwd)/tmp

NAME=dhcp-app
ARGS="
    -e DHCP_LEASE_FILE_PATH=/data/dnsmasq.leases
    -e DHCP_CONFIG_FOLDER_PATH=/data/dnsmasq-static-generated.d
    -v $(pwd)/data:/data
    -p 5000:5000
"
