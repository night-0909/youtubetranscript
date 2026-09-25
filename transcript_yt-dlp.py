import os, sys, subprocess, io, time, glob

def record_process_logfile(process, logfile):
    # Save stdout/stderr of process.
    flogfile = open(logfile, 'a', encoding="utf-8")
    for line in io.TextIOWrapper(process.stdout):
        message = line.rstrip()
        print(message)
        flogfile.write(message + "\n")
        # Write in real time
        flogfile.flush()
    
    flogfile.close()

def save_url_files(save_url, urlchannel, download_folder, urlfile, logfile):
    if save_url is True:
        print("Save url list of Youtube videos for this channel")
        if os.path.isfile(urlfile):
            os.remove(urlfile)
        
        # Save url list of Youtube videos for this channel
        yt_dlp_process = subprocess.Popen(['yt-dlp', "-v", "--flat-playlist", "--print-to-file", "%(url)s", urlfile, urlchannel],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        record_process_logfile(yt_dlp_process, logfile)
        yt_dlp_process.wait()
        print("Return code : " + str(yt_dlp_process.returncode))

def download_url_files(download_url, urlchannel, download_folder, urlfile, logfile):
    if download_url is True:
        print("Download files")
        
        if os.path.exists(urlfile) is False:
            print("File containing urls not found : " + urlfile)
            return
        
        urlfileh = open(urlfile, 'r', encoding='utf-8')
        urls = urlfileh.readlines()
        urlfileh.close()
        
        for url in urls:
            print(url)
            idVideo = url.strip().replace("https://www.youtube.com/watch?v=", "")
            if len(glob.glob(glob.escape(download_folder) + "transcript_" + idVideo + "*")) > 0:
                print("File for video " + idVideo + " is already present")
                continue

            try:
                yt_dlp_process = subprocess.Popen(['yt-dlp', "-v", "--impersonate", "firefox", "--cookies", "Y:/_Documents_Perso/Perso/Dev/Youtube/cookiesYT.txt",
                "--extractor-args", "youtube:player-client=default,web_embedded,mweb", "--skip-download", "--write-auto-subs", "--sub-lang", "fr",
                "--sub-format", "srt", "-o", f"{download_folder}transcript_%(id)s.%(ext)s", '--remote-components', 'ejs:github', '--js-runtimes', 'deno:c:/users/sylvain/.deno/bin',
                url],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                # Trace stdout and stderr of yt_dlp process
                record_process_logfile(yt_dlp_process, logfile)
                yt_dlp_process.wait()
                print("Return code : " + str(yt_dlp_process.returncode))
                if yt_dlp_process.returncode == 0:
                    print("Success downloading")
                else:
                    print("Error downloading")

                time.sleep(30)
            except Exception as e:
                print(f"url={url} Error yt-dlp : exception={e}")

if __name__ == "__main__":
    # Settings
    save_url = False
    download_url = True
    channel = '@something'
    urlchannel = 'https://www.youtube.com/' + channel + '/videos' # urlchannel can be : youtube.com/channel/zzz/, youtube.com/channel/zzz/videos, youtube.com/@aaa, youtube.com/@aaa/videos, etc...
    download_folder = r"path/something" + os.path.sep
    logfile = download_folder + 'yt-dlp-download_log' + '_something.txt'
    urlfile = download_folder + 'yt-dlp-download_videos' + '_something.txt'

    save_url_files(save_url, urlchannel, download_folder, urlfile, logfile)
    download_url_files(download_url, urlchannel, download_folder, urlfile, logfile)
    
