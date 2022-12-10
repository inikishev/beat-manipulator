import BeatManipulator as bm, json
with open("presets.json", "r") as f:
    presets=f.read()

presets=json.loads(presets)

def lib_test(filename,output='', samplerate=44100, lib='madmom.BeatDetectionProcessor', scale=1, shift=0):
    '''basically a way to quickly test scale and offset'''
    if type(filename)==str :
        song=bm.song(filename) 
        samplerate=song.samplerate
    else: 
        song=filename
    song.quick_beatsample(output=None, lib=lib, audio2=bm.generate_sine(0.1, 2000, samplerate), scale=8*scale, shift=0+shift)
    song.quick_beatsample(output=None, lib=lib, audio2=bm.generate_sine(0.05, 1000, samplerate), scale=8*scale, shift=1+shift)
    song.quick_beatsample(output=None, lib=lib, audio2=bm.generate_saw(0.05, 500, samplerate), scale=8*scale, shift=2+shift)
    song.quick_beatsample(output=None, lib=lib, audio2=bm.generate_saw(0.05, 250, samplerate), scale=8*scale, shift=3+shift)
    song.quick_beatsample(output=None, lib=lib, audio2=bm.generate_saw(0.05, 125, samplerate), scale=8*scale, shift=4+shift)
    song.quick_beatsample(output=None, lib=lib, audio2=bm.generate_saw(0.05, 250, samplerate), scale=8*scale, shift=5+shift)
    song.quick_beatsample(output=None, lib=lib, audio2=bm.generate_saw(0.05, 500, samplerate), scale=8*scale, shift=6+shift)
    song.quick_beatsample(output=output, suffix=' ('+lib+')',lib=lib, audio2=bm.generate_saw(0.05, 1000, samplerate), scale=8*scale, shift=7+shift)
    del song

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

def process(song:bm.song, preset: str, scale:float, shift:float)->bm.song:
    #print(preset)
    if 'pattern' in preset: 
        scale=scale*(preset['scale'] if 'scale' in preset else 1)
        shift=shift+(preset['shift'] if 'shift' in preset else 0)
        song.quick_beatswap(output=None, pattern=preset['pattern'], scale=scale, shift=shift)
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



def use_preset(output:str,filename: str, preset: str, presets=presets, scale=1, shift=0, test=False):
    song=bm.song(filename)
    #print(song.samplerate)
    if preset is None:
        weights=[]
        for i in presets.items():
            weights.append(i[1]['weight'])
        import random
        preset = random.choices(population=list(presets), weights=weights, k=1)[0]
    name=preset
    preset=presets[preset]
    if test is True: 
        testsong=bm.song(filename=filename, audio=song.audio, samplerate=song.samplerate)
        lib_test(testsong, output, samplerate=testsong.samplerate)
        del testsong
    #print(name, preset)
    if '1' in preset:
        for i in preset:
            if type(preset[i])==dict:song=process(song, preset[i], scale=scale, shift=shift)
    else: song=process(song, preset,scale=scale,shift=shift)
    song.write_audio(output=bm.outputfilename(output, filename, suffix=' ('+name+')'))
    
def all(output:str,filename: str, presets:dict=presets, scale=1, shift=0, test=True):
    if test is True: 
        testsong=bm.song(filename=filename)
        lib_test(testsong, output, samplerate=testsong.samplerate)
        del testsong
    for i in presets:
        use_preset(output, filename, preset=i, presets=presets, scale=scale, shift=shift, test=False)


import random, os
filename='F:/Stuff/Music/Tracks/STRADEUS - SINNERS x SAINTS.mp3'
#filename = 'F:/Stuff/Music/Tracks/'+random.choice(os.listdir("F:\Stuff\Music\Tracks"))

scale=1
shift=0
test=True
#bm.fix_beatmap(filename, scale=1, shift=0.5)
#lib_test(filename, scale=1, shift=0)
#use_preset ('', filename, 'syncopated', scale=scale, shift=shift, test=test)
#use_preset ('', filename, None, scale=scale, shift=shift, test=False)
all('',filename, scale=scale, shift=shift, test=test)

#song=bm.song(filename)
#song.analyze_beats()
#song.write_image()
#song.quick_beatswap('', 'random', 0.125, 0, autoinsert=False)