#!/bin/bash

#s3cmd put --recursive ../exports/* "s3://altium-backup/hall-electronic/exports/$(git rev-parse --short HEAD)/"
gsutil -m cp -r ../exports/ "gs://altium-backup/hall-electronic/exports/$(git rev-parse --short HEAD)"

echo "Exported on Google cloud storage with hash $(git rev-parse --short HEAD)"
