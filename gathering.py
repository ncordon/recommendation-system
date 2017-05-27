#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Librería para la recolección de datos a través de las API de Spotify y youtube
"""
import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from lxml import html
import requests
from threading import Thread
import Queue
import re
from dateutil import parser



class spotifyDataHandler:

    def __init__(self):
        self.client_credentials_manager = SpotifyClientCredentials()
        self.spotify = spotipy.Spotify(client_credentials_manager = self.client_credentials_manager)
        self.spotify.trace = False

    '''
    Método para obtener la información de un artista por el nombre.
    '''
    def get_artist_by_name(self, name):
        results = self.spotify.search(q = name, limit = 1, type = "artist")
        artist = {}

        try:
            artist = results['artists']['items'][0]
        except Exception:
            pass

        return artist

    '''
    Método para obtener la información de un album por el nombre.
    '''
    def get_album_by_name(self, name):
        results = self.spotify.search(q = name, limit = 1, type = "album")
        album = {}

        try:
            album = results['albums']['items'][0]
        except Exception:
            pass

        return album

    '''
    Método para obtener la información de los albumes de un artista por el nombre.
    '''
    def get_albums_by_artist(self, artist):
        albums = []

        try:
            results = self.spotify.artist_albums(self.get_artist_by_name(artist)['id'],
                                                 album_type = 'album', country = 'ES')
            albums.extend(results['items'])

            while results['next']:
                results = self.spotify.next(results)
                albums.extend(results['items'])

            albums = self.remove_repeated_albums(albums)
            albums.sort(key=lambda album:album['name'].lower())
        except Exception:
            pass

        return albums

    '''
    Método para obtener la información de los caciones de un album.
    '''
    def album_tracks(self, album_id):
        tracks = []

        try:
            results = self.spotify.album_tracks(album_id)
            tracks.extend(results['items'])

            while results['next']:
                results = self.spotify.next(results)
                tracks.extend(results['items'])
        except Exception:
            pass

        return tracks

    '''
    Método para obtener recomendaciones a partir de un artista por el nombre.
    '''
    def recommendation_by_artist(self, name):
        results = []

        try:
            results = self.spotify.recommendations(seed_artists =
                                                   [self.get_artist_by_name(name)['id']])
        except Exception:
            pass

        return results


    '''
    Método para obtener recomendaciones en forma de árbol a partir del nombre de un artista.
    '''
    def spider_of_recommendations(self, name, limitlen):
        result = []
        recommend_queue = Queue.Queue()
        recommend_queue.put(name)
        finished = False

        while len(result) < limitlen and not finished and recommend_queue:
            recommended = self.recommendation_by_artist( recommend_queue.get() )

            if recommended:
                recommended = set([track['artists'][0]['name'] for track in recommended['tracks']])
                recommended = recommended - set(result)
                recommended = recommended - {name}
                result += list(recommended)

                for group in recommended:
                    recommend_queue.put(group)
            else:
                finished = True

        result = result[:limitlen]
        return result

    '''
    Método para eliminar los albumes duplicados

    Args:
        albums : lista de albumes
    '''
    def remove_repeated_albums(self,albums):
        result = []
        albums_dic = {}

        #Para eliminar los elementos repetidos usamos un diccionario
        for album in albums:
            albums_dic[album['name']] = album

        #Se crea una lista con los elementos del diccionario
        for name,album in albums_dic.items() :
            result.append(album)

        return result

class youtubeDataHandler:

    def __init__(self):
        DEVELOPER_KEY = os.environ.get("YOUTUBE_DEV_KEY")
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                             developerKey = DEVELOPER_KEY)


    '''Metodo para obtener el id de los videos'''
    def search_channel(self, query):
        search_response = self.youtube.search().list(q = query, part = "id", type = "channel",
                                                     maxResults = 1).execute()

        channel_url = "Not Found"

        try:
            channel_id = search_response["items"][0]["id"]["channelId"]
            channel_url = "https://www.youtube.com/channel/" + channel_id
        except Exception:
            pass

        return channel_url

    '''Metodo para obtener el id de los videos'''
    def search_video(self, query):
        search_response = self.youtube.search().list(q = query, part = "id,snippet").execute()
        video_url = "Not Found"

        try:
            id_video = search_response["items"][0]["id"]

            if id_video["kind"] == "youtube#video":
                video_url = "https://www.youtube.com/embed/" + id_video["videoId"]
            else:
                if id_video["kind"] == "youtube#playlist":
                    video_url = "https://www.youtube.com/embed/?list=" + id_video["playlistId"]
        except Exception:
            pass

        return video_url





class musicBrainzHandler:
    def __init__(self, group_name):
        self.group_name = group_name
        self.search_result = None
        # Calcula el nombre concatenando partes separadas por espacio por un +
        formatted_name="+".join(self.group_name.split())
        base_page = 'https://musicbrainz.org'
        search_url = base_page + '/search?query=' + formatted_name + '&type=artist&method=indexed'
        results_page = requests.get(search_url, timeout = None)
        # Extrae url del primer resultado al buscar en musicbrainz el nombre del grupo
        base_tree = html.fromstring(results_page.content)
        self.search_result = base_tree.xpath('//table[@class="tbl"]')[0].xpath('//tbody')
        group_id = self.search_result[0].xpath('//tr[1]//td//a')[0].values()[0]
        # artist_url almacena la página del priemr resultado
        self.artist_url = base_page + group_id
        self.__fetch_data()


    def __fetch_description(self):
        wiki_page = requests.get(self.artist_url + '/wikipedia-extract', timeout = None)
        self.wiki_extract = html.fromstring(wiki_page.content)


    def __fetch_data(self):
        wiki_thread = Thread(target = self.__fetch_description)
        wiki_thread.start()

        overview_page = requests.get(self.artist_url, timeout = None)
        self.overview = html.fromstring(overview_page.content)
        rel_page = requests.get(self.artist_url + '/relationships', timeout = None)
        self.relationships = html.fromstring(rel_page.content)
        # Obtiene el árbol html de la pestaña Overview, Relationships y Tags
        tags_page = requests.get(self.artist_url + '/tags', timeout = None)
        self.tags = html.fromstring(tags_page.content)
        wiki_thread.join()

    """Scrapea la descripción del grupo"""
    def get_description(self):
        description = ""
        try:
            description = self.wiki_extract.xpath(
                '//div[@class="wikipedia-extract-body wikipedia-extract-collapse"]'
            )[0].text_content()
        except Exception:
            pass

        return description.encode("ISO-8859-1", "ignore").decode('utf8')

    """Scrapea el área del grupo"""
    def get_area(self):
        area = ''
        try:
            if self.search_result:
                results = self.search_result[0].xpath('//tr[1]//td[6]//text()')
                area = results[0].strip("[] \n")
        except Exception:
            pass


        return area

    """Scrapea miembros actuales del grupo"""
    def get_members(self):
        member_names = []
        member_years = []

        try:
            members = self.relationships.xpath(
                '//table[@class="details" and (.//th="members:" or .//th="original members:")]')

            if members:
                member_names = members[0].xpath('.//a[@title]//bdi//text()')
                member_info = members[0].xpath(
                   './/*[not(self::th)]//text()[following::br]')
                member_info = filter(None, [ x.strip("[] \n") for x in member_info])
                member_years = ['' for m in member_names]

                len_names = len(member_names)

                i = 0
                for j in range(len(member_info)):
                    if i < len_names and member_info[j] == member_names[i]:
                        i+=1
                    else:
                        if u'\u2013' in member_info[j]:
                            time_interval = member_info[j]
                            regex_result = re.search(r"\((\d*)(.*)(\d*)\)", time_interval)
                            if regex_result:
                                time_interval = regex_result.group(0)
                                member_years[i-1] = time_interval
        except Exception:
            pass


        return zip(member_names, member_years)


    """Scrapea lista de álbumes del grupo"""
    def get_albums(self):
        albums = []

        try:
            albums_tree = self.overview.xpath('//table[@class="tbl release-group-list"]//tbody')
            names_so_far = []

            for category in albums_tree:
                album_table = category.getchildren()

                for a in album_table:
                    name = a.xpath('.//td[2]//bdi//text()')[0]
                    if not (name in names_so_far):
                        names_so_far += [name]
                        score = a.xpath('.//span[@class="current-rating"]//text()')
                        year = a.xpath('.//td[1]//text()')

                        if year:
                            year = re.search(r"\d*", year[0])
                            year = int(year.group(0))

                        else:
                            year = None

                        if score:
                            score = float(score[0])
                        else:
                            score = 0

                        albums += [{'name': name, 'year': year, 'score': score}]

        except Exception:
            pass

        return albums


    """Scrapea tags para el grupo"""
    def get_tags(self):
        tags = []

        try:
            tags = [ t[0][0].text_content() for t in
                     self.tags.xpath('//div[@id="all-tags"]')[0][0].getchildren() ]
        except Exception:
            pass

        return tags

    """Scrapea los años activos del grupo (comienzo-fin)"""
    def get_active_time(self):
        time = {'begin_year':None, 'end_year':None}
        try:
            if self.search_result:
                begin = self.search_result[0].xpath('//tr[1]//td[7]//text()')
                end = self.search_result[0].xpath('//tr[1]//td[9]//text()')
                begin = begin[0].strip("[] \n")
                end = end[0].strip("[] \n")
                if begin:
                    time['begin_year'] = int(parser.parse(begin).year)
                if end:
                    time['end_year'] = int(parser.parse(end).year)
        except Exception:
            pass


        return time

spotify_handler = spotifyDataHandler()
youtube_handler = youtubeDataHandler()

'''
Ejemplos
'''

if __name__ == '__main__':
    data = spotifyDataHandler()
    artist = data.get_artist_by_name("gorillaz",1)

    #albums = data.get_albums_by_artist('gorillaz', 2)

    #data.categories()

    '''for album in albums:
        print "--------------------ALBUM--------------------"
        print album['name']
        tracks = data.albumTracks(album)
        print "--------------------TRACKS--------------------"
        for track in tracks:
            print track['name']
            '''
    #print()
    '''
    results = data.recommendationByArtist("gorillaz", 1)
    for track in results['tracks']:
        print track['artists'][0]['name']
    print "--------------------2--------------------"
    results = data.recommendationByArtist("Daft Punk", 1)
    for track in results['tracks']:
        print track['artists'][0]['name']
        '''
    #lista = []
    #data.spiderOfRecommendations("gorillaz", lista, 1, 2, 3)
    #print lista

    '''
    yt= youtubeData()
    result = yt.youtube_search("drake",5)
    print result
    '''
