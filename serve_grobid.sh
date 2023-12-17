#!/bin/bash
# Recommended way to run Grobid is to have docker installed. See details here: https://grobid.readthedocs.io/en/latest/Grobid-docker/

if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker before running Grobid."
    exit 1
fi


machine_arch=$(uname -m)

if [ "$machine_arch" == "armv7l" ] || [ "$machine_arch" == "aarch64" ]; then
    docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.7.3-arm
else
    docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.7.3
fi
