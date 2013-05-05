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
        output[mod] = getVersion(meta_data[mod]["url"], meta_data[mod]["scraperRegex"])

    with args.output:
        json.dump(output, args.output)
        os.chmod(args.output.name, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH)


def getVersion(url, regex):
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    digestable = soup.getText().encode("ascii", "ignore").replace("\n", "").replace(" ", "").replace("\t", "")

    m = re.search(regex, digestable)
    if m is not None:
        return m.group('version').strip().encode("utf8")


if __name__ == '__main__':
    main()