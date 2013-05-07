import argparse
import json
import os
import re
from stat import S_IRUSR, S_IWUSR, S_IRGRP, S_IWGRP, S_IROTH
import urllib2

__author__ = 'Chris'

from bs4 import BeautifulSoup


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', required=True, type=argparse.FileType('w'), help="The file to write the JSON to.")
    args = parser.parse_args()

    output = {}

    current_dir = os.path.dirname(os.path.abspath(__file__))
    meta_data = json.load(open(current_dir + '/mods.json'))

    for mod in meta_data:
        output[mod] = {}
        output[mod]['version'] = getVersion(meta_data[mod]["url"], meta_data[mod]["scraperRegex"])
        output[mod]['url'] = meta_data[mod]['url']

        print mod
        print "\t" + output[mod]

    with args.output:
        json.dump(output, args.output)
        os.chmod(args.output.name, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH)


def getVersion(url, regex):
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    digestable = re.sub("[\n\r\s\t]+", "", soup.getText().encode("ascii", "ignore"))

    m = re.search(regex, digestable)
    if m is not None:
        return m.group('version').strip()


if __name__ == '__main__':
    main()
    # print getVersion("http://files.minecraftforge.net/", "BuildsBuild(?P<version>[\d.]+):\d{4}")