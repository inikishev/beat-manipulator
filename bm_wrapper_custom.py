import BeatManipulator as bm, random,os, bm_wrapper as bmw, numpy,cv2, timeit
from tkinter import filedialog
from ast import literal_eval
# ___ my stuff ___
import random,os

# ___ get song ___
#filename='F:/Stuff/Music/Tracks/Ivlril - anxiety causer.mp3'
filename = 'F:/Stuff/Music/Tracks/'+random.choice(os.listdir("F:\Stuff\Music\Tracks"))
print(filename)

# ___ analyze+fix ___
def interact(song, ask=False):
    if ask is True and song is None:
        filename=filedialog.askopenfilename()
        song=bm.song(filename)
    if not(isinstance(song, bm.song)): song=bm.song(path=song)
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
        if 't' in what or 'f' in what: bmw.lib_test(song, scale=scale, shift=shift, beat='normal' if 'f' in what else beat)
        if 'f' in what: bm.fix_beatmap(song, scale=scale, shift=shift)
        if 'd' in what: bm.delete_beatmap(song)
        if 's' in what: break

    if beat is None: beat=input('normal / shifted / shifted2: ')
    if beat is None or beat=='': beat='normal'
    bmw.all('', filename, scale=1, shift=0, beat=beat, test=False, boring=False, effects=False)

#interact()

#scale, shift = 1, 0
#bmw.lib_test(filename, scale=scale, shift=shift)
#bm.fix_beatmap(filename, scale=scale, shift=shift)

# ___ presets ___
#bmw.use_preset ('', filename, 'hardcore', scale=1, shift=0, beat='normal', test=False)
#bmw.use_preset ('', filename, None, scale=scale, shift=shift, test=False)
#bmw.all('', filename, scale=1, shift=0, beat=beat, test=False, boring=False, effects=False)


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

# ___ effects ___

# ___ song to image ___
# song.analyze_beats()
# song.audio_beatimage(mode='median')
# song.beatimage_effect(bm.image_effect_shapren, 0.1)
# song.beatimage_write('output.png')
# song.beatimage_audio()
# song.write_audio('output.mp3')
# ___ randoms ___
# while True:
#     filename = 'F:/Stuff/Music/Tracks/'+random.choice(os.listdir("F:\Stuff\Music\Tracks"))
#     bmw.use_preset ('', filename, None, scale=scale, shift=shift, test=False)

# ___ effects ___
#song = bm.song(filename)
#song.audio=bm.pitchB(song.audio, 2, 100)
#song.write_audio(bm.outputfilename('',filename, ' (pitch)'))

# mix 2 songs
# song1=bm.song('F:/Stuff/Music/Tracks/Noisia - GO MVP Anthem.mp3')
# song2=bm.song('F:/Stuff/Music/Tracks/hali - psy.mp3')
# song2.audio=bm.effect_inverse_gradient(song1.audio)
# song2.write_audio('output2.mp3')
#1000 - 20 sec
#10000 - 200 sec (3.33 min)
#100000 - 33 min (0.5h)
#1000000 - 5h

# bpm
filename='F:/Stuff/Music/Tracks/Vowl - Pressure.mp3'
song=bm.song(filename)
#song.detect_bpm(bpm_low=50, bpm_high=200, bpm_step=0.01, mode=1, shift_step=25)
print(timeit.timeit(lambda: bm.detect_bpm(song.audio, song.samplerate), number=1))
bmw.lib_test(song, scale=1, shift=0, beat='normal')
song.audio_beatimage(mode='maximum')
song.beatimage_write('output.png')