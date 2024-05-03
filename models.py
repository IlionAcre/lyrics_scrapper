from sqlalchemy import ForeignKey, Column, String, Integer
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ArtistSong(Base):
    """
    Table for multiple songs and artists many to many relationships
    """
    __tablename__ = "artist_song"
    id = Column(Integer(), primary_key=True)
    artist_id = Column(Integer(), ForeignKey("artists.id"))
    song_id =  Column(Integer(), ForeignKey('songs.id'))


class Song(Base):
    """
    Model for the songs table.

    Args:
    title(str): Name of the song.
    artists(list:Artist): List of artists related to the song.
    lyrics(str): One string containing the lyrics of the song, used for scrapped lyrics.
    b-year(int): The year of the ranking -For billboard yearly ranking purposes-.
    rank(int): The ranking of the song in the given year.
    """
    __tablename__ = "songs"
    id = Column(Integer(), primary_key=True)
    title = Column(String())
    artists = relationship("Artist", secondary="artist_song", back_populates="songs")
    lyrics = Column(String())
    year = Column(Integer())
    rank = Column(Integer())

    def __repr__(self):
        return f"{self.title} by {','.join(self.artists)}"
    
    def get_artists(self):
        """
        No arguments. Returns a list with the names of the artists related to the song.
        """
        return ",".join(self.artists)
    

class Artist(Base):
    """
    Model for the artists table.

    Args:
    name(str): Name of the artist.
    songs(list:Song): List of songs related to the artist.
    """
    __tablename__ = "artists"
    id = Column(Integer(), primary_key=True)
    name = Column(String(), unique=True)
    songs = relationship("Song", secondary="artist_song", back_populates="artists")

    def __repr__(self):
        return f"{self.name}"
    
    def get_songs(self):
        return ([song.title for song in self.songs])
    
    @classmethod
    def get_or_create(cls, session, artist_name:str):
        """
        Retrieve an Artist object from the database or create it if it doesn't exist.

        Args:
        session (Session): SQLAlchemy session object.
        name (str): Name of the artist.

        Returns:
        Artist: The found or created Artist object.
        """
        artist = session.query(cls).filter_by(name=artist_name.lower()).one_or_none()
        if not artist:
            artist = cls(name=artist_name)
            session.add(artist)
            session.commit()
        return artist