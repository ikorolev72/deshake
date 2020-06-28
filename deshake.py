#!/usr/bin/env python3


import os
import subprocess
import argparse
import sys
import json
import unicodedata
import time
from pathlib import Path
import csv


from lib.version import version
from lib.processing import processing


baseDir = os.path.dirname(os.path.realpath(__file__))

# parse command line options
# Instantiate the parser
parser = argparse.ArgumentParser(
    description='Deshake input video file')
parser.add_argument('-c', '--config', required=False,
                    help='Path to config file')

parser.add_argument('-v', '--version', action='version',
                    version='%(prog)s '+version)
parser.add_argument('-i', '--input', required=False,
                    help='Input video file')
parser.add_argument('-o', '--output', required=False,
                    help='Output video file')
parser.add_argument('-w', '--overwrite', required=False, action='store_const', const=True, 
                    help='Overwrite input file')

args = parser.parse_args()
configFile = args.config

if args.config is None:
    configFile = baseDir+"/data/config.json"     # Config
else:
    configFile = str(args.threads)


try:
    with open(configFile) as json_file:
        config = json.load(json_file)
except IOError:
    print(("Error: Cannot read config file: "+configFile))
    sys.exit(1)


logFile = baseDir+"/log/processing.log"
processing = processing(config, logFile)
errors = 0

if  args.input is None and not os.environ.get(config['general']['inputVariable']):
    processing.writeLog(
        ("Error: Do not get parameter '--input' and do not set environment variable " + config['general']['inputVariable']))
    errors = +1
    # sys.exit(1)

if  not args.overwrite and  args.output is None and not os.environ.get(config['general']['outputVariable']):
    processing.writeLog(
        ("Error: Do not get  parameter '--output' and do not set environment variable " + config['general']['outputVariable']))
    errors = +1
    # sys.exit(1)

if errors > 0:
    sys.exit(1)


def main():
    filesForRemove = []
    processing.writeLog("Info: Script started")

    if os.environ.get(config['general']['inputVariable']):
        inputFile = os.environ.get(config['general']['inputVariable'])
    if args.input:
        inputFile = args.input

    if os.environ.get(config['general']['outputVariable']):
        outputFile = os.environ.get(config['general']['outputFile'])
    if args.output:
        outputFile = args.output
    if args.overwrite:
        outputFile = inputFile

    if not os.path.isfile(inputFile):
        processing.writeLog(
            "Error: input file '"+str(inputFile)+"'for processing do nto exists")
        sys.exit(1)

    if processing.getVideoDuration(inputFile) == 0:
        processing.writeLog(
            "Error: Cannot get duration of input video file. Something wrong")
        sys.exit(1)

    tmpFile = processing.getTmpFileName('.mp4')

    filesForRemove.append(tmpFile)
    # prepare ffmpeg command
    commands = processing.ffmpegPrepareCommand(inputFile, tmpFile )

    for cmd in commands :
        processing.writeLog(
                    "Info: Prepared command:" + cmd)
        try:
            if not processing.doExec(cmd):
                processing.writeLog(
                    "Error: Fatal. Cannot execute ffmpeg command")
                processing.removeTmpFiles(filesForRemove)
                sys.exit(1)
                
        except:
            processing.writeLog(
                "Error: Fatal. Cannot execute ffmpeg command")
            processing.removeTmpFiles(filesForRemove)
            sys.exit(1)

    try:
        os.rename(tmpFile, outputFile)      
    except:
        processing.writeLog(
                "Error: Cannot rename file "+tmpFile+" to "+ outputFile)                
        sys.exit(1)


    # except IOError:
    #    print(("Error: Cannot read csv file: "+csvDataFile))
    #    processing.writeLog("Info: Script finished")
    #    processing.removeTmpFiles(filesForRemove)
    #    sys.exit(1)

    processing.writeLog("Info: Script finished")
    processing.removeTmpFiles(filesForRemove)
    sys.exit(0)


if __name__ == '__main__':
    main()
