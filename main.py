#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import *
from google.appengine.ext import ndb
import requests
from recommender import *

app = Flask(__name__)

def normalize(arg):
    # Normalize argument. If we query for example Porcupine Tree, the HTTP petition gets done
    # with "Porcupine%20Tree"
    return arg.replace("%20", " ")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/")
def recommendation():
    return render_template("ask-recommendation.html")


@app.route("/answer-recommendation", methods = ["POST","GET"])
def recommend():
    result = request.form
    values = result.values()
    # Elimina strings vacíos de la lista, esto es, artistas no introducidos
    values = filter(None, values)

    if values:
        try:
            recommendations = get_recommendations(values)
            return render_template("table.html", recommendations = recommendations)
        except Exception:
            return render_template("error.html", msg =
                            str("Lo sentimos, no disponemos de datos para esos grupos"))
    else:
        return render_template("ask-recommendation.html")


@app.route("/<group_name>")
def echo_group(group_name):
    group_name = normalize(group_name)

    try:
        artist = data_handler.retrieve_data_for(group_name)
        albums = data_handler.get_albums_by(artist.name)
        return render_template("artist.html", artist = artist, albums = albums)
    except requests.exceptions.RequestException:
        return render_template("error.html", msg =
                               str("Error de conexión, vuelve a intentarlo en un rato"))
    except Exception:
        return render_template("error.html", msg =
                               str("Desafortunadamente no encontramos el grupo que buscas"))


@app.route("/<group_name>/<album_name>")
def echo_album(group_name, album_name):

    try:
        album_name = normalize(album_name)
        album = data_handler.get_album(group_name, album_name)
        songs = data_handler.get_songs(album)
        return render_template("album.html", album = album, songs = songs)
    except Exception:
        return render_template("error.html", msg =
                               str("Lo sentimos, no encontramos el disco que buscas"))


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
