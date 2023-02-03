import BeatManipulator as bm, json
from ast import literal_eval
with open("presets.json", "r") as f:
    presets=f.read()

presets=json.loads(presets)
def song_copy(song:bm.song):
    return bm.song(path=song.path, audio=song.audio, samplerate=song.samplerate, beatmap=song.beatmap, gradio=song.gradio, caching=song.caching,filename=song.filename, copied=True)

def normalize(song: bm.song, beat, pattern=None, scale=None, shift=None):
    beat=beat.lower()
    if pattern is not None:
        if scale is None: scale=1
        if shift is None: shift=0
        song.quick_beatswap(output=None, pattern=pattern, scale=scale,shift=shift)
    elif beat=='normal' or beat is None: pass
    elif beat=='shifted': song.quick_beatswap(output=None, pattern='1,2,3,4,5,7,6,8', scale=0.5)
    elif beat=='shifted2': song.quick_beatswap(output=None, pattern='1,2,3,4,5,6,8,7', scale=0.5)
    else: print(f"'{beat}' is not a valid beat")
    return song

def lib_test(filename,output='', samplerate=44100, lib='madmom.BeatDetectionProcessor', scale=1, shift=0,beat='normal'):
    '''basically a way to quickly test scale and offset'''
    if type(filename)==str :
        song=bm.song(filename)
        samplerate=song.samplerate
    else:
        song=filename
    if beat!='normal' and beat is not None: song=normalize(song=song, beat=beat, scale=scale, shift=shift)
    song.quick_beatswap(output=None, pattern='test', scale=scale, shift=shift)
    if beat!='normal' and beat is not None: song=normalize(song=song, beat=beat, scale=scale, shift=shift)
    song.write_audio(output=bm.outputfilename('', song.filename, f' ({lib} x{scale} {shift})'))

def lib_test_full(filename,samplerate):
    '''A way to test all beat detection modules to see which one performs better.'''
    print(filename)
    lib_test(filename, samplerate,'madmom.BeatDetectionProcessor')
    lib_test(filename, samplerate,'madmom.BeatDetectionProcessor.consistent')
    #lib_test(filename, samplerate,'madmom.BeatTrackingProcessor') # better for live performances with variable BPM
    #lib_test(filename, samplerate,'madmom.BeatTrackingProcessor.constant') # results identical to madmom.BeatDetectionProcessor
    lib_test(filename, samplerate,'madmom.BeatTrackingProcessor.consistent')
    lib_test(filename, samplerate,'madmom.CRFBeatDetectionProcessor')
    lib_test(filename, samplerate,'madmom.CRFBeatDetectionProcessor.constant')
    #lib_test(filename, samplerate,'madmom.DBNBeatTrackingProcessor') # better for live performances with variable BPM
    lib_test(filename, samplerate,'madmom.DBNBeatTrackingProcessor.1000')
    lib_test(filename, samplerate,'madmom.DBNDownBeatTrackingProcessor')
    import gc
    gc.collect()

def process_list(something)-> list:
    if isinstance(something, int) or isinstance(something, float): something=(something,)
    elif isinstance(something,list): False if isinstance(something[0],int) or isinstance(something[0],float) else list(literal_eval(i) for i in something)
    else: something=list(literal_eval(i) for i in something.split(','))
    return something

def process(song:bm.song, preset: str, scale:float, shift:float, random=False, every=False)->bm.song:
    #print(preset)
    if 'pattern' in preset:
        shift=shift+(preset['shift'] if 'shift' in preset else 0)
        # Scale can be a list and we either take one value or all of them
        if 'scale' in preset: pscale=process_list(preset['scale'])
        else: pscale=(1,)
        #input(pscale)
        if random is True:
            import random
            pscale=random.choice(pscale)
        elif every is True:
            songs=[]
            for i in pscale:
                song2=song_copy(song)
                song2.quick_beatswap(output=None, pattern=preset['pattern'], scale=scale*i, shift=shift)
                songs.append((song2, i))
            return songs
        else: pscale=preset['scale_d'] if 'scale_d' in preset else pscale[0]
        if every is False: song.quick_beatswap(output=None, pattern=preset['pattern'], scale=scale*pscale, shift=shift)
    elif preset['type'] =='sidechain':
        length=preset['sc length'] if 'sc length' in preset else 0.5
        curve=preset['sc curve'] if 'sc curve' in preset else 2
        vol0=preset['sc vol0'] if 'sc vol0' in preset else 0
        vol1=preset['sc vol1'] if 'sc vol1' in preset else 1
        sidechain=bm.open_audio(preset['sc impulse'])[0] if 'sc impulse' in preset else bm.generate_sidechain(samplerate=song.samplerate, length=length, curve=curve, vol0=vol0, vol1=vol1, smoothing=40)
        scale=scale*(preset['scale'] if 'scale' in preset else 1)
        shift=shift+(preset['shift'] if 'shift' in preset else 0)
        song.quick_sidechain(output=None, audio2=sidechain, scale=scale, shift=shift)
    elif preset['type'] =='beatsample':
        sample=preset['filename']
        scale=scale*(preset['scale'] if 'scale' in preset else 1)
        shift=shift+(preset['shift'] if 'shift' in preset else 0)
        song.quick_beatsample(output=None, filename2=sample, scale=scale, shift=shift)
    return song


