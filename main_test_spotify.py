import flask
import spotipy
import spotipy.util as util

from flask import Flask,render_template
app = flask.Flask(__name__)

spotify=spotipy.Spotify()


@app.route("/")
def index():
    result = spotify.search(q="artist:Drake",type="artist")
    print result
    
    name = result['artists']['items'][0]['name']
    uri = result['artists']['items'][0]['uri']

    related = spotify.artist_related_artists(uri)
    print('Related artists for', name)
    for artist in related['artists']:
        print('  ', artist['name'])
        
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug='True')
