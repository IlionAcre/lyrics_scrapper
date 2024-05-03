from billboard_scrapper import get_billboard_songs
from genius_scrapper import get_lyrics
from models import Artist, Song, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_url = ("sqlite:///songs_data.db")

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = Base

"""

The Section bellow was used to scrap the titles, artists and lyrics of the top 100 songs by year since 2025 to 2023.

Information stored in songs_data.db

"""

Base.metadata.create_all(engine)

for year in range(2005, 2024):
    rank_tracker = 1
    for song, artist in get_billboard_songs(year).items():
        
        try:
            artist_list = (artist.lower()
                           .replace(" x ", ",")
                           .replace("&", ",")
                           .replace("featuring",",")
                           .replace(" ft. ", ",")
                           .replace(" ft ", ",")
                           .replace(" ,", "")
                           .replace(", ", "")
                           .split(","))


            new_artists = [Artist.get_or_create(session=session, artist_name=new_artist) for new_artist in artist_list] 
            #The function adds the artist to the DB if it was not there, so no need to add and commit for new artist.
            new_song = Song(title=song, artists=new_artists, lyrics=get_lyrics(song, artist), year=year, rank=rank_tracker)
            session.add(new_song)
            session.commit()
        except Exception as e:
            print(f"An error has ocurred: {e}")
        finally:
            rank_tracker += 1