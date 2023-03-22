import numpy as np
from . import effects

def volume(audio: np.ndarray) -> float:
    return np.average(np.abs(audio))

def volume_gradient(audio: np.ndarray, number:int = 1) -> float:
    audio = effects.gradient(audio, number = number)
    return np.average(np.abs(audio))

def maximum_high(audio: np.ndarray, number:int = 1) -> float:
    audio = effects.gradient(audio, number = number)
    return np.max(np.abs(audio))

def locate_1st_hit(audio: np.ndarray, number: int = 1):
    audio = effects.gradient(audio, number = number)
    return np.argmax(audio, axis=1) / len(audio[0])

def is_hit(audio: np.ndarray, threshold: float = 0.5, number:int = 1) -> int:
    return 1 if maximum_high(audio, number=number) > threshold else 0

def hit_at_start(audio: np.ndarray, diff = 0.1) -> int:
    return is_hit(audio) * (locate_1st_hit(audio) <= diff)

def hit_in_middle(audio: np.ndarray, diff = 0.1) -> int:
    return is_hit(audio) * ((0.5 - diff) <= locate_1st_hit(audio) <= (0.5 + diff))

def hit_at_end(audio: np.ndarray, diff = 0.1) -> int:
    return is_hit(audio) * (locate_1st_hit(audio) >= (1-diff))

BM_METRICS = {
    "v": volume,
    "g": volume_gradient,
    "m": maximum_high,
    "l": locate_1st_hit,
    "h": is_hit,
    "s": hit_at_start,
    "a": hit_in_middle,
    "e": hit_at_end,
}