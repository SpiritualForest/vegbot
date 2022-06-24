import youtube_dl

opts = {"proxy": "socks5://127.0.0.1:9050"}

def getVideoInfo(url):
    # Returns (title, uploader, duration)
    try:
        with youtube_dl.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except (youtube_dl.utils.ExtractorError, youtube_dl.utils.DownloadError):
        print("Error fetching video info")
        return (None, None, None)
    m, s = divmod(info["duration"], 60)
    if s < 10:
        s = "0" + str(s)
    if m > 60:
        h, m = divmod(m, 60)
        if m < 10:
            m = "0" + str(m)
        durationStr = f"{h}:{m}:{s}"
    else:
        if m < 10:
            m = "0" + str(m)
        durationStr = f"{m}:{s}"
    
    return (info["title"], info["uploader"], durationStr)

if __name__ == "__main__":
    print(getVideoInfo("https://www.youtube.com/watch?v=_yROyxWcudo"))
    print(getVideoInfo("https://www.youtube.com/watch?v=j0_u26Vpb4w"))
