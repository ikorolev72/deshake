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

    def ffmpegPrepareCommand(self,  tmpFile, line, outputFile):
        id = line['id']
        time_start = line['time_start']
        time_finish = line['time_finish']
        link = line['link']
        make_vertical = line['make_vertical']
        placeholder = line['placeholder']
        both_sides = line['both_sides']
        watermark = line['watermark']

        width = self.width
        height = self.height
        if "0" == str(make_vertical):
            cropFilter = "scale=w=min(iw*"+height+"/ih\,"+width+"):h=min(" + \
                height+"\,ih*"+width + "/iw), setsar=1 "               

        else:
            if int( self.moveMaskWidthPercent) <0 or int(self.moveMaskWidthPercent)>100 :
                self.moveMaskWidthPercent="50"            
            cropFilter = "scale=h="+height+":w=-2, crop=x=(in_w-out_w)/100*"+self.moveMaskWidthPercent+":h="+height+":w="+width+", setsar=1"

        i = 1
        if "0" == str(placeholder) or not os.path.isfile(placeholder):
            placeholder = 0
        inputPlaceholder = ""
        placeholderFilter = "[black] null [video_bg];"
        if "0" != str(placeholder):
            placeholderIndex = i
            inputPlaceholder = "-loop 1 -i "+placeholder + \
                " -ss "+time_start+" -to "+time_finish

            if "1" == both_sides:  # both
                placeholderFilter = "["+str(placeholderIndex)+":v] scale=w="+width + \
                    ":h="+height + \
                    ", setsar=1 [placeholder]; [black][placeholder] overlay [video_bg]; "
            if "2" == both_sides:  # top
                placeholderFilter = "["+str(placeholderIndex)+":v]scale=w="+width + \
                    ":h="+height + \
                    ", setsar=1, crop=w=iw:h=ih/2:x=0:y=0  [placeholder]; [black][placeholder] overlay [video_bg]; "
            if "3" == both_sides:  # bottom
                placeholderFilter = "["+str(placeholderIndex)+":v]scale=w="+width + \
                    ":h="+height + \
                    ", setsar=1, crop=w=iw:h=ih/2:x=0:y=ih/2  [placeholder]; [black][placeholder] overlay=y=H/2[video_bg]; "
            i = i+1

        inputWatermark = ""
        watermarkOverlay = "[video_fg] null [v]"
        if not os.path.isfile(self.watermarkFile):
            watermark = 0
            self.writeLog(
                "Warning: watermark file do not exists. Please, check config file ")
        else:
            if int(watermark) == 1:
                watermarkIndex = i
                i = i+1
                inputWatermark = "-loop 1 -i "+self.watermarkFile + \
                    " -ss "+time_start+" -to "+time_finish
                watermarkOverlay = "["+str(watermarkIndex) + \
                    ":v] null [watermark]; [video_fg][watermark] overlay=x=W-w:y=H-h[v]"
                if "bottom-left" == self.watermarkPosition: #
                    watermarkOverlay = "["+str(watermarkIndex) + \
                    ":v] null [watermark]; [video_fg][watermark] overlay=x=0:y=H-h[v]"
                if "bottom-middle" == self.watermarkPosition: #
                    watermarkOverlay = "["+str(watermarkIndex) + \
                        ":v] null [watermark]; [video_fg][watermark] overlay=x=(W-w)/2:y=H-h[v]"                       
                if "top-left" == self.watermarkPosition: #
                    watermarkOverlay = "["+str(watermarkIndex) + \
                        ":v] null [watermark]; [video_fg][watermark] overlay=x=0:y=0[v]"
                if "top-right" == self.watermarkPosition: #
                    watermarkOverlay = "["+str(watermarkIndex) + \
                        ":v] null [watermark]; [video_fg][watermark] overlay=x=W-w:y=0[v]"
                if "top-middle" == self.watermarkPosition: #
                    watermarkOverlay = "["+str(watermarkIndex) + \
                        ":v] null [watermark]; [video_fg][watermark] overlay=x=(W-w)/2:y=0[v]"                                               
                if "center-left" == self.watermarkPosition:
                    watermarkOverlay = "["+str(watermarkIndex) + \
                        ":v] null [watermark]; [video_fg][watermark] overlay=x=0:y=(H-h)/2[v]"
                if "center-right" == self.watermarkPosition:
                    watermarkOverlay = "["+str(watermarkIndex) + \
                        ":v] null [watermark]; [video_fg][watermark] overlay=x=W-w:y=(H-h)/2[v]"
                if "center-middle" == self.watermarkPosition: #
                    watermarkOverlay = "["+str(watermarkIndex) + \
                        ":v] null [watermark]; [video_fg][watermark] overlay=x=(W-w)/2:y=(H-h)/2[v]"  
                        


        cmd = ' '.join([self.ffmpeg,
                        "-y",
                        "-loglevel",
                        self.logLevel,
                        "-i "+tmpFile+" -ss "+time_start+" -to "+time_finish,
                        inputPlaceholder,
                        inputWatermark,
                        "-filter_complex",
                        "\"color=black:s="+width+"x"+height + "[black];",
                        "[0:v] "+cropFilter+"[video];",
                        placeholderFilter,
                        "[video_bg][video] overlay=x=(W-w)/2:y=(H-h)/2 [video_fg];",
                        watermarkOverlay,
                        "\"",
                        #"-map \"[v]\" -map \"a:0?\" -c:v libx265 -crf 25 -c:a aac",
                        "-map \"[v]\" -map \"a:0?\" -c:v h264 -crf 21 -preset veryfast -c:a aac",
                        outputFile
                        ])
        return cmd

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
