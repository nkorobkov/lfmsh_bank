from enum import Enum


class States(Enum):
    created = 'created'
    processed = 'processed'
    declined = 'declined'
    substituted = 'substituted'

