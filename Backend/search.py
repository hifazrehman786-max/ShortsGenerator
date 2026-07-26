import os
import requests
import urllib.parse
import yt_dlp
from typing import List
from termcolor import colored

# =================================================================
# 1. PIXABAY SEARCH FUNCTION
# =================================================================
def search_pixabay_videos(query: str, api_key: str, it: int, min_dur: int) -> List[str]:
    """
    Pixabay API se vertical stock videos search karta hai.
    """
    if not api_key:
        api_key = os.getenv("PIXABAY_API_KEY")

    if not api_key:
        print(colored("[-] No Pixabay API Key found!", "yellow"))
        return []

    encoded_query = urllib.parse.quote(query.strip())
    qurl = f"https://pixabay.com/api/videos/?key={api_key}&q={encoded_query}&video_type=film&per_page={max(it * 3, 15)}"

    video_urls = []
    try:
        print(colored(f"[*] Searching Pixabay for: '{query}'...", "cyan"))
        r = requests.get(qurl, timeout=10)

        if r.status_code == 200:
            response = r.json()
            hits = response.get("hits", [])

            for hit in hits:
                duration = hit.get("duration", 0)
                if duration < min_dur:
                    continue

                videos = hit.get("videos", {})
                # Preferences: large -> medium -> small
                video_data = videos.get("large") or videos.get("medium") or videos.get("small")
                
                if video_data and video_data.get("url"):
                    link = video_data.get("url")
                    print(colored(f"[+] Found Pixabay Video: {link[:60]}...", "green"))
                    video_urls.append(link)

                if len(video_urls) >= it:
                    break
        else:
            print(colored(f"[-] Pixabay API returned status {r.status_code}", "yellow"))

    except Exception as e:
        print(colored(f"[-] Pixabay Request failed: {e}", "yellow"))

    return video_urls


# =================================================================
# 2. YOUTUBE FALLBACK FUNCTION
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
# 3. MAIN SEARCH FUNCTION (PEXELS -> PIXABAY -> YOUTUBE)
# =================================================================
def search_for_stock_videos(query: str, api_key: str, it: int, min_dur: int) -> List[str]:
    """
    Pehle Pexels try karega -> Phir Pixabay try karega -> Phir YouTube par switch karega.
    """
    
    # Pexels Key fetch
    pexels_key = api_key or os.getenv("PEXELS_API_KEY") or os.getenv("PEXELS_KEY")
    video_urls = []

    # --- STEP 1: PEXELS TRY KAREIN ---
    if pexels_key:
        headers = {
            "Authorization": pexels_key,
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
                    if v.get("duration", 0) < min_dur:
                        continue

                    video_files = v.get("video_files", [])
                    temp_video_url = ""
                    best_res = 0

                    for file in video_files:
                        link = file.get("link", "")
                        if ".mp4" in link or ".com" in link:
                            res = file.get("width", 0) * file.get("height", 0)
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

    # --- STEP 2: PIXABAY TRY KAREIN (Agar Pexels par nahi mili) ---
    if not video_urls:
        print(colored(f"[!] No match on Pexels. Trying Pixabay...", "yellow"))
        pixabay_key = os.getenv("PIXABAY_API_KEY")
        video_urls = search_pixabay_videos(query, pixabay_key, it, min_dur)

    # --- STEP 3: YOUTUBE AUTOMATIC SWITCH (Agar Pexels & Pixabay dono par 0 videos mili) ---
    if not video_urls:
        print(colored(f"[!] No match on Pexels/Pixabay for '{query}'. Auto-switching to YouTube...", "yellow"))
        video_urls = search_youtube_videos(query, it=it)

    print(colored(f"\t=> \"{query}\" successfully fetched {len(video_urls)} videos total", "cyan"))
    return video_urls
