#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from recolection import *

class DataStore:
    def create_group(self, name, genre, score, area, begin_year, spotify_url, spotify_followers):
        group = Group(name = name, genre = genre, score = score, begin_year = begin_year, area = area, spotify_url = spotify_url, spotify_followers = spotify_followers)
        group_key = group.put()
        return group_key

    def create_song(self, name, duration, score, album_key):
        song = Song(name = name, duration = duration, score = score, album_key = album_key)
        song_key = song.put()
        return song_key

    def create_album(self, name, genre, score, year, group_key):
        album = Album(name = name, duration = duration, score = score, year = year, group_key = group_key)
        album_key = album.put()
        return album_key

    def integrate_data(self, spotyfy_data, group):
        print "hello"

        #Empezemos obteniendo los datos aportados por spotify de un grupo
        artist = spotyfy_data.getArtistByName(group,1)
        print "hello"
        key = self.create_group(artist["name"], artist["genres"], int(artist["popularity"]), "UNKNOW", 0000, artist["external_urls"]["spotify"], int(artist["followers"]["total"]))
        #Continuamos obteniendo todos los datos posibles de spotify de los albumes asociados al grupo anterior
        '''
        albums = data.getAlbumsByArtist(group, 1)

        for album in albums:
            print album["name"]
            print album["external_urls"]["spotify"]
            tracks = data.albumTracks(album)
            for track in tracks:
                print track
                print track["name"]
                print track["external_urls"]["spotify"]
                print track["explicit"]
                print track["duration_ms"]
        '''



class Group(ndb.Model):
    name = ndb.StringProperty()
    genre = ndb.StringProperty()
    description = ndb.StringProperty()
    score = ndb.IntegerProperty()
    area = ndb.StringProperty()
    begin_year = ndb.IntegerProperty()
    spotify_url = ndb.StringProperty()
    spotify_followers = ndb.IntegerProperty()

def create_entity_using_keyword_arguments():
    sandy = Group(name='Sandy', score=123, genre='HIPHOP')
    sandy.put()

class Album(ndb.Model):
    name = ndb.StringProperty()
    genre = ndb.StringProperty()
    score = ndb.IntegerProperty()
    year = ndb.IntegerProperty()
    group_key = ndb.IntegerProperty()
    spotify_url = ndb.StringProperty()


class Song(ndb.Model):
    name = ndb.StringProperty()
    duration = ndb.FloatProperty()
    score = ndb.IntegerProperty()
    album_key = ndb.IntegerProperty()
    spotify_url = ndb.StringProperty()
    explicit = ndb.BooleanProperty()
