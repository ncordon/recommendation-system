#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Librería para la recolección de datos a través de las API de Spotify y youtube
'''

import spotipy
import spotipy.util as util
import re

from spotipy.oauth2 import SpotifyClientCredentials
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser


class spotifyData:

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
        results = self.spotyfy.artist_albums(self.getArtistByName(artist, n)['id'], album_type='album')
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




class youtubeData:

	def __init__(self):
		DEVELOPER_KEY =""
		YOUTUBE_API_SERVICE_NAME = "youtube"
		YOUTUBE_API_VERSION = "v3"
		self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    				developerKey=DEVELOPER_KEY)
		
	#Metodo para obtener el id de los videos y el nombre del canal VEVO
	def youtube_search(self,query,max_results):
  
		search_response = self.youtube.search().list(q=query,part="id,snippet",maxResults=max_results).execute()
		
		videos = []
  		channels = []
  		channel_name = re.compile(r'\b\w+VEVO\b')
 
  		for search_result in search_response.get("items", []):
    			if search_result["id"]["kind"] == "youtube#video":
      				videos.append("%s" % (search_result["id"]["videoId"]))
    			elif search_result["id"]["kind"] == "youtube#channel":
				if channel_name.match(search_result["snippet"]["title"]):
      					channels.append("%s" % (search_result["snippet"]["title"]))
		
		return videos[0]


'''
Ejemplos
'''

if __name__ == '__main__':
    data = spotifyData()
    albums = data.getAlbumsByArtist('gorillaz', 2)

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
    lista = []
    data.spiderOfRecommendations("gorillaz", lista, 1, 2, 3)
    print lista

    yt= youtubeData()
    result = yt.youtube_search("drake",5)
    print result
