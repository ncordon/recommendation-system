#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from google.appengine.ext import deferred
from gathering import *
from fuzzywuzzy import fuzz
from datetime import datetime

group_update_freq = 5

""" 
Método para convertir strings a utf8 

Args:
   string (str): string a convertir a utf8
"""
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
    Devuelve la key de la recomendación creada
    """
    def create_recommendation(self, name, similar_groups):
        recommendation = Recommendation(name = name, similar_groups = similar_groups)
        recommendation_key = recommendation.put()
        return recommendation_key

    """
    Método para calcular si un resultado es lo suficientemente similar de 
    entre los de una query, respecto a un target

       Comprueba si el valor de 'name' para algún elemento de query es 
       lo suficientemente similar a target, y devuelve el más similar

       Caso de que no haya uno suficientement similar, devuelve None
    """
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
      
    """
    Método paralelizado para obtener recomendaciones a partir de la API de Spotify
    
    Args:
       group_name (str): nombre del grupo para el que calcular la recomendación
       n_recommendations(int): número de recomendaciones a obtener
       request_queue (Queue): cola de peticiones paralelizadas donde escribir el resultado
    """
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



    def __group_needs_update(self, group):
        return (datetime.utcnow() - group.last_update).days >= group_update_freq


    def cascade_delete(self, group_key):
        album_keys = Album.query( Album.group_key == group_key).fetch(keys_only = True)
        song_keys = Song.query( Song.album_key.IN(album_keys) ).fetch(keys_only = True)
        ndb.delete_multi(song_keys + album_keys + [group_key])

      
    
    """
    Devuelve un grupo en caso de que exista en base de datos 
    o se pueda recuperar información de él desde todas las 
    fuentes de datos
       Si existe

    Args:
       group_name (str): nombre del grupo
       
    """
    def retrieve_data_for(self, group_name):
        groups = Group.query(projection = ['name']).iter()
        most_similar = self.__more_similar_from_to(groups, group_name)
        needs_update = False
        
        if most_similar:
            artist = most_similar.key.get()  
            needs_update = self.__group_needs_update(artist)
        if not most_similar or needs_update:     
            group_key = self.get_data_for(group_name)
            artist = group_key.get()
            if needs_update:
                deferred.defer(self.cascade_delete, most_similar.key)
            
        return artist

      
    """
    Devuelve los albums asociados al grupo pasado como argumento.
    Dicho grupo se supone que existe en la base de datos.

    Args:
       group_name (str): nombre del grupo
    Returns:
       albums
    """
    def get_albums(self, group_name):
        artist = (Group.query(Group.name == group_name)).get()
        albums = []

        if artist:
          albums = Album.query(Album.group_key == artist.key)
          
        return albums
        
    
    """
    Obtiene la informacion de un album pasado su nombre como parámetro

    Args:
       album_name (str): nombre del grupo
    
    """
    def get_album_data(self, album_name):
        #query = Album.query(Album.album_key == album_id)
        query = Album.query(Album.name == album_name)
        return query
    
    
    """
    Devuelve las canciones asociados al disco pasado como argumento.
    Dicho album se supone que existe en la base de datos.
    
    Args:
       album_name (str): nombre del grupo

    """
    def get_songs(self, album_name):
        album = Album.query(Album.name == album_name).get()
        songs = []

        if album:
          songs = Song.query(Song.album_key == album.key)
          
        return songs


    """
    Dado un album se introduce en la base de datos.
    Metodo void.
    El album y los argumentos se pasan en el método get_data_for y se suponen existentes.
    """    
    def retrieve_songs_for(self, album, group_name, artist_key):
        album_name = to_utf8(album['name'])
        group_name = to_utf8(group_name)
        video_id = youtube_handler.search_video(group_name + " " +
                                                    album_name + " " + "full album")
        album_key = self.create_album(album_name, "UNKNOWN", 0, 0000,
                                      album["external_urls"]["spotify"],
                                      video_id, artist_key)
        tracks = spotify_handler.album_tracks(album)
        
        for track in tracks:
            track_name = track["name"].encode("utf-8", "ignore")
            self.create_song(track_name, float(track["duration_ms"]), 0,
                                 track["external_urls"]["spotify"], album_key,
                                 bool(track["explicit"]))

    """
    Obtiene datos para el grupo pasado como argumento,
    usando la API de spotify para realizarlo de forma
    paralela a musicbrainz.
    """    
    def retrieve_from_apis_for(self, group_name, results):    
        results['artist'] = spotify_handler.get_artist_by_name(group_name)
        # Obtenemos todos los datos posibles de spotify de los albumes asociados al grupo anterior
        results['albums'] = spotify_handler.get_albums_by_artist(group_name)       
        # Buscamos su canal de youtube
        results['youtube_channel'] = youtube_handler.search_channel(group_name)

       
    """
    Obtiene datos para el grupo pasado como argumento,
    usando las APIs de spotify y youtube y scrapeando
    datos desde musicbrainz
    """
    def get_data_for(self, group_name):
        results = {}
        # Creamos una hebra para que Spotify trabaje en segundo plano mientras scrapeamos
        apis_thread = Thread(target = self.retrieve_from_apis_for, args = [group_name, results])
        apis_thread.start()

        musicbrainz_handler = musicbrainzHandler(group_name)
        description = musicbrainz_handler.get_description()
        actual_members = musicbrainz_handler.get_actual_members()
        former_members = musicbrainz_handler.get_former_members()
        tags = musicbrainz_handler.get_tags()

        # Unimos la hebra de spotify y recojemos sus resultados
        apis_thread.join()
        artist = results['artist']
        albums = results['albums']
        youtube_channel = results['youtube_channel']

        artist_key = self.create_group(artist["name"], description, artist["genres"],
                                       actual_members, former_members,
                                       int(artist["popularity"]), "UNKNOWN", 0000,
                                       artist["external_urls"]["spotify"],
                                       int(artist["followers"]["total"]),
                                       youtube_channel, tags,artist["images"][0]['url'])
        
        # Creamos una hebra por cada album del disco para examinarlos de forma paralela
        threads = []
        
        for i in range(len(albums)):
            threads.append(Thread(target = self.retrieve_songs_for,
                                  args = [albums[i], group_name, artist_key, ]))
            threads[i].start()

        # Esperamos a que terminen todas las hebras
        for thread in threads:
            thread.join()

        return artist_key


""" 
Modelos de la base de datos 
"""
class Group(ndb.Model):
    name = ndb.StringProperty( required = True )
    year = ndb.IntegerProperty()
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
    last_update = ndb.DateTimeProperty( auto_now = True)
    
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
    last_update = ndb.DateTimeProperty( auto_now = True)
    
class Song(ndb.Model):
    name = ndb.StringProperty()
    duration = ndb.FloatProperty()
    score = ndb.IntegerProperty()
    album_key = ndb.KeyProperty()
    spotify_url = ndb.StringProperty()
    explicit = ndb.BooleanProperty()
    last_update = ndb.DateTimeProperty( auto_now = True)

data_handler = DataStore()
