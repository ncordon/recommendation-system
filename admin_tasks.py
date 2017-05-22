#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import *
from google.appengine.ext import ndb
import requests
from database-tasks import *

app = Flask(__name__)

@app.route("/tasks/database/update")
def database-update():
    msg = 'Tareas de actualización de la base de datos'

    checking = False
    data_handler.create_recommendation("Prueba", ["Prueba", "Prueba"])
    
    ## Añadir aquí la llamada al procedimiento de actualización
    
    if checking:
        response = make_response(msg + ' realizadas correctamente')
    else:
        response = make_response((msg + ' fallidas', 500))

    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
