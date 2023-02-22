# transcode_h265
Python script to transcode video files to h265 (HEVC) using ffmpeg.

Transcodes files in the input directory and stores them in the output directory.  

Files with extension MP4 or MOV are included.
Output files will end in MP4 extension.

If the output file already exists and its duration is the same as the input file, it will be skipped.
If the duration is different, the script will report an error and quit.

Metadata is copied to the output file.
If creation_time exists in the metadata, the file's created timestamp will be set to it.
  
## Install
* Requires Python3 version *3.11* or greater
* Requires ffmpeg

## Usage
    transcode_h265.py --src SOURCE_DIR --out OUT_DIR

