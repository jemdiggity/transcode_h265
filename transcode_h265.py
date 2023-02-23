#!/usr/bin/env python3

import argparse
from pathlib import Path
import subprocess
from datetime import datetime

parser = argparse.ArgumentParser(description=
    '''
    Transcodes files in the input directory and stores them in the output directory.
    Files that already exist will be skipped.
    ''')
parser.add_argument('--src', required=True, dest='source_dir', help='source directory')
parser.add_argument('--out', required=True, dest='out_dir', help='output directory')
parser.add_argument('--fix_tag', required=False, action='store_const', const=True, dest='fix_tag', help="Just add hvc1 tag")

args = parser.parse_args()

print(f'Input dir is {args.source_dir}')
print(f'Output dir is {args.out_dir}')

input_dir = Path(args.source_dir)
if not input_dir.is_dir():
    print(f'{input_dir} is not a directory')
    exit(-1)

output_dir = Path(args.out_dir)
if not output_dir.is_dir():
    print(f'{output_dir} is not a directory')
    exit(-1)

input_extensions = ['MOV', 'MP4', 'mp4']
output_extension = 'mp4'

input_files = []
for input_extension in input_extensions:
    input_files += sorted(list(input_dir.rglob(f'*.{input_extension}')))
print(f'Found {len(input_files)} input files')

for each in input_files:
    if not each.is_file():
        continue

    output_file = each.parent.relative_to(input_dir) / each.with_suffix("." + output_extension).name
    print(output_file)

    #Check if existing file has same duration.
    if (output_dir / output_file).exists():
        input_file_duration = subprocess.run([
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(each)
        ], capture_output=True, text=True).stdout

        output_file_duration = subprocess.run([
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(output_dir / output_file)
        ], capture_output=True, text=True).stdout

        if int(float(input_file_duration)) < int(float(output_file_duration)) - 1 or int(float(input_file_duration)) > int(float(output_file_duration)) + 1:
            print(f'{output_file} exists but duration is different. {input_file_duration} != {output_file_duration}')
            raise Exception("Check input and output files. There shouldn't be duplicate file names.")

        print(f'{output_file} exists in {output_dir}. Skipping')
        continue

    command = ["ffprobe",
        "-v", "quiet",
        "-select_streams", "v:0",
        "-show_entries", "stream_tags=creation_time",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(each)]

    creation_time_tag = subprocess.run(command, capture_output=True, text=True).stdout.strip()
    creation_time = False if creation_time_tag == "" else datetime.fromisoformat(creation_time_tag).strftime("%Y%m%d%H%M.%S")
    if creation_time:
        print("Creation time: " + creation_time)

    if not (output_dir / output_file).parent.exists():
        (output_dir / output_file).parent.mkdir(parents=True)

    #Final Cut Pro requires "hvc1" metadata tag.
    if args.fix_tag:
        command = ["ffmpeg",
        "-hide_banner",
        "-i", str(each),
        "-c:v", "copy",
        "-tag:v", "hvc1",
        "-c:a", "copy",
        "-map_metadata", "0",
        str(output_dir / output_file)
        ]
        subprocess.run(command, check=True)
    else:
        command = ["ffmpeg",
            "-hide_banner",
            "-i", str(each),
            "-c:v", "libx265",
            "-crf", "26",
            "-preset", "fast",
            "-tag:v", "hvc1",
            "-c:a", "aac",
            "-b:a", "128k",
            "-map_metadata", "0",
            str(output_dir / output_file)]
        subprocess.run(command, check=True)

    if creation_time:
        command  = ["touch",
            "-t", creation_time,
            str(output_dir / output_file)]
        subprocess.run(command, check=True)

exit(0)
