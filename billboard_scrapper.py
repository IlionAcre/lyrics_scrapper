import requests
from bs4 import BeautifulSoup

def get_billboard_songs(year:int) -> str:
    """
    Gets the hot 100 songs by year from 2005 to 2023.

    Args:
    year(int): Desired year for the hot 100 songs.

    Returns:
    dict with 100 entries in the form of song_name(key):song_artist(value) sorted by rank order 
    (first entry is top-1 song, last entry the top-100)
    """
    URL = f"https://www.billboard.com/charts/year-end/{year}/hot-100-songs/"
    
    html = requests.get(URL, timeout=(5, 10)).text
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find(class_="chart-results-list")
    titles = table.find_all(class_="c-title")
    fixed_titles = [title.text.strip() for title in titles]
    authors = table.select(".c-label.a-font-primary-s")
    fixed_authors = [author.text.strip() for author in authors]

    songs = {fixed_titles[i]: fixed_authors[i] for i in range(len(titles))}
    return songs