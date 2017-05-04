#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from gathering import *

class DataStore:
    """
    Crea un grupo en base de datos con los parámetros pasados
    Devuelve la key del grupo creado
    """
    def create_group(self, name, genre, score, area, begin_year,
                     spotify_url, spotify_followers,youtube_channel):
        group = Group(name = name, genre = genre, score = score,
                      begin_year = begin_year, area = area, spotify_url = spotify_url,
                      spotify_followers = spotify_followers, youtube_channel=youtube_channel)
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
    Obtiene datos para el grupo pasado como argumento,
    usando las APIs de spotify y youtube y scrapeando
    datos desde musicbrainz
    """
    def get_data_for(self, group_name):
        musicbrainz_handler = musicbrainzHandler(group_name)
        # Obtenemos los datos aportados por spotify de un grupo
        artist = spotify_handler.getArtistByName(group_name,1)

        ###################################
        # Esta parte no está funcionando
        #Buscamos su canal de youtube
        youtube_channel=''
        #youtube_channel = youtube_handler.search_channel(artist["name"])
        ###################################
        
        artist_key = self.create_group(artist["name"], str(artist["genres"]),
                                       int(artist["popularity"]), "UNKNOWN", 0000,
                                       artist["external_urls"]["spotify"],
                                       int(artist["followers"]["total"]),youtube_channel)
        #Obtenemos todos los datos posibles de spotify de los albumes asociados al grupo anterior
        albums = spotify_handler.getAlbumsByArtist(group_name, 1)
        description = musicbrainz_handler.get_description()

        
        for album in albums:
            video_id = youtube_handler.search_video(album["name"])
            album_key = self.create_album(str(album["name"]), "UNKNOWN", 0, 0000,
                                        album["external_urls"]["spotify"],video_id,int(artist_key))
            tracks = spotify_handler.albumTracks(album)
            for track in tracks:
                self.create_song(track["name"], float(track["duration_ms"]), 0,
                                 track["external_urls"]["spotify"], int(album_key),
                                 bool(track["explicit"]))

class Group(ndb.Model):
    name = ndb.StringProperty()
    genre = ndb.StringProperty()
    description = ndb.StringProperty()
    members = ndb.JsonProperty()
    former_members = ndb.JsonProperty()
    score = ndb.IntegerProperty()
    area = ndb.StringProperty()
    begin_year = ndb.IntegerProperty()
    spotify_url = ndb.StringProperty()
    spotify_followers = ndb.IntegerProperty()
    youtube_channel = ndb.StringProperty()
    tags = ndb.JsonProperty()
    
class Album(ndb.Model):
    name = ndb.StringProperty()
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
