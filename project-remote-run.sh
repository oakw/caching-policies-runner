#!/usr/bin/bash
# This script is meant to be run on a remote machine where policies are to be tested
#
# Relevant configuration params used on Google Cloud Compute Engine:
# properties.machineType: n4-custom-32-65536 [N4, 32 vCPU, 48GB memory]
# properties.scheduling.provisioningModel: SPOT
# properties.disks.initializeParams.diskType: hyperdisk-balanced
# properties.disks.initializeParams.diskSizeGb: 10
# properties.disks.initializeParams.provisionedIops: 3060
# properties.disks.initializeParams.provisionedThroughput: 155
# properties.metadata.items[0].key: startup-script
# properties.metadata.items[0].value: [this script]


COMPRESSED_PROJECT_URL=""
API_HOST=""

apt update
apt install -y wget unzip python3 python3-pip python3-venv time

wget $COMPRESSED_PROJECT_URL -O project.tar.gz
mkdir project
tar -xzf project.tar.gz -C project

cd project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python report/remote_runner/run.py --api-host="$API_HOST"

shutdown -h now
