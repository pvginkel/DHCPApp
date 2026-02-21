#!/usr/bin/env bash

while true; do
    $SSE_GATEWAY_ROOT/scripts/run-gateway.sh --callback-url http://localhost:3301/api/sse/callback --port 3302

    echo
    echo "Press any key to restart the server..."
    echo

    read -n1 -s
done
