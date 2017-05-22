#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DIR+="/../exports/combined/"
FILENAME="component_count_report"
cd $DIR
pandoc $FILENAME.md --self-contained -o $FILENAME.html 
