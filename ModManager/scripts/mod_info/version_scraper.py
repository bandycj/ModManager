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
    # print getVersion("http://www.minecraftforum.net/topic/1536685-151152forge-hit-splat-damage-indicators-v264-rpg-ui-and-damage-amount-mod/", "DOWNLOADDamageIndicators\[[\d.]+\]v(?P<version>[\d.]+)")