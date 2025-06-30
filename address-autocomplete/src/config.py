import os
from typing import Optional
from enum import IntEnum


class LogLevel(IntEnum):
    DEBUG    = 10
    INFO     = 20
    WARNING  = 30
    ERROR    = 40
    CRITICAL = 50


class ServiceConfig:
    def __init__(self, 
                 meilisearch_url: Optional[str] = None,
                 meilisearch_key: Optional[str] = None,
                 meilisearch_index: Optional[str] = None,
                 ):
        """
        Initialize the configuration object with MeiliSearch connection parameters and search settings.
        Args:
            meilisearch_url (Optional[str], optional): MeiliSearch server URL. 
                Defaults to environment variable 'TRUSTY_ADDRESS_DATABASE' or 
                'https://dbref.trustydata.tech' if not provided.
            meilisearch_key (Optional[str], optional): MeiliSearch API search key.
                Defaults to environment variable 'TRUSTY_ADDRESS_SEARCH_KEY' if not provided.
            meilisearch_index (Optional[str], optional): MeiliSearch index name.
                Defaults to environment variable 'TRUSTY_ADDRESS_DATABASE_INDEX' or 
                'adresses_test' if not provided.
        Attributes:
            meilisearch_url (str): The MeiliSearch server URL.
            meilisearch_key (str): The MeiliSearch API search key.
            meilisearch_index (str): The MeiliSearch index name.
            score_mini_swap_sequence (float): Minimum score required to change search sequence (0.6).
            search_wo_house_number (bool): Whether to enable escalation in searches without house numbers (True).
            log_level (LogLevel): Logging level determined from environment variable 'TRUSTY_ADDRESS_LOG_LEVEL'.
                Accepts DEBUG, INFO, WARN/WARNING, ERROR, CRITICAL. Defaults to WARNING.
        """
        
        self.meilisearch_url = meilisearch_url or os.getenv(
            'TRUSTY_ADDRESS_DATABASE', 
            'https://dbref.trustydata.tech'  # URL par défaut
        )
        self.meilisearch_key = meilisearch_key or os.getenv(
            'TRUSTY_ADDRESS_SEARCH_KEY' # Clé API de recherche meilisearch
        )
        self.meilisearch_index = meilisearch_index or os.getenv(
            'TRUSTY_ADDRESS_DATABASE_INDEX', 
            'adresses_test'  # Nom de l'index par défaut
        )
        
        # Score mini nécessaire pour changer de séquence de recherche
        self.score_mini_swap_sequence = 0.6
        # Possibilité d'escalade dans les recherches.
        self.search_wo_house_number = True
        
        log = os.getenv(
            'TRUSTY_ADDRESS_LOG_LEVEL',
            'WARNING'
        )
        if log.upper() == 'DEBUG':
            self.log_level = LogLevel.DEBUG
        elif log.upper() == 'INFO':
            self.log_level = LogLevel.INFO
        elif log.upper() in ['WARN','WARNING']:
            self.log_level = LogLevel.WARNING
        elif log.upper() == 'ERROR':
            self.log_level = LogLevel.ERROR
        elif log.upper() == 'CRITICAL':
            self.log_level = LogLevel.CRITICAL
        else:
            self.log_level = LogLevel.WARNING