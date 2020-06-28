import os
import re
import sys
import datetime
import platform
import subprocess
import json
from random import randint
import time
import zlib
import unicodedata
import hashlib


class processing:
    def __init__(self, config, logFile):
        self.config = config
        self.logFile = logFile
        self.tmpDir = config['general']['tmpDir']
        self.ffmpeg = config['general']['ffmpeg']
        self.ffprobe = config['general']['ffprobe']
        # ffmpeg log level ( error, warning, info, debug, etc)
        self.logLevel = config['general']['ffmpegLogLevel']
        self.step1 = config['commands']['step1']
        self.step2 = config['commands']['step2']        

    def get_script_path(self):
        return os.path.dirname(os.path.realpath(sys.argv[0]))

    def getTmpFileName(self, suffix):
        # succeeds even if directory exists.
        os.makedirs(self.tmpDir, exist_ok=True)
        fileName = "{0}/{1}{2}{3}".format(self.tmpDir,
                                          time.time(), randint(10000, 99999), suffix)
        return(fileName)

    def getAudioDuration(self, file):
        try:
            cmd = self.ffprobe + ' -v quiet -of csv=p=0 -show_entries format=duration -select_streams a:0' + file
            if os.path.isfile(file):
                info = subprocess.getoutput(cmd)
                if not info:
                    self.writeLog(
                        "Error: Cannot get audio stream info for file "+file)
                    return 0
            else:
                info=0
            # if file do not exists
            return info
        except:
            return 0

    def getVideoDuration(self, file):
        try:
            cmd = self.ffprobe + ' -v quiet -of csv=p=0 -show_entries format=duration -select_streams v:0 ' + file
            if os.path.isfile(file):
                info = subprocess.getoutput(cmd)
                if not info:
                    self.writeLog(
                        "Error: Cannot get video stream info for file "+file)
                    return 0
            else:
                info=0
            # if file do not exists
            return info
        except:
            return 0

    # Write messages to stderr. Change this function if you need write real log-file

    def writeLog(self, message):
        today = datetime.datetime.today()
        dt = today.strftime('%Y-%m-%d %H:%M:%S')
        sys.stderr.write(dt+" "+message+"\n")
        try:
            # if not os.path.isfile(self.logFile):
            #  f=open(self.logFile, "w")
            # else:
            f = open(self.logFile, "a")
            f.write(dt+" "+message+"\n")
            f.close()
        except:
            print("Warning: cannot append to log file:"+self.logFile)

    def ffmpegPrepareCommand(self, inputFile, outputFile):
        vectors=self.getTmpFileName(".trf")
        command1 = self.step1 % {'ffmpeg': self.ffmpeg, 'input': inputFile, 'vectors': vectors }
        command2 = self.step2 % {'ffmpeg': self.ffmpeg, 'input': inputFile, 'vectors': vectors, 'output':outputFile }
        commands=[]
        commands.append(command1)
        commands.append(command2)

        return commands

    def doExec(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True)
        except subprocess.CalledProcessError:
            # print "error code", grepexc.returncode, grepexc.output
            self.writeLog("Error: Someting wrong during execute command "+cmd)
            return False
        if result.returncode == 0:
            return True
        return False



    def removeTmpFiles(self, filesForRemove):
        for file in filesForRemove:
            if os.path.exists(file):
                os.remove(file)
                self.writeLog("Temp file "+file + " was removed")
            else:
                self.writeLog("Warning: The file "+file +
                              " does not exist. Cannot remove this file")
        return True

    def crc(self, a_file_name):
        prev = 0
        for eachLine in open(a_file_name, "rb"):
            prev = zlib.crc32(eachLine, prev)
        return "%X" % (prev & 0xFFFFFFFF)

    def md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
