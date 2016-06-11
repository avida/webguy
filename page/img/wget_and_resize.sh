#!/bin/bash
wget $1 -O $2
convert $2 -resize 64x64 $2
