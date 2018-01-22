#!/usr/bin/python3.5

# convert video files in QHD resolution (2560x1440)
# Directory usage:   ./convert2qhd.py -d directory_path
# Single file usage: ./convert2qhd.py input_video_file (ouput_file_name)

import os
import sys
import subprocess


def convert_resolution(in_name, width, height, out_name=""):
    name, ext = in_name.rsplit(".", maxsplit=1)
    if not out_name:
        out_name  = "{}QHD.{}".format(name, ext)
    res = "scale={}:{}".format(width, height)
    subprocess.run(["ffmpeg", "-i", in_name, "-vf", res, out_name])

def directory_usage(dir_path):
    samples = os.listdir(dir_path)
    for sample in samples:
        sample_path = dir_path + sample
        convert_resolution(sample_path, -2, 1440)

user_help = """
Directory usage:   ./convert2qhd.py -d directory_path
Single file usage: ./convert2qhd.py input_video_file (ouput_file_name)
"""

args = sys.argv
argc = len(args)

if argc < 2 or argc > 3:
    print(user_help)

if argc == 3 and args[1] == "-d":
    # Directory usage
    dir_path = args[2]
    if not os.path.isdir(dir_path):
        print("{} is not a directory".format(dir_path))
        print(user_help)
        sys.exit()
    if (dir_path[-1] != "/"):
        dir_path += "/"
    directory_usage(dir_path)
elif argc == 2 or argc == 3:
    # Single file usage
    sample = args[1]
    if not os.path.isfile(sample):
        print("{} is not a file".format(sample))
        print(user_help)
        sys.exit()
    convert_resolution(sample, -2, 1440)
