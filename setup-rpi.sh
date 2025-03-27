#!/bin/bash

sudo apt update && sudo apt install -y \
    docker.io \
    batctl \
    iproute2 \
    iw \
    wireless-tools \
    net-tools

sudo modprobe batman-adv
echo batman-adv | sudo tee -a /etc/modules
