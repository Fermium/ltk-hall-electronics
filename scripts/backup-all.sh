#!/bin/bash

#s3cmd put --recursive ../* "s3://altium-backup/hall-electronic/whole/$(git rev-parse --short HEAD)/"
gsutil -m cp -r ../* "gs://altium-backup/hall-electronic/whole/$(git rev-parse --short HEAD)/"
