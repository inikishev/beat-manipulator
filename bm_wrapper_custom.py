import BeatManipulator as bm, random,os, bm_wrapper as bmw
from tkinter import filedialog
from ast import literal_eval
# ___ my stuff ___
import random,os

# ___ get song ___
#filename='F:/Stuff/Music/Tracks/Ivlril - anxiety causer.mp3'
#filename = 'F:/Stuff/Music/Tracks/'+random.choice(os.listdir("F:\Stuff\Music\Tracks"))
filename=filedialog.askopenfilename()
#print(filename)

# ___ analyze+fix ___
scale,shift,beat=1,0,None
while True:
    what=input('''1. t - test; f - fixing; s - skip, d - delete; 
2. scale, shift: 
''').lower().split(' ')
    if len(what)>1: 
        try: scale=literal_eval(what[1])
        except (NameError, SyntaxError):beat=what[1] 
    if len(what)>2: 
        try: shift=literal_eval(what[2])
        except (NameError, SyntaxError):beat=what[2] 
    what=what[0]
    if 't' in what or 'f' in what: bmw.lib_test(filename, scale=scale, shift=shift, beat='normal' if 'f' in what else beat)
    if 'f' in what: bm.fix_beatmap(filename, scale=scale, shift=shift)
    if 'd' in what: bm.delete_beatmap(filename)
    if 's' in what: break
#scale, shift = 1, 0
#bmw.lib_test(filename, scale=scale, shift=shift)
#bm.fix_beatmap(filename, scale=scale, shift=shift)

# ___ presets ___
#bmw.use_preset ('', filename, 'hardcore', scale=1, shift=0, beat='normal', test=False)
#bmw.use_preset ('', filename, None, scale=scale, shift=shift, test=False)
if beat is None: beat=input('normal / shifted / shifted2: ')
if beat is None or beat=='': beat='normal'
bmw.all('', filename, scale=1, shift=0, beat=beat, test=False, boring=False, effects=False)

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