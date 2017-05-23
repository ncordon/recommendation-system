FILE_TO_FIX=./lib/spotipy/oauth2.py

config:
	@echo "############ Descargando librerías en ./lib ############"
	(test -d ./lib && rm -r ./lib) || mkdir ./lib
	pip install -r ./pip_requirements -t ./lib
	@echo "############ Aplicando parche para la librería de spotipy ############"
	sed -i "s/if response.status_code is not 200:/if response.status_code != 200:/" ${FILE_TO_FIX}
	python -m py_compile ${FILE_TO_FIX}
	@echo "############ Excluyendo app.yaml de todos los commits ############"
	git update-index --assume-unchanged app.yaml

mount:
	dev_appserver.py app.yaml

clean:
	dev_appserver.py app.yaml --clear_datastore
