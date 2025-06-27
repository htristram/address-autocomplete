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