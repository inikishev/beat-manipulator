import BeatManipulator as bm, json, copy
import bm_wrapper as bmw
from tkinter import filedialog

# ___ my stuff ___
import random,os

# ___ get song ___
#filename='F:/Stuff/Music/Tracks/Poseidon & Leon Ross - Parallax.mp3'
#filename = 'F:/Stuff/Music/Tracks/'+random.choice(os.listdir("F:\Stuff\Music\Tracks"))
filename=filedialog.askopenfilename()
#print(filename)

# ___ analyze+fix ___
scale, shift = 0.25, 0
#bmw.lib_test(filename, scale=scale, shift=shift)
#bm.fix_beatmap(filename, scale=scale, shift=shift)

# ___ presets ___
bmw.use_preset ('', filename, 'hardcore', scale=1, shift=0, beat='normal', test=False)
#bmw.use_preset ('', filename, None, scale=scale, shift=shift, test=False)
#bmw.all('', filename, scale=1, shift=0, beat='shifted2', test=False, boring=False, effects=False)

# ___ beat swap __
#song=bm.song(filename)
#song.quick_beatswap(output='', pattern='test', scale=1, shift=0)

# ___ osu ___
#song=bm.song()
#song.generate_hitmap()
#song.osu()
#song.hitsample()

# ___ saber2osu ___
#import Saber2Osu as s2o
#osu=s2o.osu_map(threshold=0.3, declumping=100)

# ___ song to image ___
#song.write_image()

# ___ randoms ___
# while True:
#     filename = 'F:/Stuff/Music/Tracks/'+random.choice(os.listdir("F:\Stuff\Music\Tracks"))
#     bmw.use_preset ('', filename, None, scale=scale, shift=shift, test=False)

# ___ effects ___
#song = bm.song(filename)
#song.audio=bm.pitchB(song.audio, 2, 100)
#song.write_audio(bm.outputfilename('',filename, ' (pitch)'))