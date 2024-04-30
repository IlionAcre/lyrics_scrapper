from playwright.sync_api import sync_playwright
from cachetools import TTLCache
from bs4 import BeautifulSoup
import requests
import logging
import re

logging.basicConfig(level=logging.INFO)
cache = TTLCache(maxsize=100, ttl=3600)

def clean_string(text):
    transformed_text = (text.lower()
                        .replace("-", " ")
                        .replace("with", "and")
                        .replace(" x ", " "))
    
    pattern = r"featuring.*"
    result = re.sub(pattern, '', transformed_text, flags=re.IGNORECASE)
    return result.strip()

def get_lyrics(song, artist):
    """
    Fetches song lyrics using the lyricsgenius library with caching to reduce API calls.
    
    Args:
    song (str): The title of the song.
    artist (str): The name of the artist.

    Returns:
    str: The lyrics of the song or None if not found or on error.
    """
    query_key = f"{song.lower()}_{artist.lower()}"
    
    formatted_song = song.replace(" ","-").replace("'", "").replace(",","").replace(".","").replace("&","and")
    formatted_artist = artist.replace(" ","-").replace("'", "").replace(",","").replace(".","").replace("&","and").replace("with", "and")

    print(f"Getting lyrics from {song} by {artist}")

    if query_key in cache:
        logging.info(f"Cache hit for song: {song} by {artist}")
        return cache[query_key]

    attempts = 0

    while attempts < 3:

        try:
            URL = f"https://genius.com/{formatted_artist}-{formatted_song}-lyrics"
            response = requests.get(URL, timeout=(5, 10))
            response.raise_for_status()
            html = response.text.replace('<br>', '\n').replace('<br/>', '\n')

        except Exception as e:

            if str(response.status_code).startswith('4') or attempts >= 3:
                print("Request failed, trying playwright.")
                playw_attempts = 0

                while playw_attempts < 3:

                    try:
                        with sync_playwright() as p:

                            browser = p.chromium.launch(headless=True)
                            page = browser.new_page()
                            page.set_default_timeout(60000)
                            page.goto("https://genius.com/", wait_until='domcontentloaded')
                            input_selector = 'input.PageHeaderSearchdesktop__Input-eom9vk-2.gajVFV[name="q"][placeholder="Search lyrics & more"][autocomplete="off"]'

                            
                            page.focus(input_selector)
                            page.fill('input[name="q"]', f'{song} {clean_string(artist)}')
                            
                            page.wait_for_selector("#iFrameResizer0")
                            frames = page.frames
                            target_frame = None
                            for frame in frames:
                                if "iFrameResizer0" in frame.name or "iFrameResizer0" in frame.url:
                                    target_frame = frame
                                    break
                            iframe = target_frame

                            iframe.wait_for_selector("mini-song-card a", state="visible", timeout=60000)
                            card = iframe.query_selector("mini-song-card a")
                            if "instrumental" in card.text_content().lower():
                                cards = iframe.query_selector_all('[ng-repeat="hit in $ctrl.results | limitTo: $ctrl.limit_to"] mini-song-card')

                                for current_card in cards:
                                    link = current_card.query_selector('a')
                                    if link:
                                        text_content = link.text_content()
                                    if 'instrumental' not in text_content.lower():
                                        card = current_card
                                        break
                                    else:
                                        card = cards[0]
                            card.click()

                            response = page.inner_html("body")
                            html = response.replace('<br>', '\n').replace('<br/>', '\n')
                            browser.close()
                            break
                        
                    except Exception as e:
                        logging.error(f"Failed to fetch lyrics using playwright: {e}")
                        attempts += 1
                        if attempts == 3:
                            logging.error("Failed on last PW attempt: {e}")
                            return None

            else:
                logging.error(f"Failed to fetch lyrics from Genius: {e}")
                attempts += 1

                if attempts == 3:
                    logging.error(f"Failed on last BS attempt: {e}")
        
        finally:
            if html:
                try:
                    soup = BeautifulSoup(html, "html.parser")
                    lyrics_parts = soup.find_all("div", class_="Lyrics__Container-sc-1ynbvzw-1")
                    lyrics = "\n".join(part.get_text() for part in lyrics_parts if part.get_text().strip())
                    if lyrics:
                        cache[query_key] = lyrics
                        return lyrics
                    else:
                        logging.warning(f"Song '{song}' by '{artist}' not found on Genius.")
                        return None
                except e:
                    logging.error(f"An error has ocurred: {e}")
                    return None
            else:
                logging.error(f"Element was not found: {e}")
                return None