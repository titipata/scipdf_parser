#!/bin/bash

# Recommended way to run Grobid is Docker, https://grobid.readthedocs.io/en/latest/Grobid-docker/

docker run --rm --gpus all --init --ulimit core=0 -p 8080:8070 grobid/grobid:0.7.3
