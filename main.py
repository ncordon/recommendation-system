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
from requests_toolbelt.adapters import appengine
appengine.monkeypatch()
from recolection import *

app = Flask(__name__)
data = spotifyData()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/recommendation")
def recommendation():
    return render_template("recommendation.html")

@app.route("/recommend", methods = ["POST","GET"])
def recommend():
    result = request.form
    recommendations = []

    for key, value in result.iteritems():
        if key != 'name':
            localRecommendations = []
            data.spiderOfRecommendations(value, localRecommendations, 1, 2, 2)
            recommendations = list(set().union(recommendations,localRecommendations))
            print localRecommendations

    return render_template("table.html", recommendations = recommendations)

@app.route("/bdtest")
def echo():
    class Account(ndb.Expando):
        pass

    query = Account.query(ndb.GenericProperty('username')=='Sandy')
    return(query.get().email)

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
