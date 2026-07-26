import re
import json
import g4f
from typing import Tuple, List  
from termcolor import colored
from dotenv import load_dotenv
import os
from google import genai

# Load environment variables
if os.path.exists(".env"):
    load_dotenv(".env")
else:
    load_dotenv("../.env")

# Set environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

# Configure g4f - enable auto update and logging
g4f.version_checking = False
g4f.debug.logging = True

def generate_response(prompt: str, ai_model: str) -> str:
    """
    Generate a script or text response using Gemini or G4F providers.
    """
    model_key = str(ai_model).lower().strip()

    if model_key in ['g4f', 'gpt-4o-mini', 'gpt-4o', 'g4f-gemini']:
        from g4f.client import Client as G4FClient
        from g4f import Provider
        g4f_client = G4FClient(provider=Provider.Gemini)
        response = g4f_client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            web_search=False
        )
        return response.choices[0].message.content

    elif model_key in ['gemini', 'gemmini', 'google', 'gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-2.5-flash']:
        if client is None:
            raise ValueError("GOOGLE_API_KEY not configured in .env file")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        ).text
        return response

    else:
        # Default fallback to gemini-2.5-flash
        if client:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            ).text
            return response
        else:
            from g4f.client import Client as G4FClient
            from g4f import Provider
            g4f_client = G4FClient(provider=Provider.Gemini)
            response = g4f_client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
                web_search=False
            )
            return response.choices[0].message.content


def get_search_terms(video_subject: str, amount: int, script: str, ai_model: str) -> List[str]:
    """
    Generate a JSON-Array of highly visual stock video search terms for Pexels/Pixabay.
    Converts game names and abstract topics into real visual stock scenes.
    """

    prompt = f"""
    # Role: Expert Stock Video Visual Director

    ## Goal:
    Generate exactly {amount} highly visual, generic search queries for stock video platforms like Pexels based on the video context.

    ## CRITICAL RULES FOR STOCK SEARCH:
    1. NEVER use specific game titles, brand names, proper nouns, or abstract terms (e.g. NEVER search 'Free Fire', 'OB54', 'PUBG', 'Mindset', 'Crypto').
    2. Convert topics into REAL VISUAL ACTIONS & SCENES that exist in stock video libraries.
       - Example for Gaming/Free Fire: ["gamer playing mobile game", "esports tournament player", "holding smartphone gaming", "close up smartphone gaming", "gaming controller RGB setup"]
       - Example for Motivation: ["man running sunset", "person reaching mountain top", "focused man working laptop"]
    3. Each search term must be 2 to 3 words max in English.
    4. Return ONLY a valid JSON array of strings. Do not add markdown blocks like ```json, intro, or outro text.

    ## Context:
    Subject: {video_subject}
    Script: {script}

    ## Output Format:
    ["visual scene 1", "visual scene 2", "visual scene 3"]
    """.strip()

    print(colored(f"Generating {amount} visual search terms for '{video_subject}'...", "cyan"))

    response = generate_response(prompt, ai_model)
    print(colored(f"Raw Response: {response}", "cyan"))

    # Cleanup response if wrapped in markdown code blocks
    cleaned_response = response.strip()
    if cleaned_response.startswith("```"):
        cleaned_response = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned_response)
        cleaned_response = re.sub(r"\n?```$", "", cleaned_response).strip()

    search_terms = []
    
    try:
        search_terms = json.loads(cleaned_response)
        if not isinstance(search_terms, list) or not all(isinstance(term, str) for term in search_terms):
            raise ValueError("Response is not a valid list of strings.")

    except (json.JSONDecodeError, ValueError):
        print(colored("[*] Attempting regex extraction for JSON array...", "yellow"))

        match = re.search(r'\[\s*".*?"\s*(?:,\s*".*?"\s*)*\]', response, re.DOTALL)
        if match:
            try:
                search_terms = json.loads(match.group())
            except json.JSONDecodeError:
                print(colored("[-] Failed to parse extracted JSON array.", "red"))
                # Smart fallback depending on topic
                if any(k in video_subject.lower() for k in ['game', 'gaming', 'fire', 'pubg', 'mobile']):
                    return ["gamer playing mobile game", "esports gaming", "holding smartphone gaming", "gaming setup"]
                return ["generic scene", "abstract background", "technology screen"]

    print(colored(f"\nGenerated {len(search_terms)} visual search terms: {', '.join(search_terms)}", "cyan"))
    return search_terms


def generate_metadata(video_subject: str, script: str, ai_model: str) -> Tuple[str, str, List[str], str]:  
    """  
    Generate metadata for YouTube Shorts / Social Media post.
    """  

    title_prompt = f"""  
    You are an expert YouTube Shorts title writer. Generate a single catchy, SEO-optimized title for a video based on the following script.  
    The title must be attention-grabbing, under 60 characters, and directly reflect the content of the script.  
    Return ONLY the title text — no quotes, no explanations, no extra formatting.  

    Video Subject: {video_subject}  

    Script:  
    {script}  
    """  

    title = generate_response(title_prompt, ai_model).strip().strip('"').strip("'")  
    
    description_prompt = f"""  
    You are an expert YouTube Shorts description writer. Write a brief, engaging description for a video based on the following script.  
    The description should include relevant hashtags and be optimized for discovery.  
    Return ONLY the description text — no extra formatting or explanations.  

    Video Subject: {video_subject}  

    Script:  
    {script}  
    """  

    description = generate_response(description_prompt, ai_model).strip()  
    keywords = get_search_terms(video_subject, 5, script, ai_model)  

    post_prompt = f"""  
    You are an expert social media content writer. Write a short, engaging post to promote this video on social platforms like YouTube, TikTok, or Instagram.  
    The post should grab attention, use line breaks, and end with a call to action. Keep it under 280 characters.  
    Return ONLY the post text — no quotes, no formatting.  

    Video Title: {title}  
    Video Subject: {video_subject}  

    Script:  
    {script}  
    """  
    post_content = generate_response(post_prompt, ai_model).strip().strip('"').strip("'")  

    return title, description, keywords, post_content
