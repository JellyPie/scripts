#!/bin/sh

# Downloads today's image from Bing's image archive.

# You can tweak $nc and $idx to download other images.
# $nc = the date, in Unix-ish timestamp which includes milliseconds
# $idx = offset from the date

nc="$(date +%s%3N)"
idx=1

str="https://www.bing.com/HPImageArchive.aspx?format=js&idx=$idx&n=1&nc=$nc&pid=hp"
resp="$(curl -s "$str")"

img="$(echo "$resp" | grep -Po '(?<="url":").*?[^\\](?=")')"
url="https://www.bing.com/$img"

ext="$(echo "$img" | grep -Po '(\.[^\.]+)$')"
filename="$(date -I)$ext"
curl "$url" > "$filename"

