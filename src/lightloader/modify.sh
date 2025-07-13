#!/bin/bash


# Calculate the absolute path of the script directory
LIGHTLOADER_DIR=$(cd "$(dirname "$0")" && pwd)

# Check if there are input parameters
if [ $# -ne 1 ]; then
    echo "Usage: $0 <destination_path>"
    exit 1
fi

# Input path
destination=$1

# Check if destination path exists
if [ ! -d "$destination" ]; then
    echo "Destination path does not exist."
    exit 1
fi

# Copy files
cp -r "$LIGHTLOADER_DIR" "$destination/template/python3-debian"
# mv "$destination/template/python3-debian/master_light4faas_pycg"  "$destination/template/python3-debian/light4faas"

# Modify Dockerfile
dockerfilePath="$destination/template/python3-debian/Dockerfile"
if [ -f "$dockerfilePath" ]; then
    # Check if there are enough lines
    if [ $(wc -l < "$dockerfilePath") -lt 53 ]; then
        echo "Dockerfile does not have enough lines."
        exit 1
    fi
    
# insert content
sed -i '53i\
# copy LightLoader----------------------\
COPY LightLoader         LightLoader\
RUN cp ./function/handler.py ./python && \\\
    cd /home/app/LightLoader && \\\
    python ./Light.py && \\\
    cd /home/app/\
#-----------------------------------' "$dockerfilePath"


# insert ahead line 31
# keep ustc pip mirror if needed
sed -i '31i\
RUN pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple\
RUN pip install astroid==3.1.0 astor numpy openai --target=/home/ast' "$dockerfilePath"

sed -i '29a\
ENV PYTHONPATH=$PYTHONPATH:/home/ast' "$dockerfilePath"

sed -i '26a\
RUN mkdir -p /home/ast && chown -R app /home/ast' "$dockerfilePath"

sed -i '23a\
COPY function/call_graph.json .' "$dockerfilePath" 

sed -i '3s|.*|FROM --platform=${TARGETPLATFORM:-linux/amd64} localhost:5000/python:${PYTHON_VERSION}|' "$dockerfilePath"
 # only for local registry
sed -i '1s/ARG PYTHON_VERSION=.*/ARG PYTHON_VERSION=3.10.5/' "$dockerfilePath"
# only for local registry
else
    echo "Dockerfile not found."
    exit 1
fi
echo "Script completed successfully."
