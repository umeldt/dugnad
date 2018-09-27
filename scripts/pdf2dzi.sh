#!/bin/bash
# pdf2dzi.sh <pdf file> <dzi directory>

usage() {
  echo "$0 <pdf file> <dzi directory>"
}

[ -z $2 ] && usage && exit

pages=$(qpdf --show-npages $1)
let pages-=1

[[ ! "$pages" =~ ^[0-9]+$ ]] && exit 1

for page in $(seq 0 $pages); do
  echo "generating dzi for page $page"
  vips pdfload --page $page --dpi 240 $1 $2/$page.tif
  vips dzsave $2/$page.tif $2/$page.dzi
  rm -f $2/$page.tif
done

