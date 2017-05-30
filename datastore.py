#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.api import memcache
from gathering import *
from fuzzywuzzy import fuzz
from datetime import datetime


"""
Borra toda la información en BD para un grupo

Args:
    group_key (ndb.key): key del grupo
"""
def cascade_delete(group_key):
    try:
        album_keys = Album.query( Album.group_key == group_key).fetch(keys_only = True)
        ndb.delete_multi(album_keys + [group_key])
    except Exception:
        pass



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
    Método wrapper para calcular el grupo más similar a
    un grupo desde base de datos

    Args:
        target(str): nombre al que queremos asemejarnos
    """
    def most_similar_group_to(self, target):
        groups = Group.query(projection = ['name'])

        return self.__most_similar_from_to(groups, target)

    """
    Método wrapper para calcular la recomendación más similar
    para el nombre de grupo pasado como argumento

    Args:
        target(str): nombre al que queremos asemejarnos
    """
    def most_similar_recommendation_to(self, target):
        groups = Recommendation.query(projection = ['name'])

        return self.__most_similar_from_to(groups, target)


    """
    Crea un grupo en base de datos con los parámetros pasados

    Return:
        group_key: key del grupo creado
    """
    def create_group(self, name, begin_year, end_year, description, genres, members,
                     area, spotify_url, youtube_channel, tags, img):
        group = Group(name = name, begin_year = begin_year, end_year = end_year,
                      description = description, genres = genres, members = members,
                      area = area, spotify_url = spotify_url,
                      youtube_channel = youtube_channel, tags = tags,img = img)
        group_key = group.put()
        return group_key

    """
    Crea un álbum con los parámetros pasados

    Return:
        album_key: key del álbum creado

    """
    def create_album(self, name, score, year, spotify_url, video_url, group_key, songs):
        album = Album(name = name, score = score, year = year,
                      group_key = group_key, spotify_url = spotify_url,
                      video_url = video_url, songs = songs)
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
        most_similar = self.most_similar_recommendation_to(group_name)

        # Si existe un grupo de nombre lo suficientemente parecido en base de datos
        if most_similar:
            # Se comprueba si esta en la caché
            maybe_cached = u'{}:recommendations'.format(most_similar)
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
                memcache.add(u'{}:recommendations'.format(group_name), current_similar)
                request_queue.put(current_similar)


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
        most_similar = self.most_similar_group_to(group_name)
        needs_update = False

        if most_similar:
            artist = most_similar.key.get()
            needs_update = (datetime.utcnow() - artist.last_update).days >= group_update_freq
        if not most_similar or needs_update:
            group_key = self.get_data_for(group_name)
            artist = group_key.get()
            if needs_update:
                deferred.defer(cascade_delete, most_similar.key)

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
        artist = ((Group.query(Group.name == group_name)).order(-Group.last_update)).get()
        albums = []

        if artist:
          albums = (Album.query(Album.group_key == artist.key)).order(-Album.score)

        return albums


    """
    Obtiene la informacion de un album pasado su nombre como parámetro

    Args:
       album_name (str): nombre del grupo
    Return:
       album
    """
    def get_album(self, group_name, album_name):
        group = Group.query(Group.name == group_name).get()

        if group:
            album = Album.query(Album.group_key == group.key, Album.name == album_name).get()
            if album:
                return album

        raise Exception("El álbum pedido no existe en base de datos")


    """
    Scrapea las canciones para un album pasado como argumento

    Args:
        album (ndb.Album)
        group_name (str): Nombre del grupo
        artist_key (ndb.key): key del grupo en BD
    """
    def __retrieve_album(self, album, group_name, artist_key):
        album_name = to_utf8(album['name'])
        group_name = to_utf8(group_name)
        video_id = youtube_handler.search_video(group_name + " " +
                                                album_name + " " + "full album")

        # Obtiene canciones usando la API de spotify
        tracks = spotify_handler.album_tracks(album['spotify_id'])
        songs = []

        for track in tracks:
            track_name = track["name"].encode("utf-8", "ignore")
            duration = int((track["duration_ms"]/1000))


            songs.append(Song(name = track_name, duration = duration,
                              spotify_url = track["external_urls"]["spotify"],
                              explicit = bool(track["explicit"])))

        self.create_album(album['name'], album['score'], album['year'],
                          album['spotify_url'], video_id, artist_key, songs)

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
        apis_thread = Thread(target = self.__retrieve_from_apis_for,
                             args = [group_name, results])
        apis_thread.start()

        musicbrainz_handler = musicBrainzHandler(group_name)
        description = musicbrainz_handler.get_description()
        members = musicbrainz_handler.get_members()
        members = [GroupMember(name = m[0], begin_year = m[1], end_year = m[2]) for
                   m in members]

        tags = musicbrainz_handler.get_tags()
        active_time = musicbrainz_handler.get_active_time()
        area = musicbrainz_handler.get_area()
        albums = musicbrainz_handler.get_albums()

        begin_year = active_time['begin_year']
        end_year = active_time['end_year']

        # Unimos la hebra de spotify y recojemos sus resultados
        apis_thread.join()
        artist = results['artist']
        spotify_albums = results['albums']
        youtube_channel = results['youtube_channel']

        # Une a los tags el área del grupo
        tags = set(tags) | set([area])

        # Agregamos a los albums los datos de spotify obtenidos desde la API
        for album in albums:
            name = to_utf8(album['name'].lower())
            # Añade la url de spotify y el id del disco
            album['spotify_url'] = None
            album['spotify_id'] = None

            max = 0
            # Intenta hacer match con los datos recuperados desde spotify
            for spotify_album in spotify_albums:
                spotify_name = to_utf8(spotify_album['name'].lower())
                # Si el álbum tiene el mismo título (admitiendo por ejemplo coletillas como
                # -Remastered-
                if fuzz.partial_ratio(spotify_name, name) >= 90:
                    similarity = fuzz.ratio(spotify_name, name)
                    if similarity > max:
                        max = similarity
                        album['spotify_url'] = spotify_album['external_urls']['spotify']
                        album['spotify_id']  = spotify_album['id']

        artist_key = self.create_group(artist['name'], begin_year, end_year,
                                       description, artist['genres'], members,
                                       area, artist['external_urls']['spotify'],
                                       youtube_channel, tags, artist["images"][0]['url'])

        # Scrapeamos los álbumes
        for album in albums:
            self.__retrieve_album(album, group_name, artist_key)

        return artist_key


"""
Modelos de la base de datos
"""
class GroupMember(ndb.Model):
    name = ndb.StringProperty( required = True)
    begin_year = ndb.IntegerProperty()
    end_year = ndb.IntegerProperty()

class Group(ndb.Model):
    name = ndb.StringProperty( required = True )
    begin_year = ndb.IntegerProperty()
    end_year = ndb.IntegerProperty()
    description = ndb.TextProperty()
    genres = ndb.StringProperty( repeated = True )
    members = ndb.StructuredProperty( GroupMember, repeated=True )
    area = ndb.StringProperty()
    spotify_url = ndb.StringProperty()
    youtube_channel = ndb.StringProperty()
    tags = ndb.StringProperty( repeated = True )
    img = ndb.StringProperty()
    last_update = ndb.DateTimeProperty( auto_now = True)

class Recommendation(ndb.Model):
    name = ndb.StringProperty( required = True )
    similar_groups = ndb.StringProperty( repeated = True )
    # auto_now hace que la fecha de creación/actualización se genere sola
    last_update = ndb.DateTimeProperty( auto_now = True)

class Song(ndb.Model):
    name = ndb.StringProperty()
    duration = ndb.IntegerProperty()
    spotify_url = ndb.StringProperty()
    explicit = ndb.BooleanProperty()

class Album(ndb.Model):
    name = ndb.StringProperty( required = True )
    score = ndb.FloatProperty()
    year = ndb.IntegerProperty()
    group_key = ndb.KeyProperty()
    spotify_url = ndb.StringProperty()
    video_url = ndb.StringProperty()
    last_update = ndb.DateTimeProperty( auto_now = True)
    songs = ndb.StructuredProperty( Song, repeated=True )

data_handler = DataStore()
