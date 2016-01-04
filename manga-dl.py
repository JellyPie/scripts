#!/usr/bin/env python3

from urllib.parse import urlparse
from lxml.html import fromstring
import itertools
import requests
import tempfile
import tarfile
import sys
import os
import re


supported_websites = {

    'www.mangahere.co': {
        'nameselector': '.readpage_top > div:nth-child(2) > h1:nth-child(1) > a:nth-child(1)',
        'imageselector': '#image',
        'urlregex': '([0-9]{3}(?=\.jpg))',
        'step': 1,
        'trailingzeros': 3
    },

    'mangafox.me': {
        'nameselector': '.no > a:nth-child(1)',
        'imageselector': '#image',
        'urlregex': '([0-9]{3}(?=\.jpg))',
        'step': 1,
        'trailingzeros': 3
    },

    'www.mangareader.net': {
        'nameselector': '#mangainfo > div:nth-child(1) > h1:nth-child(1)',
        'imageselector': '#img',
        'urlregex': '([0-9]{3}(?=\.jpg))',
        'step': 2,
        'trailingzeros': 3,
    },

    'www.mangapanda.com': {
        'nameselector': '#mangainfo > div:nth-child(1) > h1:nth-child(1)',
        'imageselector': '#img',
        'urlregex': '([0-9]{3}(?=\.jpg))',
        'step': 2,
        'trailingzeros': 3,
    }

}


def display_documentation():
    print("""\
Usage: manga-dl [options] url

Options:
    -h, --help            print this help and exit

Report bugs to https://github.com/JellyPie/manga-dl/issues""")


def get_website(url):
    return urlparse(url).netloc


def get_html(url):
    print("[manga-dl] downloading webpage")
    return requests.get(url).text


def get_manga_name(html, rulebook):
    parser = fromstring(html)
    selector = rulebook['nameselector']
    print("[manga-dl] finding manga name")
    return parser.cssselect(selector)[0].text


def get_image_url(html, rulebook):
    parser = fromstring(html)
    selector = rulebook['imageselector']
    print("[manga-dl] finding images")
    return parser.cssselect(selector)[0].get('src')


def get_urlgen(imageurl, rulebook):
    urlregex = rulebook['urlregex']
    baseurl = re.split(urlregex, imageurl)

    prefix = baseurl[0]
    suffix = baseurl[2]
    start = int(baseurl[1])
    step = rulebook['step']
    trailingzeros = rulebook['trailingzeros']

    pattern = "{}{{:0{}d}}{}".format(prefix, trailingzeros, suffix)
    for i in itertools.count(start, step):
        yield pattern.format(i)


def get_progressbar():
    return ("\r[manga-dl] downloaded image %i" % i for i in itertools.count(1))


def batch_download(urlgen, destinationfolder):
    namegen = ("%03i.jpg" % i for i in itertools.count(1))
    progressbar = get_progressbar()

    while True:
        imagerequest = requests.get(next(urlgen))

        if imagerequest.status_code != 200:
            print("\n[manga-dl] finished downloading")
            break

        sys.stdout.write(next(progressbar))
        sys.stdout.flush()
        with (open(destinationfolder + next(namegen), 'wb+')) as imagefile:
            imagefile.write(imagerequest.content)


def make_comic_archive(fromfolder, tofile):
    with tarfile.open(tofile, 'w') as comicarchive:
        for file in os.listdir(fromfolder):
            comicarchive.add(fromfolder + file, arcname=file)
    print("[manga-dl] created archive")


def main(url):
    website = get_website(url)

    if website not in supported_websites:
        sys.exit('Error: Unsupported website')

    rulebook = supported_websites[website]

    html = get_html(url)
    manganame = get_manga_name(html, rulebook)
    imageurl = get_image_url(html, rulebook)
    urlgen = get_urlgen(imageurl, rulebook)

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = tempdir + os.path.sep
        batch_download(urlgen, tempdir)
        make_comic_archive(tempdir, manganame + '.cbt')


if __name__ == '__main__':

    if len(sys.argv) < 2:
        display_documentation()
        sys.exit()

    if '-h' in sys.argv or '--help' in sys.argv:
        display_documentation()
        sys.exit()

    url = sys.argv[1]
    main(url)
