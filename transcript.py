# -*- encoding: utf-8 -*-

import scrapetube
from datetime import datetime
import dateutil.parser
import sys
import requests, json, os, glob, time
from zoneinfo import ZoneInfo
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig
from youtube_transcript_api.formatters import SRTFormatter

class Program():
    def __init__(self, idchannel, urlchannel, content_types, tz, dateFormats):
        self.idchannel = idchannel
        self.urlchannel = urlchannel
        self.content_types = content_types
        self.tzinfo = ZoneInfo(tz)
        self.dateFormats = dateFormats
        
        self.initLoggingFile()
            
    def initLoggingFile(self):
        loggingfilename = "transcript_" + self.idchannel
        self.loggingfile = open(loggingfilename + ".log", "a", encoding="utf-8")
    
    def getDateNow(self):
        timestamp_now = datetime.now().timestamp()
        date = datetime.fromtimestamp(timestamp_now, self.tzinfo)
        dateString = date.strftime(self.dateFormats['dateString'])
        dateDBString = date.strftime(self.dateFormats['dateDBString'])
        dateFileString = date.strftime(self.dateFormats['dateFileString'])
        
        dateNow = {"dateString": dateString, "dateDBString": dateDBString, "dateFileString": dateFileString}
        
        return dateNow

    def writelog(self, message):       
        dateNow = self.getDateNow()
        self.loggingfile.write(dateNow['dateString'] + " : " + message + "\n")
        # Write in real time
        self.loggingfile.flush()
            
    # Used when errors/exceptions occured and when we want to exit right now
    def exitProgram(self):
        self.writelog("Execution had errors")
        self.writelog("Ending program")
        self.clean()
        sys.exit(1)
    
    # Used at the end of program without errors/exceptions and when errors/exception occured
    def clean(self):
        try:
            # Close Files
            self.loggingfile.close()
        except Exception as e:
            print("Error cleaning up : " + str(e))
    
    def main(self):
        print("Starting program")
        self.writelog("Starting program")

        # Proxy config, as Youtube is temporarily banning IP really fast
        useProxy = False

        proxy_config = None
        if useProxy is True:
            proxy_config=GenericProxyConfig(
                https_url="",
            )
            
        ytt_api = YouTubeTranscriptApi(
            proxy_config=proxy_config
        )

        for content_type in self.content_types:
            print(content_type)
            self.writelog(content_type)
            
            # Get all videos
            videos = scrapetube.get_channel(channel_id=self.idchannel, content_type=content_type, sort_by="newest")
            listVideos = list(videos)

            limitVideos = 10
            print(str(len(listVideos)) + ' ' + content_type)
            self.writelog(str(len(listVideos)) + ' ' + content_type)
            print("Subtitles number to download : " + str(limitVideos))
            self.writelog("Subtitles number to download : " + str(limitVideos))
            index = 0

            for video in listVideos:
                print("Try num : " + str(index + 1))
                self.writelog("Try num : " + str(index + 1))
                print(video['videoId'])
                self.writelog(video['videoId'])
                                
                url = "https://www.youtube.com/watch?v="+str(video['videoId'])
                idVideo = video['videoId']
                print(url)

                # Check if we already have subtitle
                subfiles = glob.glob('transcript_*' + idVideo + '*.srt')
                if len(subfiles) > 0:
                    print('Subtitle already present')
                    self.writelog('Subtitle already present')
                    continue

                print('We get subtitle')
                try:        
                    transcript_list = ytt_api.list(idVideo)
                    # Check if fr is in list
                    hasFrench = False
                    for t in transcript_list:
                        if t.language_code == 'fr':
                            hasFrench = True
                            break

                    if (hasFrench is False) :
                        print("No french auto generated subtitles")
                        self.writelog("No french auto generated subtitles")
                        continue

                    print("French auto generated is present")
                    self.writelog("French auto generated is present")
                    
                    transcript = transcript_list.find_generated_transcript(['fr'])
                    fetchedTranscript = transcript.fetch()

                    formatter = SRTFormatter()
                    srt_formatted = formatter.format_transcript(fetchedTranscript)
                    dateNow = self.getDateNow()
                    srt_file = open('transcript_' + idVideo + '_' + dateNow["dateFileString"] + '.srt', 'w', encoding='utf-8')
                    srt_file.write(srt_formatted)
                    srt_file.close()
                    print("French auto generated is saved")
                    self.writelog("French auto generated is saved")
                    
                    index = index + 1
                except Exception as e:
                    print("Exception line : " + str(sys.exc_info()[-1].tb_lineno))
                    self.writelog("Exception line : " + str(sys.exc_info()[-1].tb_lineno))
                    print(f"[×] Error in getting and saving subtitle : {e}")
                    self.writelog(f"[×] Error in getting and saving subtitle : {e}")

                if index == limitVideos:
                    print("Limit of " + str(limitVideos) + " has passed")
                    self.writelog("Limit of " + str(limitVideos) + " has passed")
                    break

                time.sleep(30)

        print("Execution was OK")
        self.writelog("Execution was OK")
        print("Ending program")
        self.writelog("Ending program")
        self.clean()

if __name__ == "__main__":
    # Youtube
    urlchannel = "https://www.youtube.com/@your_channel"
    idchannel = '' # Found channel id on Youtube by clicking "Share channel" then "Copy channel ID"
    content_types = ["streams", "videos", "shorts"] # Possible values : "streams", "videos", "shorts"
    # Format
    tz = "Europe/Paris"
    dateFormats = {"dateString": "%d/%m/%Y %H:%M:%S", "dateDBString": "%Y-%m-%d %H:%M:%S", "dateFileString": "%d%m%Y%H%M%S"}

    # Launch
    program = Program(idchannel, urlchannel, content_types, tz, dateFormats)
    program.main()
    

