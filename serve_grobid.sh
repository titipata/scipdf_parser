#!/bin/bash
# assumes you have docker and nvidia-container-toolkit installed
# see https://aur.archlinux.org/packages/nvidia-container-toolkit
# After installing, you need to restart docker
# sudo systemctl restart docker

docker run -t --rm --gpus all -p 8070:8070 grobid/grobid:0.7.3
