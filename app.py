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
scalebox = Textbox(value=1, label="Beatmap scale. At 2, every two beats will be merged, at 0.5 - a beat added between every two beats.", placeholder=1, lines=1)
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

Upload your audio, enter the beat swapping pattern, change scale and shift if needed, and run the app.

It can be useful to test where each beat is by writing `test` into the `pattern` field, which will put cowbells on each beat. Highest cowbell should be the on first beat.

Use scale and shift to adjust the beatmap, for example if it is shifted 0.5 beats forward, set shift to -0.5. If it is two times faster than you want, set scale to 0.5

Feel free to use complex patterns and very low scales - most of the computation time is in detecting beats, not swapping them.

# Pattern syntax

Patterns are sequences of expressions, separated by `,` - for example, `1>3/8,   1>3/8,   1>0.25,   2,   3>0.75s2,   3>3/8,   3>0.25,   4d9`. Spaces can be freely used for formatting as they will be ignored. Any other character that isnt used in the syntax can also be used for formatting but only between beats, not inside them.
- `1, 3, 2, 4` - every 4 beats, swap 2nd and 3rd beat. This pattern loops every 4 beats, because 4 is the biggest number in it.
- `1, 3, 4` - every 4 beats, skip 2nd beat.
- `1, 2, 2, 4` - every 4 beats, repeat 2nd beat.
- `1, 2!` - skip every second beat. `!` after a number sets length of the pattern (beat isnt played). `1, 2, 3, 4!` - skip every 4th beat.
- `2>0.5` - play only first half of the second beat. `>` after a beat allows you to take first `i` of that beat.
- `2<0.5` - play only second half of the second beat. `<` after a beat takes last `i` of that beat.
- `1.5:4.5` - play a range of beats from 1.5 to 4.5. `0:0.5` means first half of 1st beat. Keep that in mind, to play first half of 5th beat, you do `4:4.5`, not `5:5.5`. `1` is equivalent to `0:1`. `1.5` is equivalent to `0.5:1.5`. `1,2,3,4` is `0:4`.

**Tip: instead of slicing beats, sometimes it is easier to make scale smaller, like 0.5 or 0.25.**
- `1, 1>1/3, 1>1/3, 1<1/3` - you can use math expressions with `+`, `-`, `*`, `/` in place of numbers.
- `1, 2, 3, 4!, 8?` - every 4 beats, 4th beat is replaced with 8th beat. `?` after a beat makes that number not count for looping. 
- `v` + number - controls volume of that beat. `1v2` means 200% volume, `1v1/3` means 33.33% volume, etc.
- `r` after a beat reverses that beat. `1r, 2` - every two beats, first beat will be reversed
- another way to reverse - `4:0` is reversed `0:4`.
- `s` + number - changes speed and pitch of that beat. 2 will be 2 times faster, 1/2 will be 2 times slower. Note: Only integers or 1/integer numbers are supported, everything else will be rounded.
- `c` - if not followed by a number, swaps left and right channels of the beat. If followed by 0, mutes left channel, 1 - right channel.
- `b` + number - bitcrush. The higher the number, the stronger the effect. Barely noticeable at values less then 1
- `d` + number - downsample (8-bit sound). The higher the number, the stronger the effect. Starts being noticeable at 3, good 8-bit sounding values are around 8+.
- `t` + number - saturation
- you can combine stuff like `0:1/3d8v2cr` - that line means 0:1/3 beat will be downsampled, 200% volume, swapped channels, and reversed

there are certain commands you can write in pattern instead of the actual pattern:
- `random` - each beat will be randomly selected from all beats, basically similar to shuffling all beats
- `reverse` - reverses the order of all beats
- `test` - test beat detection by putting cowbells on each beat. The highest pitched cowbell should be on the first beat; next cowbell should be on the snare. If it is not, use scale and shift.

There are also some interesting patterns there: https://github.com/stunlocked1/BeatManipulator/blob/main/presets.json. Those are meant to be used with properly adjusted shift and scale, where 1st beat is 1st kick, 2nd beat is the snare after it, etc.

Check my soundcloud https://soundcloud.com/stunlocked
"""
 ).launch(share=False)