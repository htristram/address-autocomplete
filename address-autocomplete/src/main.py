from typing import Union
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from address_parser import AddressParser
from urllib.parse import unquote_plus
import sys
from loguru import logger
from config import ServiceConfig, LogLevel
import meilisearch

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mini_len_for_parse = 4
config = ServiceConfig()

logger.info(f"Connexion index {config.meilisearch_index} sur {config.meilisearch_url}")
client = meilisearch.Client(config.meilisearch_url, config.meilisearch_key)
# An index is where the documents are stored.
index = client.index(config.meilisearch_index)

logger.remove()  # Supprimer le handler par défaut
logger.add(
    sink=sys.stderr,
    level=config.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/address/autocomplete")
async def autocomplete_search(
    q: str,  # terme de recherche
    limit: int = 20,  # nombre de résultats
    country: str = 'FRA'  # Pays
):
    request = unquote_plus(q)
    
    parser = AddressParser()
    filter_search = ""
    try:
        if len(request) >= mini_len_for_parse:
            parser.parse(request)
            request = parser.get_address()
            if config.log_level == LogLevel.DEBUG:
                parser.print_analyse()
                parser.print_choice()

            filter = [] 
            """ si on trouve un truc qui commence à ressembler à un CP,
            on le passe en filtre"""
            postal_code = parser.get_component("postcode")
            if postal_code:
                for cp in postal_code:
                    if len(str(cp["value"])) == 5:
                        filter.append(f"code_postal = {cp["value"]}")
                    else:
                        filter.append(f"code_postal STARTS WITH {cp["value"]}")

                request=parser.get_address_without(["postcode"])
            
            """ si city contient 2 valeurs et qu'il n'y a pas de road, 
            on considére que le second mot est une ville qu'on filtre
            """ 
            city = parser.get_component("city")
            road = parser.get_component("road")
            if len(city)>1 and len(road)==0:
                for commune in city:
                    filter.append(f"nom_commune CONTAINS '{commune['value']}'")
            
            # Si il y a des filtres, on les assemble en OR
            if len(filter)>0:
                filter_search = "(" + " OR ".join(filter) + ")"  
            
        else:
            logger.debug("trop court pour le parser")
            return { "status": "TOO_SHORT", "choices": [] }
            
        logger.debug(f"Saisie : {q}")
        logger.debug(f"Recherche : {request}")
        logger.debug(f"Filtre de recherche : {filter_search}")
        result = index.search(
            request, {"showRankingScore": True, "filter": filter_search}
        )
        respons=[]
        if len(result["hits"])>0:
            for hit in result["hits"]:
                logger.debug(f"Score: {hit.get('_rankingScore', 0.0):.2f} : {hit.get('adresse')} ")
                respons.append({
                    "score": round(hit.get('_rankingScore', 0.0), 2),
                    "adresse": hit.get('adresse', None),
                    "id": hit.get('id', None),
                    "numero": hit.get('numero', None),
                    "rep": hit.get('rep', None),
                    "nom_voie": hit.get('nom_voie', None),
                    "code_postal": hit.get('code_postal', None),
                    "nom_commune": hit.get('nom_commune', None),
                })

        return { "status": "OK", "choices": respons }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de '{q}': {e}")
        

if __name__ == "__main__":
    # Pour le débogage direct
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=config.log_level
    )
    

