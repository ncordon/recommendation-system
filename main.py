#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import *
from google.appengine.ext import ndb
import requests
from recommender import *

app = Flask(__name__)

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
            local_recommendations = spotify_handler.spiderOfRecommendations(value, 10)
            recommendations = list(set().union(recommendations,local_recommendations))

    return render_template("table.html", recommendations = recommendations)

@app.route("/<group_name>")
def echo(group_name):
    # Normalize group name. If we query for example Porcupine Tree, the HTTP petition gets done
    # with "Porcupine%20Tree"
    group_name = group_name.replace("%20", " ")
    result = data_handler.retrieve_data_for(group_name)
    return render_template("artist.html", result = result)

@app.route("/bdtest2")
def echo2():
    data_handler.get_data_for("gorillaz")
    return("FUNCIONA!!")


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
