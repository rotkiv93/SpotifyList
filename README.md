# SpotifyList

## Pasos previos

Deber crear un .env con las siguientes variables:

```env
SPOTIFY_CLIENT_ID=<SECRET>
SPOTIFY_CLIENT_SECRET=<SECRET>
TEAMS_WEBHOOK_URL=<SECRET>
POLL_API_KEY=<SECRET>
```

## Instalación

```bash
pip install -r requirements.txt
```

## Ejemplo de uso

Para lanzar el mensaje de resumen de la playlist, ejecutar:

```bash
python Resumen.py
```

Para crear la playlist, ejecutar:

```bash
python PollCreator.py
```
