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
parser = argparse.ArgumentParser(
    description='Deshake input video file')
parser.add_argument('-c', '--config', required=False,
                    help='Path to config file')

parser.add_argument('-v', '--version', action='version',
                    version='%(prog)s '+version)
parser.add_argument('-i', '--input', required=False,
                    help='Input video file or directory')
parser.add_argument('-o', '--output', required=False,
                    help='Output video file')


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
tmpDir = "tmp"
processing = processing(config, logFile, tmpDir)
errors = 0

if args.input is None and not os.environ.get(config['general']['inputVariable']):
    processing.writeLog(
        ("Error: Do not get parameter '--input' and do not set environment variable " + config['general']['inputVariable']))
    errors = +1

if  args.output is None and not os.environ.get(config['general']['outputVariable']):    
    processing.writeLog(
        ("Info: Do not get parameter '--output' and do not set environment variable " + config['general']['outputVariable']))
    processing.writeLog(
       "Info: Input files will be overwritten")
    #errors = +1

if errors > 0:
    sys.exit(1)


def main():
    filesForRemove = []
    processing.writeLog("Info: Script started")

    if os.environ.get(config['general']['inputVariable']):
        inputPath = os.environ.get(config['general']['inputVariable'])
    if args.input:
        inputPath = args.input
    
    outputFile = inputPath
    if os.environ.get(config['general']['outputVariable']):
        outputFile = os.environ.get(config['general']['outputVariable'])
    if args.output:
        outputFile = args.output

    
    inputFiles = []
    if os.path.isdir(inputPath):
        processing.writeLog(
            "Info: input path "+inputPath+"is directory, Will process all video files there")
        inputFiles = processing.scanDirectory(
            inputPath, config['general']['extensions'])
    else:
        inputFiles.append(inputPath)

    for inputFile in inputFiles:
        if not os.path.isfile(inputFile):
            processing.writeLog(
                "Error: input file '"+str(inputFile)+"' for processing do not exists")
            continue
        processing.writeLog(
                "Info: Start processing input file '"+str(inputFile)+"'")
        if processing.getVideoDuration(inputFile) == 0:
            processing.writeLog(
                "Error: Cannot get duration of input video file. Something wrong")
            continue
        if os.path.isdir(inputPath):
            outputFile = inputFile

        tmpFile = processing.getTmpFileName('.mp4')

        # prepare ffmpeg command
        commands = processing.ffmpegPrepareCommand(inputFile, tmpFile)

        for cmd in commands:
            processing.writeLog(
                "Info: Prepared command:" + cmd)
            try:
                if not processing.doExec(cmd):
                    processing.writeLog(
                        "Error: Fatal. Cannot execute ffmpeg command")
                    processing.removeTmpFiles()
                    continue

            except:
                processing.writeLog(
                    "Error: Fatal. Cannot execute ffmpeg command")
                processing.removeTmpFiles()
                continue

        try:
            backupFile = baseDir+"/backup/" + \
                str(time.time()) + "_"+os.path.basename(inputFile)
            if config['general']['backup']:
                os.rename(inputFile, backupFile)
        except:
            processing.writeLog(
                "Error: Cannot make backup of input file. Cannot rename file " + inputFile + " to " + backupFile )
            processing.writeLog(
                "Info: Processed file is stored as " + tmpFile)
            continue
        try:
            os.rename(tmpFile, outputFile)
        except:
            processing.writeLog(
                "Error: Cannot rename file "+tmpFile+" to " + outputFile)
            continue

    processing.writeLog("Info: Script finished")
    processing.removeTmpFiles()
    sys.exit(0)


if __name__ == '__main__':
    main()