def use_preset(output:str,song: str, preset: str, presets=presets, scale=1, shift=0, beat:str='normal', test=False, normalize=True, random=False, every=False):
    if not isinstance(song, bm.song): song=bm.song(song)
    #print(song.samplerate)
    if preset is None:
        weights=[]
        for i in presets.items():
            weights.append(i[1]['weight'])
        import random
        preset = random.choices(population=list(presets), weights=weights, k=1)[0]
    name=preset
    if isinstance(preset, str): preset=presets[preset]
    if test is True:
        testsong=song_copy(song)
        lib_test(testsong, output, samplerate=testsong.samplerate)
        del testsong
    #print(name, preset)
    if normalize is True and beat!='normal' and beat is not None:
        if 'normalize' in preset:
            if preset['normalize'] is True:
                song=normalize(song, beat)
    if '1' in preset:
        for i in preset:
            if type(preset[i])==dict:song=process(song, preset[i], scale=scale, shift=shift)
    else: song=process(song, preset,scale=scale,shift=shift,random=random, every=every)
    if isinstance(song, list): 
        for i in song:
            i[0].write_audio(output=bm.outputfilename(output, i[0].filename, suffix=f' ({name}{(" x"+str(round(i[1], 3)))*(len(song)>1)})'))
    else: song.write_audio(output=bm.outputfilename(output,  song.filename, suffix=' ('+name+')'))

def all(output:str,filename: str, presets:dict=presets, scale=1, shift=0, beat='normal', test=True, boring=False, effects=False, variations=False):
    if boring is False:
        for i in ['2x faster','3x faster','4x faster','8x faster','1.33x faster','1.5x faster','1.5x slower','reverse','random', 'syncopated effect']:
            if i in presets: 
                #print(i)
                presets.pop(i)
    if not isinstance(filename, bm.song): song=bm.song(filename)
    else: song=filename
    song_normalized=normalize(song_copy(song), beat)
    if test is True:
        testsong=song_copy(song)
        lib_test(testsong, output, samplerate=testsong.samplerate)
        del testsong
    for key, i in presets.items():
        #print(key, i)
        if 'scale' in i:
            #print(i['scale'])
            if isinstance(i['scale'], int) or isinstance(i['scale'], float):
                if i['scale']<0.01:
                    continue
                if effects is False:
                    if 'effect - ' in key: continue
        if 'normalize' in i:
            if i['normalize'] is True:
                song2=song_copy(song_normalized)
            else: song2=song_copy(song)
        else: song2=song_copy(song)
        use_preset(output, song2, preset=key, presets=presets, scale=scale, shift=shift, beat=beat, test=False, normalize=False, every=variations)

def randosu(filename=None):
    if filename is None: filename = 'F:/Stuff/Music/Tracks/'+random.choice(os.listdir("F:\Stuff\Music\Tracks"))
    print(filename)
    song=bm.song(filename)
    song.generate_hitmap('madmom.RNNBeatProcessor')
    song.osu()


# ___ my stuff ___
import random,os

# ___ get song ___
#filename='F:/Stuff/Music/Tracks/Poseidon & Leon Ross - Parallax.mp3'
#filename = 'F:/Stuff/Music/Tracks/'+random.choice(os.listdir("F:\Stuff\Music\Tracks"))
# print(filename)

# ___ analyze+fix ___
#scale, shift = 1,0
#lib_test(filename, scale=scale, shift=shift)
#bm.fix_beatmap(filename, scale=scale, shift=shift)

# ___ presets ___
#use_preset ('', filename, 'dotted kicks', scale=1, shift=0, beat='normal', test=False)
#use_preset ('', filename, None, scale=scale, shift=shift, test=False)
#all('', filename, scale=1, shift=0, beat='normal', test=False)

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
#     use_preset ('', filename, None, scale=scale, shift=shift, test=False)

# ___ effects ___
#song = bm.song(filename)
#song.audio=bm.pitchB(song.audio, 2, 100)
#song.write_audio(bm.outputfilename('',filename, ' (pitch)'))