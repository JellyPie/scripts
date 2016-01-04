#!/bin/bash

for i in *.flac ; do
	ffmpeg -i "$i" "$(basename "${i/.flac}").wav"
done
