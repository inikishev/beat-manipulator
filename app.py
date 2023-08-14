import gradio as gr, numpy as np
from gradio.components import Audio, Textbox, Checkbox, Image
import beat_manipulator as bm
import cv2

def BeatSwap(audiofile, pattern: str = 'test', scale:float = 1, shift:float = 0, caching:bool = True, variableBPM:bool = False):
    print()
    print(f'path = {audiofile}, pattern = "{pattern}", scale = {scale}, shift = {shift}, caching = {caching}, variable BPM = {variableBPM}')
    if pattern == '' or pattern is None: pattern = 'test'
    if caching is not False: caching == True
    if variableBPM is not True: variableBPM == False
    try:
        scale=bm.utils._safer_eval(scale)
    except: scale = 1
    try:
        shift=bm.utils._safer_eval(shift)
    except: shift = 0
    if scale <0: scale = -scale
    if scale < 0.02: scale = 0.02
    print('Loading auidofile...')
    if audiofile is not None:
        try:
            song=bm.song(audio=audiofile,log=False)
        except Exception as e:
            print(f'Failed to load audio, retrying: {e}')
            song=bm.song(audio=audiofile, log=False)
    else: 
        print(f'Audiofile is {audiofile}')
        return
    try:
        print(f'Scale = {scale}, shift = {shift}, length = {len(song.audio[0])/song.sr}')
        if len(song.audio[0]) > (song.sr*1800):
            song.audio = np.array(song.audio, copy=False)
            song.audio = song.audio[:,:song.sr*1800]
    except Exception as e: print(f'Reducing audio size failed, why? {e}')
    lib = 'madmom.BeatDetectionProcessor' if variableBPM is False else 'madmom.BeatTrackingProcessor'
    song.path = '.'.join(song.path.split('.')[:-1])[:-8]+'.'+song.path.split('.')[-1]
    print(f'path: {song.path}')
    print('Generating beatmap...')
    song.beatmap_generate(lib=lib, caching=caching)
    song.beatmap_shift(shift)
    song.beatmap_scale(scale)
    print('Generating image...')
    try:
        song.image_generate()
        image = bm.image.bw_to_colored(song.image)
        y=min(len(image), len(image[0]), 2048)
        y=max(y, 2048)
        image = np.rot90(np.clip(cv2.resize(image, (y,y), interpolation=cv2.INTER_NEAREST), -1, 1))
        #print(image)
    except Exception as e: 
        print(f'Image generation failed: {e}')
        image = np.asarray([[0.5,-0.5],[-0.5,0.5]])
    print('Beatswapping...')
    song.beatswap(pattern=pattern, scale=1, shift=0)
    song.audio = (np.clip(np.asarray(song.audio), -1, 1) * 32766).astype(np.int16).T
    #song.write_audio(output=bm.outputfilename('',song.filename, suffix=' (beatswap)'))
    print('___ SUCCESS ___')
    return ((song.sr, song.audio), image)

audiofile=Audio(source='upload', type='filepath')
patternbox = Textbox(label="Pattern:", placeholder="1, 3, 2, 4!", value="1, 2>0.5, 3, 4>0.5, 5, 6>0.5, 3, 4>0.5, 7, 8", lines=1)
scalebox = Textbox(value=1, label="Beatmap scale. At 2, every two beat positions will be merged, at 0.5 - a beat position added between every two existing ones.", placeholder=1, lines=1)
shiftbox = Textbox(value=0, label="Beatmap shift, in beats (applies before scaling):", placeholder=0, lines=1)
cachebox = Checkbox(value=True, label="Enable caching generated beatmaps for faster loading. Saves a file with beat positions and loads it when you open same audio again.")
beatdetectionbox = Checkbox(value=False, label='Enable support for variable BPM, however this makes beat detection slightly less accurate')

gr.Interface (fn=BeatSwap,inputs=[audiofile,patternbox,scalebox,shiftbox, cachebox, beatdetectionbox],outputs=[Audio(type='numpy'), Image(type='numpy')],theme="default",
title = "Stunlocked's Beat Manipulator"
,description = """Remix music using AI-powered beat detection and advanced beat swapping. Make \"every other beat is missing\" remixes, or completely change beat of the song. 

Github - https://github.com/stunlocked1/beat_manipulator. 

Colab version - https://colab.research.google.com/drive/1gEsZCCh2zMKqLmaGH5BPPLrImhEGVhv3?usp=sharing"""
,article="""# <h1><p style='text-align: center'><a href='https://github.com/stunlocked1/beat_manipulator' target='_blank'>Github</a></p></h1>
### Basic usage
Upload your audio, enter the beat swapping pattern, change scale and shift if needed, and run it.

### pattern syntax
patterns are sequences of **beats**, separated by **commas** or other separators. You can use spaces freely in patterns to make them look prettier.
- `1, 3, 2, 4` - swap 2nd and 3rd beat every four beats. Repeats every four beats because `4` is the biggest number in it.
- `1, 3, 4` - skip 2nd beat every four beats
- `1, 2, 3, 4!` - skip 4th beat every four beats. `!` skips the beat.

**slicing:**
- `1>0.5` - plays first half of 1st beat
- `1<0.5` - plays last half of 1st beat
- `1 > 1/3, 2, 3, 4` - every four beats, plays first third of the first beat - you can use math expressions anywhere in your pattern.
- also instead of slicing beats you can use a smaller `scale` parameter to make more precise beat edits 

**merging beats:**
- `1; 2, 3, 4` - every four beats, play 1st and 2nd beats at the same time.

**effects:**
- `1, 2r` - 2nd beat will be reversed
- `1, 2s0.5` - 2nd beat will be played at 0.5x speed
- `1, 2d10` - 2nd beat will have 8-bit effect (downsampled)

You can do much more with the syntax - shuffle/randomize beats, use samples, mix two songs, etc. Syntax is described in detail at https://github.com/stunlocked1/beat_manipulator
### scale
`scale = 0.5` will insert a new beat position between every existing beat position in the beatmap. That allows you to make patterns on smaller intervals.

`scale = 2`, on the other hand, will merge every two beat positions in the beatmap. Useful, for example, when beat map detection puts sees BPM as two times faster than it actually is, and puts beats in between every actual beat.
### shift
Shifts the beatmap, in beats. For example, if you want to remove 4th beat every four beats, you can do it by writing `1, 2, 3, 4!`. However sometimes it doesn't properly detect which beat is first, and for example remove 2nd beat every 4 beats instead. In that case, if you want 4th beat, use `shift = 2`. Also sometimes beats are detected right in between actual beats, so shift = 0.5 or -0.5 will fix it.
### creating images
You can create cool images based on beat positions. Each song produces its own unique image. This gradio app creates a 2048x2048 image from each song.
### presets
A bunch of example patterns: https://github.com/stunlocked1/beat_manipulator/blob/main/beat_manipulator/presets.yaml

Those are supposed to be used on normalized beat maps, where kick + snare is two beats, so make sure to adjust beatmaps using `scale` and `shift`.

### Changelog:
- play two beats at the same time by using `;` instead of `,`
- significantly reduced clicking
- shuffle and randomize beats
- gradient effect, similar to high pass
- add samples to beats
- use beats from other songs

### My soundcloud https://soundcloud.com/stunlocked
"""
 ).launch(share=False)