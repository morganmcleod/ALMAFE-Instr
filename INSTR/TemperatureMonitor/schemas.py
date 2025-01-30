from pydantic import BaseModel
from typing import List

DESCRIPTIONS = [
    'Cold head',
    '',
    '15K stage',
    '110K stage',
    'Ambient load',
    '',
    '',
    ''
]

class Temperatures(BaseModel):
    temps: List[float] = [-1, -1, -1, -1, -1, -1, -1, -1]
    errors: List[int] = [1, 1, 1, 1, 1, 1, 1, 1]
    descriptions: List[str] = DESCRIPTIONS
