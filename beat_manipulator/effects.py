import numpy as np
from . import io

def deco_abs(effect):
    def stuff(*args, **kwargs):
        if len(args)>0: audio = args[0]
        else: audio = kwargs['audio']
        if not isinstance(audio, np.ndarray): audio = io._load(audio)
        audio_signs = np.sign(audio)
        audio = np.abs(audio)
        if len(args)>0: args[0] = audio
        else: kwargs['audio'] = audio
        audio = effect(*args, **kwargs)
        audio *= audio_signs
    return stuff



def volume(audio: np.ndarray, v: float):
    return audio*v

def speed(audio: np.ndarray, s: float = 2, precision:int = 24):
    if s%1 != 0 and (1/s)%1 != 0:
        import fractions
        s = fractions.Fraction(s).limit_denominator(precision)
        audio = np.repeat(audio, s.denominator, axis=1)
        return audio[:,::s.numerator]
    elif s%1 == 0:
        return audio[:,::int(s)]
    else:
        return np.repeat(audio, int(1/s), axis=1)

def channel(audio: np.ndarray, c:int = None):
    if c is None:
        audio[0], audio[1] = audio[1], audio[0]
        return audio
    elif c == 0:
        audio[0] = 0
        return audio
    else:
        audio[1] = 0
        return audio
    
def downsample(audio: np.ndarray, d:int = 10):
    return np.repeat(audio[:,::d], d, axis=1)

def gradient(audio: np.ndarray, number: int = 1):
    for _ in range(number):
        audio = np.gradient(audio, axis=1)
    return audio

def bitcrush(audio: np.ndarray, b:float = 4):
    if 1/b > 1:
        return np.around(audio, decimals=int(1/b))
    else: 
        return np.around(audio*b, decimals = 1)

def reverse(audio: np.ndarray):
    return audio[:,::-1]

def normalize(audio: np.ndarray):
    return audio*(1/np.max(np.abs(audio)))

def clip(audio: np.ndarray):
    return np.clip(audio, -1, 1)

def to_sidechain(audio: np.ndarray):
    audio = np.clip(np.abs(audio), -1, 1)
    for channel in range(len(audio)):
        audio[channel] = np.abs(1 - np.convolve(audio[channel], np.ones(shape=(1000)), mode = 'same'))
    return audio



# some stuff is defined in main.py to reduce function calls for 1 line stuff
BM_EFFECTS = {
    "v": "volume",
    "s": speed,
    "c": channel,
    "d": "downsample",
    "g": "gradient",
    "b": bitcrush,
    "r": "reverse",
}