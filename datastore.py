#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.api import memcache
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
    Método para calcular si un resultado es lo suficientemente similar de
    entre los de una query, respecto a un target

       Comprueba si el valor de 'name' para algún elemento de query es
       lo suficientemente similar a target, y devuelve el más similar

       Caso de que no haya uno suficientement similar, devuelve None

    Args:
        query(ndb.query): query tal que los objetos tienen el atributo name
        target(str): nombre al que queremos asemejarnos
    """
    def __most_similar_from_to(self, query, target):
        max_similarity = 0
        result = None
        query = query.iter()

        while query.has_next():
            stored = query.next()
            # Calcula la medida de similaridad con el target
            current_similarity = fuzz.ratio(stored.name.lower(), target.lower())

            if current_similarity >= 80 and current_similarity > max_similarity:
                max_similarity = current_similarity
                result = stored

        return result


    """
    Crea un grupo en base de datos con los parámetros pasados

    Return:
        group_key: key del grupo creado
    """
    def create_group(self, name, begin_year, end_year, description, genre, members, score,
                     area, spotify_url, spotify_followers, youtube_channel, tags, img):
        group = Group(name = name, begin_year = begin_year, end_year = end_year,
                      description = description, genre = genre, members = members,
                      score = score, area = area,
                      spotify_url = spotify_url, spotify_followers = spotify_followers,
                      youtube_channel = youtube_channel, tags = tags,img = img)
        group_key = group.put()
        return group_key

    """
    Crea una canción en base de datos con los parámetros pasados

    Return:
        album_key: key del grupo creado

    """
    def create_song(self, name, duration, score, spotify_url, album_key, explicit):
        song = Song(name = name, duration = duration, score = score,
                    album_key = album_key, spotify_url = spotify_url, explicit = explicit)
        song_key = song.put()
        return song_key

    """
    Crea un álbum con los parámetros pasados

    Return:
        album_key: key del álbum creado

    """
    def create_album(self, name, genre, score, year, spotify_url,video_url,group_key):
        album = Album(name = name, genre = genre, score = score, year = year,
                      group_key = group_key, spotify_url = spotify_url,video_url=video_url)
        album_key = album.put()
        return album_key

    """
    Crea una recomendación en base de datos

    Return:
        recommendation_key: key de la rcomendación creada

    """
    def create_recommendation(self, name, similar_groups):
        recommendation = Recommendation(name = name, similar_groups = similar_groups)
        recommendation_key = recommendation.put()
        return recommendation_key

    """
    Método para obtener recomendaciones a partir de la API de Spotify

    Args:
       group_name (str): grupo para el que recomendar
       n_recommendations(int): número de recomendaciones a obtener
       request_queue (Queue): cola de peticiones paralelizadas donde escribir el resultado
    """
    def retrieve_recommendations(self, group_name, n_recommendations, request_queue):
        groups = Recommendation.query(projection = ['name'])

        most_similar = self.__most_similar_from_to(groups, group_name)

        # Si existe un grupo de nombre lo suficientemente parecido en base de datos
        if most_similar:
            # Se comprueba si esta en la caché
            maybe_cached = '{}:recommendations'.format(most_similar)
            data = memcache.get(maybe_cached)

            if data:
                request_queue.put(data)
            # Si no lo está
            else:
                most_similar = most_similar.key.get()
                # Se mete en caché
                memcache.add(maybe_cached, most_similar.similar_groups)
                request_queue.put(most_similar.similar_groups)
        else:
            # Caso opuesto, se scrapea la información para ellos
            current_similar = spotify_handler.spider_of_recommendations(group_name,
                                                                        n_recommendations)
            if current_similar:
                self.create_recommendation(group_name, current_similar)
                memcache.add('{}:recommendations'.format(group_name), current_similar)
                request_queue.put(current_similar)


    """
    Borra toda la información en BD para un grupo

    Args:
        group_key (ndb.key): key del grupo
    """
    def __cascade_delete(self, group_key):
        album_keys = Album.query( Album.group_key == group_key).fetch(keys_only = True)
        song_keys = Song.query( Song.album_key.IN(album_keys) ).fetch(keys_only = True)
        ndb.delete_multi(song_keys + album_keys + [group_key])



    """
    Devuelve un grupo en caso de que se pueda recuperar información sobre él
       Si existe un grupo similar en base de datos y no necesita actualización,
          Lo devuelve
       Caso opuesto,
          Scrapea o actualiza la información para el grupo
          Si lo ha actualizado,
              Borra el anterior asíncronamente


    Args:
       group_name (str): nombre del grupo

    """
    def retrieve_data_for(self, group_name):
        groups = Group.query(projection = ['name'])
        most_similar = self.__most_similar_from_to(groups, group_name)
        needs_update = False

        if most_similar:
            artist = most_similar.key.get()
            needs_update = (datetime.utcnow() - artist.last_update).days >= group_update_freq
        if not most_similar or needs_update:
            group_key = self.get_data_for(group_name)
            artist = group_key.get()
            if needs_update:
                deferred.defer(self.__cascade_delete, most_similar.key)

        return artist


    """
    Devuelve los albums asociados al grupo pasado como argumento.
    Dicho grupo se supone que existe en la base de datos.

    Args:
        group_name (str): nombre del grupo
    Returns:
        albums
    """
    def get_albums_by(self, group_name):
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
    def get_album(self, album_name):
        album = (Album.query(Album.name == album_name)).get()

        if not album:
            raise NameError

        return album


    """
    Devuelve las canciones asociados al disco pasado como argumento.
    Dicho album se supone que existe en la base de datos.

    Args:
       album (ndb.Album): grupo

    """
    def get_songs(self, album):
        songs = []

        if album:
          songs = Song.query(Song.album_key == album.key)

        return songs


    """
    Scrapea las canciones para un album pasado como argumento

    Args:
        album (ndb.Album)
        group_name (str): Nombre del grupo
        artist_key (ndb.key): key del grupo en BD
    """
    def __retrieve_songs_for(self, album, group_name, artist_key):
        album_name = to_utf8(album['name'])
        group_name = to_utf8(group_name)
        video_id = youtube_handler.search_video(group_name + " " +
                                                    album_name + " " + "full album")
        album_key = self.create_album(album_name, "UNKNOWN", 0, 0000,
                                      album["external_urls"]["spotify"],
                                      video_id, artist_key)
        # Obtiene canciones usando la API de spotify
        tracks = spotify_handler.album_tracks(album)

        # Mete cada una de esas canciones en BD
        for track in tracks:
            track_name = track["name"].encode("utf-8", "ignore")
            self.create_song(track_name, float(track["duration_ms"]), 0,
                                 track["external_urls"]["spotify"], album_key,
                                 bool(track["explicit"]))

    """
    Obtiene datos para el grupo pasado como argumento.

    Args:
        group_name (str): nombre del grupo
        results ({}): diccionario donde guardar los resultados

    """
    def __retrieve_from_apis_for(self, group_name, results):
        results['artist'] = spotify_handler.get_artist_by_name(group_name)
        # Obtenemos todos los datos posibles de spotify de los albumes asociados al grupo anterior
        results['albums'] = spotify_handler.get_albums_by_artist(group_name)
        # Buscamos su canal de youtube
        results['youtube_channel'] = youtube_handler.search_channel(group_name)


    """
    Obtiene datos para el grupo pasado como argumento, y los integra
    Usa las APIs de spotify y youtube y scrapeando datos desde musicbrainz

    Args:
        group_name (str): nombre del grupo para el que obtener datos

    Return:
        artist_key (ndb.Key): key del artista en BD
    """
    def get_data_for(self, group_name):
        results = {}
        # Creamos una hebra para que Spotify trabaje en segundo plano mientras scrapeamos
        apis_thread = Thread(target = self.__retrieve_from_apis_for, args = [group_name, results])
        apis_thread.start()

        musicbrainz_handler = musicBrainzHandler(group_name)
        description = musicbrainz_handler.get_description()
        members = musicbrainz_handler.get_members()
        members = [GroupMember(name = m[0], time_interval = m[1]) for m in members]

        tags = musicbrainz_handler.get_tags()
        active_time = musicbrainz_handler.get_active_time()
        begin_year = active_time['begin_year']
        end_year = active_time['end_year']

        # Unimos la hebra de spotify y recojemos sus resultados
        apis_thread.join()
        artist = results['artist']
        albums = results['albums']
        youtube_channel = results['youtube_channel']

        artist_key = self.create_group(artist["name"], begin_year, end_year,
                                       description, artist["genres"], members,
                                       int(artist["popularity"]), "UNKNOWN",
                                       artist["external_urls"]["spotify"],
                                       int(artist["followers"]["total"]),
                                       youtube_channel, tags,artist["images"][0]['url'])

        # Creamos una hebra por cada album del disco para examinarlos de forma paralela
        threads = []

        for i in range(len(albums)):
            threads.append(Thread(target = self.__retrieve_songs_for,
                                  args = [albums[i], group_name, artist_key, ]))
            threads[i].start()

        # Esperamos a que terminen todas las hebras
        for thread in threads:
            thread.join()

        return artist_key


"""
Modelos de la base de datos
"""
class GroupMember(ndb.Model):
    name = ndb.StringProperty( required = True)
    time_interval = ndb.StringProperty()

class Group(ndb.Model):
    name = ndb.StringProperty( required = True )
    begin_year = ndb.IntegerProperty()
    end_year = ndb.IntegerProperty()
    description = ndb.TextProperty()
    genre = ndb.StringProperty( repeated = True )
    members = ndb.StructuredProperty( GroupMember, repeated=True )
    score = ndb.IntegerProperty()
    area = ndb.StringProperty()
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
