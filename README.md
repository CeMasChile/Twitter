# Twitter
Repositorio donde se aloja el código para bajar datos de Twitter. Esto se va a hacer con Python y en particular con el paquete ``tweepy``, la documentación se puede encontrar en [este link](http://docs.tweepy.org/en/v3.5.0/index.html).

## Contenido
  * ``twitterGeoLoc.py``: En este archivo se encuentra el Streamer que se encarga de bajar los datos desde Twitter.
  * ``app.py``: Aplicación dash que se encarga se toda la parte de visualización de datos.
  * ``news_and_tweets.py``: Contiene una prueba de cruce de datos recopilados en Twitter con datos recopilados de noticieros nacionales.

## Crear entorno virtual
```sh
cd codigo
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Deployment

```sh
gunicorn app:server -b ip:port
