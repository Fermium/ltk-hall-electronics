#!/bin/bash

#s3cmd put --recursive ../* "s3://altium-backup/hall-electronic/whole/$(git rev-parse --short HEAD)/"
HASH=$(git rev-parse --short HEAD)
TARGZ_NAME="/tmp/$HASH.tar.gz"
mkdir "/tmp/$HASH"
tar -zcvf "$TARGZ_NAME" ../
#gsutil -m cp  "$TARGZ_NAME" "gs://altium-backup/hall-electronic/whole/"
s3cmd put "$TARGZ_NAME" "s3://altium-backup/hall-electronic/whole/"
rm "$TARGZ_NAME"
