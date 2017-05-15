#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import *
from google.appengine.ext import ndb
import requests
from recommender import *
import pdb;

app = Flask(__name__)

def normalize(arg):
    # Normalize argument. If we query for example Porcupine Tree, the HTTP petition gets done
    # with "Porcupine%20Tree"
    return arg.replace("%20", " ")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/ask-recommendation")
def recommendation():
    return render_template("ask-recommendation.html")

@app.route("/answer-recommendation", methods = ["POST","GET"])
def recommend():
    result = request.form
    recommendations = []

    for key, value in result.iteritems():
        if key != 'name':
            local_recommendations = spotify_handler.spider_of_recommendations(value, 10)
            recommendations = list(set().union(recommendations,local_recommendations))

    return render_template("table.html", recommendations = recommendations)

@app.route("/<group_name>")
def echo(group_name):
    group_name = normalize(group_name)
    result = data_handler.retrieve_data_for(group_name)
    albums = data_handler.get_albums(group_name)
    return render_template("artist.html", result = result,albums = albums)

@app.route("/<group_name>/<album_name>")
def echo3(group_name,album_name):
    album_name = normalize(album_name)
    albums = data_handler.get_album_data(album_name)
    songs = data_handler.get_songs(album_name)
    return render_template("album.html",result = albums, songs= songs)

@app.route("/bdtest2")
def echo2():
    data_handler.get_data_for("gorillaz")
    return("FUNCIONA!!")


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
