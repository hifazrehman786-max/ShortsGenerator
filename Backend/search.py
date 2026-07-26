import os
import requests
import urllib.parse
from typing import List
from termcolor import colored

def search_for_stock_videos(query: str, api_key: str, it: int, min_dur: int) -> List[str]:
    """
    Searches for portrait/vertical stock videos on Pexels tailored for Shorts/Reels/TikTok.
    Includes smart fallbacks, orientation filtering, and high-quality resolution preference.
    """
    
    # Fallback check: Environment variables se key verify karein
    if not api_key:
        api_key = os.getenv("PEXELS_API_KEY") or os.getenv("PEXELS_KEY")

    if not api_key:
        print(colored("[-] Error: No Pexels API Key found in env or arguments!", "red"))
        return []

    # Headers setup
    headers = {
        "Authorization": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    # Query encode karein taaki spaces/special characters URL break na karein
    encoded_query = urllib.parse.quote(query.strip())
    
    # Pexels API URL with orientation='portrait' filter for YouTube Shorts / Vertical videos
    qurl = f"https://api.pexels.com/videos/search?query={encoded_query}&per_page={max(it * 3, 15)}&orientation=portrait"

    video_urls = []

    try:
        print(colored(f"[*] Searching Pexels for portrait video: '{query}'...", "cyan"))
        r = requests.get(qurl, headers=headers, timeout=10)

        if r.status_code != 200:
            print(colored(f"[-] Pexels API returned status code {r.status_code}", "yellow"))
            # Fallback attempt without portrait constraint if specific term has few vertical videos
            qurl_fallback = f"https://api.pexels.com/videos/search?query={encoded_query}&per_page={it * 2}"
            r = requests.get(qurl_fallback, headers=headers, timeout=10)

        response = r.json()
        videos_list = response.get("videos", [])

        # Process found videos
        for v in videos_list:
            # Duration Check: Ensure video clip meets minimum required length
            duration = v.get("duration", 0)
            if duration < min_dur:
                continue

            video_files = v.get("video_files", [])
            temp_video_url = ""
            best_res = 0

            # Find best resolution download URL (Prefer HD Vertical)
            for file in video_files:
                link = file.get("link", "")
                if ".mp4" in link or ".com" in link:
                    width = file.get("width", 0)
                    height = file.get("height", 0)
                    
                    # Preference given to vertical or high res
                    res = width * height
                    if res > best_res:
                        best_res = res
                        temp_video_url = link

            if temp_video_url:
                print(colored(f"[+] Found Vertical Video: {temp_video_url[:60]}...", "green"))
                video_urls.append(temp_video_url)

            # Desired count achieve hone par loop exit karein
            if len(video_urls) >= it:
                break

    except Exception as e:
        print(colored(f"[-] Request failed for query '{query}': {e}", "red"))

    # Fallback Mechanism: Agar query too specific ho aur 0 videos milen
    if not video_urls and query.lower() != "mobile gaming":
        print(colored(f"[!] No videos found for '{query}'. Trying generic fallback...", "yellow"))
        return search_for_stock_videos("mobile gaming", api_key, it, min_dur)

    print(colored(f"\t=> \"{query}\" successfully fetched {len(video_urls)} portrait videos", "cyan"))
    return video_urls
