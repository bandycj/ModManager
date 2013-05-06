import argparse
import glob
import json
import os
import re
import zipfile

from stat import S_IRUSR, S_IWUSR, S_IRGRP, S_IWGRP, S_IROTH
from minecraft_query import MinecraftQuery

__author__ = 'e83800'


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    meta_data = json.load(open(current_dir + '/mods.json'))

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', required=True, help="Minecraft directory.")
    parser.add_argument('-o', '--output', required=True, type=argparse.FileType('w'), help="The file to write the JSON to.")
    parser.add_argument('-s', '--server', required=False, help="Minecraft server address (default: localhost).")
    parser.add_argument('-p', '--port', required=True, help="The port this instance is on")
    args = parser.parse_args()

    server = "localhost"
    if args.server is not None:
        server = args.server
    query = MinecraftQuery(server, int(args.port))
    full_info = query.get_rules()

    minecraft_dir = args.directory
    output = {"minecraft": full_info['version']}
    for mod_file in glob.glob(minecraft_dir + "/*mods/*"):
        for key in meta_data:
            if meta_data[key]['fileRegex'] != "":
                m = re.search('(?i)' + meta_data[key]['fileRegex'] + '\\.(jar|zip)', mod_file)
                if m is not None:
                    output[key] = {}
                    try:
                        output[key]['version'] = m.group('version')
                    except IndexError:
                        # no version regex, ignore
                        pass
                    try:
                        output[key]['mcversion'] = m.group('mcversion')
                    except IndexError:
                        # no minecraft version regex, ignore
                        pass

                    if 'mcversion' not in output[key] or 'version' not in output[key]:
                        root = zipfile.ZipFile(mod_file, "r")
                        try:
                            root.getinfo('mcmod.info')
                            lines = root.open('mcmod.info').readlines()
                            mcmod_info = '\n'.join([str(x) for x in lines]).encode("ascii", "ignore").replace("\n", "").replace(" ", "").replace("\t", "")

                            m1 = re.search('mcversion[":\s]+(?P<mcversion>[\d.]+)',mcmod_info)
                            if m1 is not None and 'mcversion' not in output[key]:
                                output[key]['mcversion'] = m1.group('mcversion')
                            if 'version' not in output[key]:
                                m2 = re.search('version[":\s]+(?P<version>[\d.]+)',mcmod_info)
                                if m2 is not None:
                                    output[key]['version'] = m2.group('version')
                        except KeyError:
                            # no mcmod.info, ignore
                            pass

                    if 'version' in output[key] and 'mcversion' in output[key]:
                        break

    for key in meta_data:
        if key in output:
            if 'version' not in output[key] or output[key]['version'] == "":
                output[key]['version'] = "na"
            if 'mcversion' not in output[key] or output[key]['mcversion'] == "":
                output[key]['mcversion'] = "na"
            print key + "\t:\t" + output[key]['version'] + "\t:\t" + output[key]['mcversion']

    with args.output:
        json.dump(output, args.output)
        os.chmod(args.output.name, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH)


def sanitize(line):
    line = line.replace("mc", "")
    line = line.replace("version", "")
    line = line.replace(":", "")
    line = line.replace("\"", "")
    line = line.replace(",", "")
    line = line.strip()
    if line != "":
        return line
    else:
        return "na"


if __name__ == "__main__":
    main()
