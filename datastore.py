#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from gathering import *
from fuzzywuzzy import fuzz
import pdb

def to_utf8(string):
  return string.encode("utf-8", "ignore")

class DataStore:
    """
    Crea un grupo en base de datos con los parámetros pasados
    Devuelve la key del grupo creado
    """
    def create_group(self, name, description, genre, actual_members, former_members,
                     score, area, begin_year, spotify_url, spotify_followers,
                     youtube_channel, tags, img):
        group = Group(name = name, description = description, genre = genre,
                      actual_members = actual_members, former_members = former_members,
                      score = score, begin_year = begin_year, area = area,
                      spotify_url = spotify_url, spotify_followers = spotify_followers,
                      youtube_channel = youtube_channel, tags = tags,img = img)
        group_key = group.put()
        return group_key

    """
    Crea una canción en base de datos con los parámetros pasados
    Devuelve la key de la canción creada
    """
    def create_song(self, name, duration, score, spotify_url, album_key, explicit):
        song = Song(name = name, duration = duration, score = score,
                    album_key = album_key, spotify_url = spotify_url, explicit = explicit)
        song_key = song.put()
        return song_key

    """
    Crea un álbum con los parámetros pasados
    Devuelve la key del álbum creado
    """
    def create_album(self, name, genre, score, year, spotify_url,video_url,group_key):
        album = Album(name = name, genre = genre, score = score, year = year,
                      group_key = group_key, spotify_url = spotify_url,video_url=video_url)
        album_key = album.put()
        return album_key

    """
    Crea una recomendación en base de datos
    """
    def create_recommendation(self, name, similar_groups):
        recommendation = Recommendation(name = name, similar_groups = similar_groups)
        recommendation_key = recommendation.put()
        return recommendation_key

      
    def __more_similar_from_to(self, query, target):
        max_similarity = 0
        result = None
        
        while query.has_next():
            stored = query.next()
            # Calcula la medida de similaridad con el target
            current_similarity = fuzz.ratio(stored.name.lower(), target.lower())
            
            if current_similarity >= 80 and current_similarity > max_similarity:
                max_similarity = current_similarity
                result = stored

        return result
      

    def thread_retrieve_recommendations(self, group_name, n_recommendations, request_queue):
        groups = Recommendation.query(projection = ['name']).iter()
        
        most_similar = self.__more_similar_from_to(groups, group_name)
        
        # Si existe un grupo de nombre lo suficientemente parecido en base de datos
        if most_similar:
            most_similar = most_similar.key.get() 
            request_queue.put(most_similar.similar_groups)
        else:
            current_similar = spotify_handler.spider_of_recommendations(group_name,
                                                                        n_recommendations)
            if current_similar:
                self.create_recommendation(group_name, current_similar)            
                request_queue.put(current_similar)
        
    
    def retrieve_data_for(self, group_name):
        groups = Group.query(projection = ['name']).iter()
        most_similar = self.__more_similar_from_to(groups, group_name)

        if most_similar:
            artist = most_similar.key.get()
        else:
            group_key = self.get_data_for(group_name)
            artist = group_key.get()
        
        return artist

    """
    Devuelve los albums asociados al grupo pasado como argumento.
    Dicho grupo se supone que existe en la base de datos.
    """
    def get_albums(self, group_name):
        artist = (Group.query(Group.name == group_name)).get()
        albums = []

        if artist:
          albums = Album.query(Album.group_key == artist.key)

        return albums
        
    
    """
    Obtiene la informacion de un album pasado como parámetro
    """
    def get_album_data(self, album_name):
        #query = Album.query(Album.album_key == album_id)
        query = Album.query(Album.name == album_name)
        return query
    
    
    """
    Devuelve las canciones asociados al disco pasado como argumento.
    Dicho album se supone que existe en la base de datos.
    """
    def get_songs(self, album_name):
        album = Album.query(Album.name == album_name).get()
        songs = []

        if album:
          songs = Song.query(Song.album_key == album.key)
          
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
        artist_key = self.create_group(artist["name"], description, artist["genres"],
                                       actual_members, former_members,
                                       int(artist["popularity"]), "UNKNOWN", 0000,
                                       artist["external_urls"]["spotify"],
                                       int(artist["followers"]["total"]),
                                       youtube_channel, tags,artist["images"][0]['url'])
        # Obtenemos todos los datos posibles de spotify de los albumes asociados al grupo anterior
        albums = spotify_handler.get_albums_by_artist(group_name)
        
        
        for album in albums:
            album_name = to_utf8(album['name'])
            group_name = to_utf8(group_name)
            video_id = youtube_handler.search_video(group_name + " " +
                                                    album_name + " " + "full album")
            album_key = self.create_album(album_name, "UNKNOWN", 0, 0000,
                                          album["external_urls"]["spotify"],
                                          video_id, artist_key )
            tracks = spotify_handler.album_tracks(album)
            
            for track in tracks:
                track_name = track["name"].encode("utf-8", "ignore")
                self.create_song(track_name, float(track["duration_ms"]), 0,
                                 track["external_urls"]["spotify"], album_key,
                                 bool(track["explicit"]))

        return artist_key


""" 
Modelos de la base de datos 
"""
class Group(ndb.Model):
    name = ndb.StringProperty( required = True )
    description = ndb.TextProperty()
    genre = ndb.StringProperty( repeated = True )
    actual_members = ndb.StringProperty( repeated = True )
    former_members = ndb.StringProperty( repeated = True )
    score = ndb.IntegerProperty()
    area = ndb.StringProperty()
    begin_year = ndb.IntegerProperty()
    spotify_url = ndb.StringProperty()
    spotify_followers = ndb.IntegerProperty()
    youtube_channel = ndb.StringProperty()
    tags = ndb.StringProperty( repeated = True )
    img = ndb.StringProperty()

class Recommendation(ndb.Model):
    name = ndb.StringProperty( required = True )
    similar_groups = ndb.StringProperty( repeated = True )
    # auto_now hace que la fecha de creación/actualización se genere sola
    last_update = ndb.DateTimeProperty( auto_now = True) 
    
class Album(ndb.Model):
    name = ndb.StringProperty( required = True )
    genre = ndb.StringProperty()
    score = ndb.IntegerProperty()
    year = ndb.IntegerProperty()
    group_key = ndb.KeyProperty()
    spotify_url = ndb.StringProperty()
    video_url = ndb.StringProperty()
    
class Song(ndb.Model):
    name = ndb.StringProperty()
    duration = ndb.FloatProperty()
    score = ndb.IntegerProperty()
    album_key = ndb.KeyProperty()
    spotify_url = ndb.StringProperty()
    explicit = ndb.BooleanProperty()


data_handler = DataStore()
