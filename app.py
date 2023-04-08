import gradio as gr, numpy as np
from gradio.components import Audio, Textbox, Checkbox, Image
import beat_manipulator as bm
import cv2

def BeatSwap(audiofile, pattern: str = 'test', scale:float = 1, shift:float = 0, caching:bool = True, variableBPM:bool = False):
    print()
    print(f'path = {audiofile}, pattern = "{pattern}", scale = {scale}, shift = {shift}, caching = {caching}, variable BPM = {variableBPM}', end=',  ')
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
    if scale < 0.01: scale = 0.01
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
        print(f'scale = {scale}, shift = {shift}, length = {len(song.audio[0])/song.sr}')
        if len(song.audio[0]) > (song.sr*1800):
            song.audio = np.array(song.audio, copy=False)
            song.audio = song.audio[:,:song.sr*1800]
    except Exception as e: print(f'Reducing audio size failed, why? {e}')
    lib = 'madmom.BeatDetectionProcessor' if variableBPM is False else 'madmom.BeatTrackingProcessor'
    song.path = song.path.split('.')[-2][:-8]+'.'+song.path.split('.')[-1]
    song.beatmap_generate(lib=lib, caching=caching)
    song.beatmap_shift(shift)
    song.beatmap_scale(scale)
    try:
        song.image_generate()
        image = bm.image.bw_to_colored(song.image)
        y=min(len(image), len(image[0]), 2048)
        y=max(y, 2048)
        image = np.rot90(np.clip(cv2.resize(image, (y,y), interpolation=cv2.INTER_NEAREST), -1, 1))
        print(image)
        #print(image)
    except Exception as e: 
        print(f'Image generation failed: {e}')
        image = np.asarray([[0.5,-0.5],[-0.5,0.5]])
    song.beatswap(pattern=pattern, scale=1, shift=0)
    song.audio = (np.clip(np.asarray(song.audio), -1, 1) * 32766).astype(np.int16).T
    #song.write_audio(output=bm.outputfilename('',song.filename, suffix=' (beatswap)'))
    print('___ SUCCESS ___')
    return ((song.sr, song.audio), image)

audiofile=Audio(source='upload', type='filepath')
patternbox = Textbox(label="Pattern:", placeholder="1, 3, 2, 4!", value="1, 2!", lines=1)
scalebox = Textbox(value=1, label="Beatmap scale. At 2, every two beat positions will be merged, at 0.5 - a beat position added between every two existing ones.", placeholder=1, lines=1)
shiftbox = Textbox(value=0, label="Beatmap shift, in beats (applies before scaling):", placeholder=0, lines=1)
cachebox = Checkbox(value=True, label="Enable caching generated beatmaps for faster loading. Saves a file with beat positions and loads it when you open same audio again.")
beatdetectionbox = Checkbox(value=False, label='Enable support for variable BPM, however this makes beat detection slightly less accurate')

