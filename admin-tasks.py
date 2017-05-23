#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import *
from google.appengine.ext import ndb
import requests
from database_tasks import *

app = Flask(__name__)

@app.route("/tasks/database/update")
def database_update():
    msg = 'Tareas de actualización de la base de datos'
    admin_update_proc() 
    
    ## Añadir aquí la llamada al procedimiento de actualización
    
    try:
        response = make_response(msg + ' realizadas correctamente')
    except Exception:
        response = make_response((msg + ' fallidas', 500))

    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
