from typing import Union
from loguru import logger

def build_respons(results) -> list[dict[str, Union[float, str, int, None]]]:
    """
    Build a response list from search results containing address information.
    
    Args:
        results (dict): Search results dictionary containing a 'hits' key with a list of address matches.
                       Each hit should contain address fields like 'adresse', 'id', 'numero', etc.
    
    Returns:
        list[dict[str, Union[float, str, int, None]]]: A list of dictionaries where each dictionary 
        contains formatted address information with the following keys:
            - score (float): Rounded ranking score of the address match
            - adresse (str | None): Full address string
            - id (str | int | None): Unique identifier for the address
            - numero (str | int | None): Street number
            - rep (str | None): Address repetition/suffix
            - nom_voie (str | None): Street name
            - code_postal (str | int | None): Postal code
            - nom_commune (str | None): Municipality name
    
    Note:
        The function logs debug information showing the score and address for each hit.
        Missing fields in the input hits are filled with None values in the output.
    """
    respons=[]
    for hit in results["hits"]:
       # logger.debug(f"Score: {hit.get('_rankingScore', 0.0):.2f} : {hit.get('adresse')} ")
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
