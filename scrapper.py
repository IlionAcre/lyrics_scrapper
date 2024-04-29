import requests
from bs4 import BeautifulSoup
from genius_scrapper import get_lyrics


def get_titles(year):
    ''' From 2005 to 2023 '''
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

    
for song, artist in get_titles(2025).items():
    with open("lyrics2.txt", "a", encoding='utf-8') as lyrics_file:
        song_to_search = get_lyrics(song, artist)
        lyrics_file.write(f"{song} by {artist}")
        lyrics_file.write(song_to_search)
        lyrics_file.write("\n\n")
