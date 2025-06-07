from typing import Union
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from address_parser import AddressParser
import sys
from loguru import logger
import meilisearch
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

masterKey = "e615f1fdc87b6de90240cf4501f611e7866519918e9b44bd1be9ff4b02b7fd7d"
mini_len_for_parse = 4

client = meilisearch.Client("http://127.0.0.1:7700", masterKey)
# An index is where the documents are stored.
index = client.index("adresses")


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
    parser = AddressParser()
    filter_search = ""
    try:
        if len(q) >= mini_len_for_parse:
            result = parser.parse(q)
            parser.print_analyse()
            parser.print_choice()

            postal_code = parser.get_component("postcode")
            if postal_code:
                filter_cp = []
                for cp in postal_code:
                    if len(str(cp["value"])) == 5:
                        filter_cp.append(f"code_postal = {cp["value"]}")
                    else:
                        filter_cp.append(f"code_postal STARTS WITH {cp["value"]}")

                if len(postal_code) > 0:
                    filter_search = "(" + " OR ".join(filter_cp) + ")"

                q=parser.get_address_without(["postcode"])
            #city = parser.get_component("city")
            #house_number = parser.get_component("house_number")

            logger.debug(f"Filtre de recherche : {filter_search}")

        else:
            logger.debug("trop court pour le parser")

        result = index.search(
            q, {"showRankingScore": True, "filter": filter_search}
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

        return respons
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de '{q}': {e}")
        

if __name__ == "__main__":
    # Pour le débogage direct
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )