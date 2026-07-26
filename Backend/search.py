import os
import requests

from typing import List
from termcolor import colored

def search_for_stock_videos(query: str, api_key: str, it: int, min_dur: int) -> List[str]:
    """
    Searches for stock videos based on a query.

    Args:
        query (str): The query to search for.
        api_key (str): The API key to use.

    Returns:
        List[str]: A list of stock videos.
    """
    
    # Fallback check: Agar main.py se api_key None aaye toh system environment se lein
    if not api_key:
        api_key = os.getenv("PEXELS_API_KEY") or os.getenv("PEXELS_KEY")

    if not api_key:
        print(colored("[-] Error: No Pexels API Key found!", "red"))
        return []

    # Build headers
    headers = {
        "Authorization": api_key
    }

    # Build URL
    qurl = f"https://api.pexels.com/videos/search?query={query}&per_page={it}"

    try:
        # Send the request
        r = requests.get(qurl, headers=headers)

        # log response
        print(colored(f"Response: {r.status_code}", "green"))

        # Parse the JSON response
        response = r.json()

        raw_urls = []
        video_url = []
        
        videos_list = response.get("videos", [])
        
        # Loop safely through returned videos
        for i in range(min(it, len(videos_list))):
            # Check if video has desired minimum duration
            if videos_list[i].get("duration", 0) < min_dur:
                continue
                
            raw_urls = videos_list[i].get("video_files", [])
            temp_video_url = ""
            video_res = 0
            
            # Loop through each url to determine the best quality
            for video in raw_urls:
                # Check if video has a valid download link
                if ".com" in video.get("link", ""):
                    # Only save the URL with the largest resolution
                    current_res = video.get("width", 0) * video.get("height", 0)
                    if current_res > video_res:
                        temp_video_url = video.get("link", "")
                        video_res = current_res
                        
            # Add the url to the return list if it's not empty
            if temp_video_url != "":
                print(colored(f"[+] Found video URL: {temp_video_url}", "green"))
                video_url.append(temp_video_url)

    except Exception as e:
        print(colored("[-] No Videos found or request failed.", "red"))
        print(colored(e, "red"))

    # Let user know
    print(colored(f"\t=> \"{query}\" found {len(video_url)} Videos", "cyan"))

    # Return the video url
    return video_url
