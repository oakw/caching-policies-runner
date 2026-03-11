#!/bin/bash

datetime=$(date +"%Y-%m-%d-%H-%M-%S")
export_dir="caching-policies-runner-$datetime"

tar -czf "$export_dir.tar.gz" \
    policy_runner.py \
    requirements.txt \
    components/ \
    policies/ \
    report/ \
    traffic/models/wiki-t-10/ \
    traffic/models/docker-dal09/ \
    traffic/models/docker-lon02/ \
    traffic/models/letapartika/ \
    traffic/reader.py