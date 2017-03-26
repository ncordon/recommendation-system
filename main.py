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
# Things to manage database
from config import *
import pymongo
from pprint import pprint

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/bdtest")
def echo():
    client = pymongo.MongoClient(MONGO_URI)
    db = client.get_default_database()
    grupos_db = db['grupos']

    #Dato = {'name': 'Porcupine Tree', 'album': 'Voyage 34', 'origin': 'GB'}
    #grupos.db.insert(Dato)
    query = grupos_db.find({'name':'Porcupine Tree'})

    return(str(query[0]))

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)

