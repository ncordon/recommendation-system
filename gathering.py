#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Librería para la recolección de datos a través de las API de Spotify y youtube
'''
import spotipy
import spotipy.util as util
import re
import os
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from lxml import html
import requests

class spotifyDataHandler:

    def __init__(self):
        self.client_credentials_manager = SpotifyClientCredentials()
        self.spotyfy = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
        self.spotyfy.trace=False

    '''
    Método para obtener la información de un artista por el nombre.
    '''
    def getArtistByName(self, name, n):
        results = self.spotyfy.search(q = name, limit = n, type = "artist")
        artists = results['artists']['items']
        return artists[0]

    '''
    Método para obtener la información de un album por el nombre.
    '''
    def getAlbumByName(self, name, n):
        results = self.spotyfy.search(q = name, limit = n, type = "album")
        albums = results['album']['items']
        return albums[0]

    '''
    Método para obtener la información de los albumes de un artista por el nombre.
    '''
    def getAlbumsByArtist(self, artist, n):
        albums = []
        results = self.spotyfy.artist_albums(self.getArtistByName(artist, n)['id'],
                                             album_type='album')
        albums.extend(results['items'])
        while results['next']:
            results = self.spotyfy.next(results)
            albums.extend(results['items'])
        albums.sort(key=lambda album:album['name'].lower())
        return albums

    '''
    Método para obtener la información de los caciones de un album.
    '''
    def albumTracks(self, album):
        tracks = []
        results = self.spotyfy.album_tracks(album['id'])
        tracks.extend(results['items'])
        while results['next']:
            results = self.spotyfy.next(results)
            tracks.extend(results['items'])
        return tracks

    '''
    Método para obtener recomendaciones a partir de un artista por el nombre.
    '''
    def recommendationByArtist(self, name, n):
        albums = []
        results = self.spotyfy.recommendations(seed_artists = [self.getArtistByName(name, n)['id']])
        return results

    def categories(self):
        print self.spotyfy.categories()

    '''
    Método para obtener recomendaciones en forma de árbol a partir del nombre de un artista.
    '''
    def spiderOfRecommendations(self, name, li, i, n, limitlen):
        localli = []
        if i == n:
            results = self.recommendationByArtist(name,1)
            for track in results['tracks']:
                if track['artists'][0]['name'] not in li:
                    li.insert(0,track['artists'][0]['name'])
            return
        else:
            results = self.recommendationByArtist(name,1)
            for track in results['tracks']:
                if track['artists'][0]['name'] not in li:
                    li.insert(0,track['artists'][0]['name'])
                    localli.insert(0,track['artists'][0]['name'])
            i += 1
            if limitlen == -1:
                for j in range(len(localli)):
                    self.spiderOfRecommendations(localli[j], li, i, n, limitlen)
            else:
                for j in range(limitlen):
                    self.spiderOfRecommendations(localli[j], li, i, n, limitlen)




class youtubeDataHandler:

    def __init__(self):
        DEVELOPER_KEY = os.environ.get("YOUTUBE_DEV_KEY")
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                             developerKey=DEVELOPER_KEY)

   
    #Metodo para obtener el id de los videos
    def search_channel(self,query,max_results=5):

        search_response = self.youtube.search().list(q=query,part="id",
                                                     maxResults=max_results).execute()

        channels = []
                
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#channel":
                videos.append("%s" % (search_result["id"]["channelId"]))
                
        return channels[0]
            
    
    #Metodo para obtener el id de los videos
    def search_video(self,query,max_results=5):

        search_response = self.youtube.search().list(q=query, part="id,snippet",
                                                         maxResults=max_results).execute()

        videos = []
                
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append("%s" % (search_result["id"]["videoId"]))
                
        return videos[0]
            



class musicbrainzHandler:
    def __init__(self, group_name):
        self.group_name = group_name
        # Calcula el nombre concatenando partes separadas por espacio por un +
        formatted_name="+".join(group_name.split())
        base_page = 'https://musicbrainz.org'
        results_page = requests.get(base_page + '/search?query=' + formatted_name + '&type=artist',
                                    timeout = None)
        # Extrae url del primer resultado al buscar en musicbrainz el nombre del grupo
        base_tree = html.fromstring(results_page.content)
        first_result = base_tree.xpath(
            '//table[@class="tbl"]')[0].xpath('//tbody//tr//td//a')[0].values()[0]
        # artist_url almacena la página del priemr resultado
        self.artist_url = base_page + first_result

        
        # Obtiene el árbol html de la pestaña Overview, Relationships y Tags
        overview_page = requests.get(self.artist_url, timeout = None)
        self.overview = html.fromstring(overview_page.content)
        rel_page = requests.get(self.artist_url + '/relationships', timeout = None)
        self.relationships = html.fromstring(rel_page.content)
        tags_page = requests.get(self.artist_url + '/tags', timeout = None)
        self.tags = html.fromstring(tags_page.content)

        
    """Scrapea la descripción del grupo"""
    def get_description(self):
        description = ""
        try:
            description = self.overview.xpath(
                '//div[@class="wikipedia-extract-body wikipedia-extract-collapse"]'
            )[0].text_content()
        except Exception:
            pass
        
        return description


    def __get_members(self, actual):
        if(actual):
            index = 0
        else:
            index = 1

        member_list = []

        try:
            members = self.relationships.xpath('//table[@class="details"]')[0]
            member_tags = members[index].xpath('td//a//bdi')
            member_list = [ m.text_content() for m in member_tags ]
        except IndexError:
            pass

        return member_list

    
    """Scrapea miembros actuales del grupo"""
    def get_actual_members(self):
        return (self.__get_members(True))

        
    """Scrapea miembros antiguos del grupo"""
    def get_former_members(self):
        return (self.__get_members(False))


    """Scrapea lista de álbumes del grupo"""
    def get_albums(self):
        albums = []

        try:
            albums_tree = self.overview.xpath('//table[@class="tbl release-group-list"]//tbody')
            for category in albums_tree:
                albums += [ (a.getchildren()[0].text_content(), a.getchildren()[1].text_content())
                            for a in category.getchildren() ]
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

    
    
spotify_handler = spotifyDataHandler()
youtube_handler = youtubeDataHandler()

'''
Ejemplos
'''

if __name__ == '__main__':
    data = spotifyDataHandler()
    artist = data.getArtistByName("gorillaz",1)

    #albums = data.getAlbumsByArtist('gorillaz', 2)

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
