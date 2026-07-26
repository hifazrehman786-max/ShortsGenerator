import os
import requests
import urllib.parse
import yt_dlp
from typing import List
from termcolor import colored

# =================================================================
# 1. YOUTUBE FALLBACK FUNCTION (BINA API KEY KE)
# =================================================================
def search_youtube_videos(query: str, it: int = 1) -> List[str]:
    """
    YouTube se exact topic search karke MP4 stream URL lata hai.
    """
    print(colored(f"[*] Searching YouTube as fallback for: '{query}'...", "cyan"))
    
    search_query = f"ytsearch{it}:{query}"
    ydl_opts = {
        'format': 'best[ext=mp4]/best', 
        'quiet': True,
        'no_warnings': True,
    }
    
    video_urls = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            
            if 'entries' in info:
                for entry in info['entries']:
                    if entry and entry.get('url'):
                        video_urls.append(entry['url'])
                        print(colored(f"[+] Found YouTube Video: {entry.get('title')[:50]}...", "green"))
            elif info and info.get('url'):
                video_urls.append(info['url'])
                print(colored(f"[+] Found YouTube Video: {info.get('title')[:50]}...", "green"))
                
    except Exception as e:
        print(colored(f"[-] YouTube search failed for '{query}': {e}", "red"))
        
    return video_urls


# =================================================================
# 2. MAIN SEARCH FUNCTION (PEXELS -> YOUTUBE SMART AUTO-SWITCH)
# =================================================================
def search_for_stock_videos(query: str, api_key: str, it: int, min_dur: int) -> List[str]:
    """
    Pehle Pexels par portrait videos dhoondta hai. 
    Agar Pexels par target result na mile, toh AUTO-SWITCH karke YouTube se exact matching video uthata hai.
    """
    
    # Fallback check: Environment variables
    if not api_key:
        api_key = os.getenv("PEXELS_API_KEY") or os.getenv("PEXELS_KEY")

    video_urls = []

    # --- STEP 1: PEXELS TRY KAREIN ---
    if api_key:
        headers = {
            "Authorization": api_key,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        encoded_query = urllib.parse.quote(query.strip())
        qurl = f"https://api.pexels.com/videos/search?query={encoded_query}&per_page={max(it * 3, 15)}&orientation=portrait"

        try:
            print(colored(f"[*] Searching Pexels for: '{query}'...", "cyan"))
            r = requests.get(qurl, headers=headers, timeout=10)

            if r.status_code == 200:
                response = r.json()
                videos_list = response.get("videos", [])

                for v in videos_list:
                    duration = v.get("duration", 0)
                    if duration < min_dur:
                        continue

                    video_files = v.get("video_files", [])
                    temp_video_url = ""
                    best_res = 0

                    for file in video_files:
                        link = file.get("link", "")
                        if ".mp4" in link or ".com" in link:
                            width = file.get("width", 0)
                            height = file.get("height", 0)
                            res = width * height
                            if res > best_res:
                                best_res = res
                                temp_video_url = link

                    if temp_video_url:
                        print(colored(f"[+] Found Pexels Video: {temp_video_url[:60]}...", "green"))
                        video_urls.append(temp_video_url)

                    if len(video_urls) >= it:
                        break
        except Exception as e:
            print(colored(f"[-] Pexels Request failed: {e}", "yellow"))

    # --- STEP 2: YOUTUBE AUTOMATIC SWITCH (Agar Pexels se 0 videos mili) ---
    if not video_urls:
        print(colored(f"[!] No exact matches on Pexels for '{query}'. Auto-switching to YouTube...", "yellow"))
        video_urls = search_youtube_videos(query, it=it)

    print(colored(f"\t=> \"{query}\" successfully fetched {len(video_urls)} videos total", "cyan"))
    return video_urls
