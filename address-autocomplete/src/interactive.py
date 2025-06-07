from address_parser import AddressParser
import sys
from loguru import logger
import meilisearch

masterKey = "e615f1fdc87b6de90240cf4501f611e7866519918e9b44bd1be9ff4b02b7fd7d"
mini_len_for_parse = 4


def main():
    print("Hello, World!")
    client = meilisearch.Client("http://127.0.0.1:7700", masterKey)
    # An index is where the documents are stored.
    index = client.index("adresses")
    parser = AddressParser()

    print("Entrez des adresses (une par ligne, CTRL+D pour terminer):")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        filter_search = ""
        logger.info(f"Traitement de l'adresse: {line}")
        try:
            if len(line) >= mini_len_for_parse:
                result = parser.parse(line)
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

                line=parser.get_address_without(["postcode"])

#                road = parser.get_component("road")
#                filter_road = []
#                for r in road:
#                    filter_road.append(f"nom_voie = '{r["value"]}'")

#                city = parser.get_component("city")
#                house_number = parser.get_component("house_number")

                logger.debug(f"Filtre de recherche : {filter_search}")

            else:
                logger.debug("trop court pour le parser")

            result = index.search(
                line, {"showRankingScore": True, "filter": filter_search}
            )
            logger.debug(f"Recherche : {line}")
            for response in result["hits"]:
                logger.debug(
                    f"Score: {response.get('_rankingScore', 0.0):.2f} : {response.get('adresse')} "
                )
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de '{line}': {e}")


if __name__ == "__main__":
    main()
