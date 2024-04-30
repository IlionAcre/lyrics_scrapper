from sqlalchemy import ForeignKey, Column, String, Integer
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ArtistSong(Base):
    __tablename__ = "artist_song"
    id = Column(Integer(), primary_key=True)
    artist_id = Column(Integer(), ForeignKey("artists.id"))
    song_id =  Column(Integer(), ForeignKey('songs.id'))


class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer(), primary_key=True)
    title = Column(String())
    artists = relationship("Artist", secondary="artist_song", back_populates="songs")
    lyrics = Column(String())

    def __repr__(self):
        return f"{self.title} by {self.artists}"
    
    def get_artists(self):
        return ([artist.name for artist in self.artists])
    

class Artist(Base):
    __tablename__ = "artists"
    id = Column(Integer(), primary_key=True)
    name = Column(String())
    songs = relationship("Song", secondary="artist_song", back_populates="artists")

    def __repr__(self):
        return f"{self.name}"
    
    def get_songs(self):
        return ([song.title for song in self.songs])