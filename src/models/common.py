"""Common enums and shared types for the recruiter domain."""

from enum import Enum
from typing import Literal


class Stage(str, Enum):
    pre_seed = "pre-seed"
    seed = "seed"
    series_a = "series-a"
    series_b = "series-b"
    growth = "growth"
    public = "public"


class Seniority(str, Enum):
    head = "head"
    director = "director"
    vp = "vp"
    cxo = "cxo"


Tone = Literal["friendly", "professional", "concise"]
Channel = Literal["email", "linkedin"]
