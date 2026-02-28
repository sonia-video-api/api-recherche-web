# API Recherche Web Gratuite

API REST de recherche web gratuite basée sur **DuckDuckGo** et **Wikipedia**. Aucune clé API requise.

## Fonctionnalités

| Endpoint | Description |
|----------|-------------|
| `GET /` | Page d'accueil avec la liste des endpoints |
| `GET /search` | Recherche web générale |
| `GET /news` | Recherche d'actualités |
| `GET /images` | Recherche d'images |
| `GET /wikipedia` | Recherche et résumé Wikipedia |
| `GET /docs` | Documentation interactive (Swagger UI) |

## Installation locale

```bash
# Cloner le repo
git clone https://github.com/VOTRE_NOM/api-recherche-web.git
cd api-recherche-web

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API
uvicorn api:app --host 0.0.0.0 --port 8000
```

L'API sera disponible sur `http://localhost:8000`.

## Exemples d'utilisation

### Recherche web

```
GET /search?q=python+tutorial&max_results=5&region=fr-fr
```

### Actualités

```
GET /news?q=intelligence+artificielle&max_results=5
```

### Images

```
GET /images?q=tour+eiffel&max_results=5
```

### Wikipedia

```
GET /wikipedia?q=Paris&lang=fr
```

## Déploiement sur Render (gratuit)

1. Créez un compte sur [render.com](https://render.com)
2. Connectez votre repo GitHub
3. Créez un **Web Service** avec les paramètres suivants :

| Champ | Valeur |
|-------|--------|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn api:app --host 0.0.0.0 --port $PORT` |
| Plan | Free |

## Utilisation depuis Python

```python
import requests

BASE_URL = "https://votre-api.onrender.com"

# Recherche web
r = requests.get(f"{BASE_URL}/search", params={"q": "python", "max_results": 5})
print(r.json())

# Actualités
r = requests.get(f"{BASE_URL}/news", params={"q": "intelligence artificielle"})
print(r.json())
```

## Utilisation depuis JavaScript

```javascript
// Recherche web
fetch('https://votre-api.onrender.com/search?q=python')
  .then(r => r.json())
  .then(data => console.log(data));
```

## Licence

MIT — Utilisation libre et gratuite.
