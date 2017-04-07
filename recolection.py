#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Librería para la recolección de datos a través de las API de Spotify y youtube
'''

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials


class spotifyData:

    def __init__(self):
        #self.client_credentials_manager = SpotifyClientCredentials()
        #self.spotyfy = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        #self.spotyfy.trace=False
        self.spotyfy = spotipy.Spotify()

    def getArtistByName(self, name, n):
        results = self.spotyfy.search(q = name, limit = n, type = "artist")
        artists = results['artists']['items']
        return artists[0]

    def getAlbumsByArtist(self, artist, n):
        albums = []
        results = self.spotyfy.artist_albums(self.getArtistByName(artist, n)['id'], album_type='album')
        albums.extend(results['items'])
        while results['next']:
            results = self.spotyfy.next(results)
            albums.extend(results['items'])
        albums.sort(key=lambda album:album['name'].lower())
        return albums

    def albumTracks(self, album):
        tracks = []
        results = self.spotyfy.album_tracks(album['id'])
        tracks.extend(results['items'])
        while results['next']:
            results = self.spotyfy.next(results)
            tracks.extend(results['items'])
        return tracks

    def recommendationByArtist(self, name, n):
        albums = []
        results = self.spotyfy.recommendations(seed_artists = [self.getArtistByName(name, n)['id']])
        for track in results['tracks']:
            print track['name'], '-', track['artists'][0]['name']

    def categories(self):
        print self.spotyfy.categories()

    def getTrackByGenre(self, genre, n):
        return

data = spotifyData()
albums = data.getAlbumsByArtist('gorillaz', 2)

data.categories()

for album in albums:
    print "--------------------ALBUM--------------------"
    print album['name']
    tracks = data.albumTracks(album)
    print "--------------------TRACKS--------------------"
    for track in tracks:
        print track['name']
#data.recommendationByArtist("gorillaz", 1)