gr.Interface (fn=BeatSwap,inputs=[audiofile,patternbox,scalebox,shiftbox, cachebox, beatdetectionbox],outputs=[Audio(type='numpy'), Image(type='numpy')],theme="default",
title = "Stunlocked's Beat Manipulator"
,description = """Remix music using AI-powered beat detection and advanced beat swapping. Make \"every other beat is missing\" remixes, or completely change beat of the song. 

Github - https://github.com/stunlocked1/BeatManipulator. 

Colab version - https://colab.research.google.com/drive/1gEsZCCh2zMKqLmaGH5BPPLrImhEGVhv3?usp=sharing"""
,article="""# <h1><p style='text-align: center'><a href='https://github.com/stunlocked1/BeatManipulator' target='_blank'>Github</a></p></h1>

# Basic usage

Upload your audio, enter the beat swapping pattern, change scale and shift if needed, and run it.

# pattern syntax
The pattern syntax is quite powerful and you can do a whole bunch of stuff with it. 

Basic syntax is - `1, 3, 2, 4` means every 4 beats, swap 2nd and 3rd beats, but you can do much more, like applying audio effects, shuffling beats, slicing them, mixing two songs, adding samples, sidechain.

You can use spaces freely in patterns for formatting. Most other symbols have some use though. Here is the full syntax:
#### beats
* `1` - 1st beat;
* `1>0.5` - first half of first beat
* `1<0.5` - second half of first beat
* `0:0.5` - range of beats, this also means first half of first beat, but with this you can do complex stuff like `1.25:1.5`. However this one is a bit more confusing because indexing starts from 0, so 1:2 is second beat, not first.
* Also sometimes it is more convenient to use smaller `scale`, like 0.5 or 0.25, instead of slicing beats.
#### basic patterns
- `1, 3, 2, 4` - 3rd and 2nd beats will be swapped every 4 beats. Happens every 4 beats because 4 is the biggest number in the pattern.
- `1, 2, 3, 4!` - every 4 beats, it will remove the 4th beat. `!` allows you to skip a beat but it still counts for pattern size.
- Specifying pattern length: `pattern = '1, 2, 3', length = 4` is another way to remove 4th beat every 4 beats.
- `1, 4` skips 2nd and 3rd beat
- `1; 2` plays 1st and second beat at the same time.
#### joining operators
`,` and `;` are beat joining operators. Here are all available joiners:
  - `,` puts the beat next to previous beat.
  - `;` puts the beat on top of previous beat. Normalizes the volume to avoid clipping. If previous beat is shorter, your beat will be shortened to match it.
  - `^` multiplies previous beat by your beat. This can be used for fake sidechain.
  - `$` adds the beat on top of previous beat + sidechains previous beat by your beat (I haven't tested this one)
#### effects
beats can be followed by effects. For example `1s0.75` means take first beat and play it at 0.75x speed. Here are all available effects:
  - `s` - speed. `1s2` means first beat will be played at 2x speed.
  - `r` - reverse. `1r` means first beat will have reversed audio.
  - `v` - volume. `1v0.5` means 1st beat will have 50% volume
  - `d` - downsample, or 8-bit sound. `1d10` will downsample the first beat so that it sounds 8-bit. Good values start above 7.
  - `b` - bitcrush. `1b4` will bitcrush it.
  - `g` - gradient, sounds like highpass. `1g1` is the recommended value
  - `c` - channel. If not followed by number, swaps channels. If followed by 0, plays only left channel. If 1, only right channel
  - mixing effects - `1s2rd8` - take first beat, play at 2x speed, reversed, and downsampled.
#### math
mathematical expressions with `+`, `-`, `*`, `/`, and `**` are supported. For example, if you write `1/3` anywhere in the pattern, to slice beats or as effect value, it will be replaced by `0.33333333`
#### using samples, mixing two songs
- WIP (you can do that if you run locally, I am just figuring out gradio UI because that requires a bunch of new input interface)
#### other stuff
- `i` will be replaced by current position, e.g. `i, i, i, i+1` is equvalent to `1, 2, 3, 4 + 1`, or `1, 2, 3, 5`.
- `#` will add shuffle all beats with the same number after it. `1#1, 2#2, 3#1, 4#2, 5#1, 6#2, 7#1, 8#2` will shuffle 1st, 3rd, 5th and 7th beats (the are in 1st group), and 2nd, 4th, 6th and 8th beats - from 2nd shuffle group.
- `!` skips that beat. If you want to remove every 4th beat, you can't just do `1, 2, 3`, because that would simply play every 3 beats. So to play 3 beats every 4 beats, you can write `1, 2, 3, 4!`
- `?` makes that beat not count for pattern size. For example, `1, 2, 3, 8` will normally repeat every 8 beats because 8 is the highest number, but `1, 2, 3, 8?` will repeat every 3 beats.
- `@` allows you to take a random beat with the following syntax: @start_stop_step. For example, `@1_4_0.5` means it will take a random beat out of 1st, 1.5, 2nd, 2.5, 3rd, 3.5, and 4th. It will take whole beat, so you can also add `>0.5` to take only first half.
- `%` - for very advanced patterns you can create variables from various metrics. For example, `%v` will create a variable with average volume of that beat, and all following `%` will be replaced by that variable until you create a new one. Useful for applying different effects based on different song metrics. All metrics are in `beat_manipulator/metrics.py`.
#### special patterns
You can write special commands into the `pattern` argument instead of actual patterns.
- `reverse` - plays all beats in reverse chronological order
- `shuffle` - shuffles all beats
- `test` - puts different pitched cowbells on each beat, useful for testing beat detection and adjusting it using scale and shift. Each cowbell is 1 beat, highest pitched cowbell is the 1st beat, lowest pitched - 4th.
#### complex patterns
You should be able to use all of the above operators in any combination, as complex as you want. Very low scales should also be fine, up to 0.01.
### scale
`scale = 0.5` will insert a new beat position between every existing beat position in the beatmap. That allows you to make patterns on smaller intervals.

`scale = 2`, on the other hand, will merge every two beat positions in the beatmap. Useful, for example, when beat map detection puts sees BPM as two times faster than it actually is, and puts beats in between every actual beat.
### shift
Shifts the beatmap, in beats. For example, if you want to remove 4th beat every four beats, you can do it by writing `1, 2, 3, 4!`. However sometimes it doesn't properly detect which beat is first, and for example remove 2nd beat every 4 beats instead. In that case, if you want 4th beat, use `shift = 2`. Also sometimes beats are detected right in between actual beats, so shift = 0.5 or -0.5 will fix it.
## creating images
You can create cool images based on beat positions. Each song produces its own unique image. This gradio app creates a 2048x2048 image from each song.
## presets
A bunch of example patterns: https://github.com/stunlocked1/beat_manipulator/blob/main/beat_manipulator/presets.yaml

Those are supposed to be used on normalized beat maps, where kick + snare is two beats, so make sure to adjust beatmaps using `scale` and `shift`.

# My soundcloud https://soundcloud.com/stunlocked
"""
 ).launch(share=False)