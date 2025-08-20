mkdir -p $(pwd)/tmp

NAME=dhcp-app-ui
BUILD_ARGS="
    --build-arg VITE_API_BASE_URL=http://wrkdev:5000/api/v1
"
ARGS="
    -p 8080:80
"
