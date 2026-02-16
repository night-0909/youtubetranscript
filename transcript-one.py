# -*- encoding: utf-8 -*-

import scrapetube
from datetime import datetime
import dateutil.parser
import sys
import requests, json, glob, time
from zoneinfo import ZoneInfo
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig
from youtube_transcript_api.formatters import SRTFormatter

class Program():
    def __init__(self, idchannel, urlchannel, idVideo, tz, dateFormats):
        self.idchannel = idchannel
        self.urlchannel = urlchannel
        self.idVideo = idVideo
        self.tzinfo = ZoneInfo(tz)
        self.dateFormats = dateFormats
            
    def getDateNow(self):
        timestamp_now = datetime.now().timestamp()
        date = datetime.fromtimestamp(timestamp_now, self.tzinfo)
        dateString = date.strftime(self.dateFormats['dateString'])
        dateDBString = date.strftime(self.dateFormats['dateDBString'])
        dateFileString = date.strftime(self.dateFormats['dateFileString'])
        
        dateNow = {"dateString": dateString, "dateDBString": dateDBString, "dateFileString": dateFileString}
        
        return dateNow
                
    def main(self):
        print("Starting program")

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

        url = "https://www.youtube.com/watch?v="+self.idVideo
        print(url)

        try:        
            transcript_list = ytt_api.list(self.idVideo)
            # Check if fr is in list
            hasFrench = False
            for t in transcript_list:
                if t.language_code == 'fr':
                    hasFrench = True
                    break

            if (hasFrench is False) :
                print("No french auto generated subtitles")
                sys.exit(1)

            print("French auto generated is present")
            transcript = transcript_list.find_generated_transcript(['fr'])
            fetchedTranscript = transcript.fetch()

            formatter = SRTFormatter()
            srt_formatted = formatter.format_transcript(fetchedTranscript)
            dateNow = self.getDateNow()
            srt_file = open('transcript_' + self.idVideo + '_' + dateNow["dateFileString"] + '.srt', 'w', encoding='utf-8')
            srt_file.write(srt_formatted)
            srt_file.close()
            print("French auto generated is saved")
        except Exception as e:
            print("Exception line : " + str(sys.exc_info()[-1].tb_lineno))
            print(f"[×] Error in getting and saving subtitle : {e}")

if __name__ == "__main__":
    # Youtube
    urlchannel = "https://www.youtube.com/@your_channel"
    idchannel = '' # Found channel id on Youtube by clicking "Share channel" then "Copy channel ID"
    idVideo = ''
    # Format
    tz = "Europe/Paris"
    dateFormats = {"dateString": "%d/%m/%Y %H:%M:%S", "dateDBString": "%Y-%m-%d %H:%M:%S", "dateFileString": "%d%m%Y%H%M%S"}

    # Launch
    program = Program(idchannel, urlchannel, idVideo, tz, dateFormats)
    program.main()
