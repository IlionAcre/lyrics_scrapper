import requests
from bs4 import BeautifulSoup
from genius_scrapper import get_lyrics
from models import Artist, Song, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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


db_url = ("sqlite:///songs_data.db")

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = Base

Base.metadata.create_all(engine)

# for song, artist in get_titles(2023).items():
#     with open("lyrics2.txt", "a", encoding='utf-8') as lyrics_file:
#         song_to_search = get_lyrics(song, artist)
#         lyrics_file.write(f"{song} by {artist}")
#         lyrics_file.write(song_to_search)
#         lyrics_file.write("\n\n")
song = "seven"
artist = "jung kook"
lyrics = get_lyrics(song, artist)

try:
    ex_artist = Artist(name=artist)
    session.add(ex_artist)
    ex_song = Song(title=song, artists=[ex_artist], lyrics=lyrics)
    session.add(ex_song)
    session.commit()
except Exception as e:
    print(f"This error xd {e}")
