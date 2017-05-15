#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from gathering import *

class DataStore:
    """
    Crea un grupo en base de datos con los parámetros pasados
    Devuelve la key del grupo creado
    """
    def create_group(self, name, description, genre, actual_members, former_members,
                     score, area, begin_year, spotify_url, spotify_followers,
                     youtube_channel, tags,img):
        group = Group(name = name, description = description, genre = genre,
                      actual_members = actual_members, former_members = former_members,
                      score = score, begin_year = begin_year, area = area,
                      spotify_url = spotify_url, spotify_followers = spotify_followers,
                      youtube_channel = youtube_channel, tags = tags,img = img)
        group_key = group.put()
        return group_key.id()

    """
    Crea una canción en base de datos con los parámetros pasados
    Devuelve la key de la canción creada
    """
    def create_song(self, name, duration, score, spotify_url, album_key, explicit):
        song = Song(name = name, duration = duration, score = score,
                    album_key = album_key, spotify_url = spotify_url, explicit = explicit)
        song_key = song.put()
        return song_key.id()

    """
    Crea un álbum con los parámetros pasados
    Devuelve la key del álbum creado
    """
    def create_album(self, name, genre, score, year, spotify_url,video_url,group_key):
        album = Album(name = name, genre = genre, score = score, year = year,
                      group_key = group_key, spotify_url = spotify_url,video_url=video_url)
        album_key = album.put()
        return album_key.id()


    """
    Devuelve datos para el grupo pasado como argumento.
    Si no existe en base de datos, lo crea con get_data_for 
    y lo devuelve
    """
    def retrieve_data_for(self, group_name):
        query = Group.query(Group.name == group_name)
        if query.count() == 0:
            key = self.get_data_for(group_name)
            query = Group.query(Group.name == group_name)
        

        return query
    
    """
    Devuelve los albums asociados al grupo pasado como argumento.
    Dicho grupo se supone que existe en la base de datos.
    """
    def get_albums(self,group_name):
        query = Group.query(Group.name == group_name)
        for artist in query:
            albums = Album.query(Album.group_key == artist.key.id())
        return albums
        
    
    """
    Obtiene la informacion de un album pasado como parámetro
    """
    def get_album_data(self,album_id):
        #query = Album.query(Album.album_key == album_id)
        query = Album.query(Album.name == album_id)
        return query
    
    
    """
    Devuelve las canciones asociados al disco pasado como argumento.
    Dicho album se supone que existe en la base de datos.
    """
    def get_songs(self,album_id):
        #query = Album.query(Album.album_key == album_id)
        query = Album.query(Album.name == album_id)
        for album in query:
            songs = Song.query(Song.album_key == album.key.id())
        return songs
        
    
    
    
    
    """
    Obtiene datos para el grupo pasado como argumento,
    usando las APIs de spotify y youtube y scrapeando
    datos desde musicbrainz
    """
    def get_data_for(self, group_name):
        musicbrainz_handler = musicbrainzHandler(group_name)
        # Obtenemos los datos aportados por spotify de un grupo
        artist = spotify_handler.get_artist_by_name(group_name)
    
        ###################################
        # Buscamos su canal de youtube
        youtube_channel= youtube_handler.search_channel(group_name)
        ###################################

        description = musicbrainz_handler.get_description()
        actual_members = musicbrainz_handler.get_actual_members()
        former_members = musicbrainz_handler.get_former_members()
        tags = musicbrainz_handler.get_tags()
        
        artist_key = self.create_group(artist["name"], description, str(artist["genres"]),
                                       actual_members, former_members,
                                       int(artist["popularity"]), "UNKNOWN", 0000,
                                       artist["external_urls"]["spotify"],
                                       int(artist["followers"]["total"]),
                                       youtube_channel, tags,artist["images"][0]['url'])
        # Obtenemos todos los datos posibles de spotify de los albumes asociados al grupo anterior
        albums = spotify_handler.get_albums_by_artist(group_name)
        
        
        for album in albums:
            album_name = album['name'].encode("utf-8", "ignore")
            video_id = youtube_handler.search_video(group_name + " " +
                                                    album_name + " " + "full album")
            album_key = self.create_album(album_name, "UNKNOWN", 0, 0000,
                                          album["external_urls"]["spotify"],
                                          video_id, int(artist_key))
            tracks = spotify_handler.album_tracks(album)
            for track in tracks:
                track_name = track["name"].encode("utf-8", "ignore")
                self.create_song(track_name, float(track["duration_ms"]), 0,
                                 track["external_urls"]["spotify"], int(album_key),
                                 bool(track["explicit"]))

        
        

class Group(ndb.Model):
    name = ndb.StringProperty( required = True )
    description = ndb.TextProperty()
    genre = ndb.StringProperty()
    actual_members = ndb.StringProperty( repeated = True )
    former_members = ndb.StringProperty( repeated = True )
    score = ndb.IntegerProperty()
    area = ndb.StringProperty()
    begin_year = ndb.IntegerProperty()
    spotify_url = ndb.StringProperty()
    spotify_followers = ndb.IntegerProperty()
    youtube_channel = ndb.StringProperty()
    similar_groups = ndb.KeyProperty( repeated = True, indexed = True )
    tags = ndb.StringProperty( repeated = True )
    img = ndb.StringProperty()
    
class Album(ndb.Model):
    name = ndb.StringProperty( required = True )
    genre = ndb.StringProperty()
    score = ndb.IntegerProperty()
    year = ndb.IntegerProperty()
    group_key = ndb.IntegerProperty()
    spotify_url = ndb.StringProperty()
    video_url = ndb.StringProperty()
    
class Song(ndb.Model):
    name = ndb.StringProperty()
    duration = ndb.FloatProperty()
    score = ndb.IntegerProperty()
    album_key = ndb.IntegerProperty()
    spotify_url = ndb.StringProperty()
    explicit = ndb.BooleanProperty()


data_handler = DataStore()
