# deshake

This script `deshake` - remove camera shake from hand-holding a camera in video files . Features:
  + input file can be defined by enviroment variable or in command line
  + by default, output file will overwrite input file, or output file can be set in command line or as enviroment variable
  + if input parameters is directory, will be processed all video files in this directory
  + input files can be backuped. This option can be defined in `config` file

## Version
#### Version 1.0 20200630

## What's new

  Version 1.0 20200630

  + Working version


## How to install

```bash
git clone https://github.com/ikorolev72/deshake.git
cd deshake
chmod +x deshake.py
./deshake.py
```


## How to run
Command line options:
```
usage: deshake.py [-h] [-c CONFIG] [-v] [-i INPUT] [-o OUTPUT] [-w]

Deshake input video file

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to config file
  -v, --version         show program's version number and exit
  -i INPUT, --input INPUT
                        Input video file or directory
  -o OUTPUT, --output OUTPUT
                        Output video file
  Example :
  deshake.py --input /home/user/1.mp4 --output /tmp/2.mp4 
  deshake.py --input /home/user/ 
  ```

  or can be set enviroment variables `$File_Name` and `$OutName` ( variable names can be defined in `data/config.json` file ), those variables will be used as `--input` and `--output` options.


## Appendix
#### Files and directory structure
```
backup/ - backup input files to this directory ( [general][ backup] must be set to `true` )
data/config.json - config file
lib/processing.py - main processing library
log/processing.log - log file
tmp/ - directory for temporary files
deshake.py - main script
README.md - this README file
``` 

  #### Config file
  In config file `data/config.json` set most part of specified parameters
  ```json
  {
  "general": { 
    "ffmpeg": "ffmpeg", // ffmpeg binaries, can be set absolute path to ffmpeg, eg /my/path/ffmpeg
    "ffprobe": "ffprobe", // ffprobe binaries, can be set absolute path to ffprobe, eg /my/path/ffprobe
    "ffmpegLogLevel": "warning", // ffmpeg loglevel, eg info, warning, error, debug
    "tmpDir": "tmp", // dir for temporary files, can set set relative or absolute path, eg /tmp
    "inputVariable": "File_Name", // this variable set the input file or directory
    "outputVariable": "OutName", // this variable set the output file
    "backup": true, // make backup of input file, if it will be overwritten
    "extensions": [ // check those video extensions for video files in directory
      ".avi",
      ".mkv",
      ".mov",
      ".mp4",
      ".flv",
      ".m2ts",
      ".mts",
      ".wmv",
      ".asf",
      ".amv",
      ".m4p",
      ".mpg",
      ".mp2",
      ".mpeg",
      ".mpe",
      ".mpv",
      ".m2v",
      ".m4v",
      ".svi",
      ".3gp"
    ]
  },
  "commands": {
    "step1": "%(ffmpeg)s -y -i \"%(input)s\" -loglevel %(loglevel)s -vf vidstabdetect=stepsize=15:shakiness=10:accuracy=10:result=\"%(vectors)s\" -f null - ",
    "step2": "%(ffmpeg)s -y -i \"%(input)s\" -loglevel %(loglevel)s -vf vidstabtransform=input=\"%(vectors)s\":zoom=0:smoothing=30,unsharp=5:5:0.8:3:3:0.4,scale=1920:-1 -vcodec libx264 -tune film -an \"%(output)s\" "
  }
}
  ```


##  Bugs
##  ------------

##  Licensing
  ---------
	GNU

  Contacts
  --------

     o korolev-ia [at] yandex.ru
     o http://www.unixpin.com



