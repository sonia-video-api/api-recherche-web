from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os

# Import DDGS (DuckDuckGo Search)
try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

app = FastAPI(
    title="API Recherche Web Gratuite",
    description=(
        "API de recherche web gratuite utilisant DuckDuckGo (texte, actualites, images) "
        "et Wikipedia comme source supplementaire. Aucune cle API requise."
    ),
    version="2.0.0"
)

# Autoriser tout le monde (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchResult(BaseModel):
    title: str
    url: str
    content: Optional[str] = None
    source: str


class NewsResult(BaseModel):
    title: str
    url: str
    body: Optional[str] = None
    date: Optional[str] = None
    source: Optional[str] = None


class ImageResult(BaseModel):
    title: str
    url: str
    image_url: str
    thumbnail: Optional[str] = None
    source: Optional[str] = None


@app.get("/")
def accueil():
    return {
        "message": "API Recherche Web Gratuite en ligne !",
        "version": "2.0.0",
        "moteur": "DuckDuckGo + Wikipedia",
        "endpoints": {
            "/search": "Recherche web generale  (?q=...&max_results=10&region=fr-fr)",
            "/news": "Recherche d'actualites     (?q=...&max_results=10)",
            "/images": "Recherche d'images        (?q=...&max_results=10)",
            "/wikipedia": "Recherche Wikipedia       (?q=...&lang=fr)",
        },
        "exemples": [
            "/search?q=python+tutorial",
            "/news?q=intelligence+artificielle",
            "/images?q=tour+eiffel",
            "/wikipedia?q=Paris&lang=fr",
        ],
        "documentation": "/docs",
    }


@app.get("/search", response_model=dict)
def recherche_web(
    q: str = Query(..., description="Terme a rechercher"),
    max_results: int = Query(10, ge=1, le=50, description="Nombre maximum de resultats"),
    region: str = Query("fr-fr", description="Region (ex: fr-fr, en-us, wt-wt)"),
):
    """
    Recherche web generale via DuckDuckGo.
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Parametre 'q' requis et non vide.")

    if not DDGS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Moteur de recherche non disponible.")

    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(q.strip(), max_results=max_results, region=region))

        results = [
            SearchResult(
                title=item.get("title", "Sans titre"),
                url=item.get("href", ""),
                content=item.get("body", ""),
                source="DuckDuckGo",
            )
            for item in raw
        ]

        return {
            "query": q,
            "region": region,
            "count": len(results),
            "results": [r.model_dump() for r in results],
        }

    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Erreur lors de la recherche : {str(exc)}")


@app.get("/news", response_model=dict)
def recherche_actualites(
    q: str = Query(..., description="Terme a rechercher"),
    max_results: int = Query(10, ge=1, le=50, description="Nombre maximum de resultats"),
    region: str = Query("fr-fr", description="Region (ex: fr-fr, en-us)"),
):
    """
    Recherche d'actualites via DuckDuckGo News.
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Parametre 'q' requis et non vide.")

    if not DDGS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Moteur de recherche non disponible.")

    try:
        with DDGS() as ddgs:
            raw = list(ddgs.news(q.strip(), max_results=max_results, region=region))

        results = [
            NewsResult(
                title=item.get("title", "Sans titre"),
                url=item.get("url", ""),
                body=item.get("body", ""),
                date=item.get("date", ""),
                source=item.get("source", ""),
            )
            for item in raw
        ]

        return {
            "query": q,
            "region": region,
            "count": len(results),
            "results": [r.model_dump() for r in results],
        }

    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Erreur lors de la recherche : {str(exc)}")


@app.get("/images", response_model=dict)
def recherche_images(
    q: str = Query(..., description="Terme a rechercher"),
    max_results: int = Query(10, ge=1, le=50, description="Nombre maximum de resultats"),
    region: str = Query("fr-fr", description="Region (ex: fr-fr, en-us)"),
):
    """
    Recherche d'images via DuckDuckGo Images.
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Parametre 'q' requis et non vide.")

    if not DDGS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Moteur de recherche non disponible.")

    try:
        with DDGS() as ddgs:
            raw = list(ddgs.images(q.strip(), max_results=max_results, region=region))

        results = [
            ImageResult(
                title=item.get("title", "Sans titre"),
                url=item.get("url", ""),
                image_url=item.get("image", ""),
                thumbnail=item.get("thumbnail", ""),
                source=item.get("source", ""),
            )
            for item in raw
        ]

        return {
            "query": q,
            "region": region,
            "count": len(results),
            "results": [r.model_dump() for r in results],
        }

    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Erreur lors de la recherche : {str(exc)}")


@app.get("/wikipedia", response_model=dict)
async def recherche_wikipedia(
    q: str = Query(..., description="Terme a rechercher sur Wikipedia"),
    lang: str = Query("fr", description="Langue Wikipedia (fr, en, de, es, ...)"),
):
    """
    Recherche et resume Wikipedia via l'API officielle gratuite.
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Parametre 'q' requis et non vide.")

    try:
        search_url = f"https://{lang}.wikipedia.org/w/api.php"
        params_search = {
            "action": "query",
            "list": "search",
            "srsearch": q.strip(),
            "format": "json",
            "srlimit": 5,
        }

        headers = {"User-Agent": "SearchAPI/2.0 (https://github.com/api-recherche)"}
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(search_url, params=params_search)
            resp.raise_for_status()
            data = resp.json()

        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            return {"query": q, "lang": lang, "count": 0, "results": []}

        # Recuperer le resume du premier article
        top_title = search_results[0]["title"]
        params_summary = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": top_title,
            "format": "json",
        }

        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp2 = await client.get(search_url, params=params_summary)
            resp2.raise_for_status()
            data2 = resp2.json()

        pages = data2.get("query", {}).get("pages", {})
        page = next(iter(pages.values()), {})
        extract = page.get("extract", "")[:1000]  # Limiter a 1000 caracteres

        results = [
            {
                "title": item["title"],
                "url": f"https://{lang}.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
                "snippet": item.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
                "wordcount": item.get("wordcount", 0),
            }
            for item in search_results
        ]

        return {
            "query": q,
            "lang": lang,
            "count": len(results),
            "top_article": {
                "title": top_title,
                "url": f"https://{lang}.wikipedia.org/wiki/{top_title.replace(' ', '_')}",
                "extract": extract,
            },
            "results": results,
        }

    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Erreur Wikipedia : {str(exc)}")


# Point d'entree pour Render (variable PORT) ou local
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
