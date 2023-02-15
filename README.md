(Никишев И.О.)

Advanced beat swapping powered by [madmom](https://github.com/CPJKU/madmom). Effortlessly make "every other beat is missing" remixes, or completely change beat of the song with patterns as complex you want. Additional remixing features include putting samples and fake sidechain on each beat.

# Requirements
- tested on python 3.10, 3.9 and 3.8. Note that currently only github version of madmom seems to work on 3.10 (at least I couldn't get pip version to work on 3.10).
- packages: `numpy`, `madmom`, `ffmpeg-python`, `soundfile`, `pedalboard`
- if you get file not found error, put ffmpeg.exe next to your .py file - https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip

Quick commands to install those packages at the bottom.

# Basic how to use
**Download the repo and open Jupiter.ipynb.**

Alternatively put BeatManipulator.py next to your .py file so that you can import it. Copy the following into your .py:
```
import BeatManipulator as bm
song=bm.song() # open a song
song.quick_beatswap(output='', pattern='1, 3, 2, 4', scale=1, shift=0) # beatswap and export
```
It will let you pick an audio file, analyze it using madmom, and swap every 2nd and 3rd beats. Analyzing beats for the first time will take some time, but it also saves beatmaps, so opening already analyzed file is much faster.

You can specify audio file to be opened:
```
song=bm.song('/path/to/file.mp3')
```

By default processed audio will be outputted into the same folder as your .py file, and will use original file name with a `_bm` suffix. To change that, specify output parameter: `output='/path/to/output')`, or add file extension to override filename: `output='/path/to/output/file.mp3')`

Set output to None if you don't want to write the audio: `song.quick_beatswap(output=None, pattern='0, 3, 2, 4', scale=1, shift=0)`

Useful parameters for quick_beatswap: `scale=0.5` that means all beats will be 2 times smaller. `shift=-0.5` means pattern will be shifted 0.5 scaled beats left. `start`, `end` take a number of seconds and only beats in that interval will be processed.

# Pattern syntax
Patterns are sequences of numbers or ranges, separated by `,`. Numbers and ranges can be followed by letters that apply effects to them. Spaces can be freely used for formatting as they will be ignored. Any other character that isn't used in the syntax can also be used for formatting but only between beats, not inside them.
- `'1, 3, 2, 4'` - every 4 beats, swap 2nd and 3rd beat. This pattern loops every 4 beats, because 4 is the biggest number in it.
- `!` after a number sets length of the pattern (beat isn't played). `'1, 3, 2, 4, 8!'` - every 8 beats, swap 2nd and 3rd beat, and 5-8 beats will be skipped.
- `'1, 3, 4'` - skip 2nd beat
- `'1, 2, 2, 4'` - repeat 2nd beat
- `'1, 1:1.5, 4'` - play a range of beats. `0:0.5` means first half of 1st beat. Keep that in mind, to play first half of 5th beat, you do `4:4.5`, not `5:5.5`. `1` is equivalent to `0:1`. `1.5` is equivalent to `0.5:1.5`. `1,2,3,4` is `0:4`.
- `'1, 0:1/3, 0:1/3, 2/3:1'` - you can use expressions with `+`, `-`, `*`, `/`.
- `?` after a beat makes that number not count for looping. `'1, 2, 3, 4!, 8?'` - every 4 beats, 4th beat is replaced with 8th beat.
- `v` + number - controls volume of that beat. `'1v2'` means 200% volume, `1v1/3` means 33.33% volume, etc.
- `r` after a beat reverses that beat. `'1r, 2'` - every two beats first beat will be reversed
- another way to reverse - `4:0` is reversed `0:4`.
- `s` + number - changes speed and pitch of that beat. 2 will be 2 times faster, 1/2 will be 2 times slower. Note: Only integers or 1/integer numbers are supported, everything else will be rounded.
- `c` - swaps left and right channels of the beat. If followed by 0, mutes left channel instead, 1 - right channel.
- `b` + number - bitcrush. The higher the number, the stronger the effect. Barely noticeable at values less then 1
- `d` + number - downsample (8-bit sound). The higher the number, the stronger the effect. Starts being noticeable at 3, good 8-bit sounding values are around 8+.
- `t` + number - saturation
- you can combine stuff like `0:1/3d8v2cr` - that line means 0:1/3 beat will be downsampled, 200% volume, swapped channels, and reversed

there are certain commands you can write in pattern instead of the actual pattern:
- `random` - each beat will be randomly selected from all beats, basically similar to shuffling all beats
- `reverse` - reverses the order of all beats
- `test` - test beat detection by putting cowbells on each beat. The highest pitched cowbell should be on the first beat; next cowbell should be on the snare.

### Other
`song.quick_beatsample(output='', filename2=None, scale=1, shift=0, start=0, end=None, autotrim=True, autoscale=False, autoinsert=False):` - puts a filename2 (or audio2) sample on each beat. If you don't provide filename2, a file explorer will open.

`song.quick_sidechain(output='', audio2=None, scale=1, shift=0, start=0, end=None, autotrim=True, autoscale=False, autoinsert=False)` - puts fake sidechain (fade in) on each beat. audio2 (or filename2) is the sidechain impulse, if not specified, it will be generated. Or you can manually generate it with `bm.generate_sidechain(samplerate=44100, len=0.5, curve=2, vol0=0, vol1=1)`. This one will be 0.5 seconds, 0% -> 100% volume fade in, with a minor curve.

`song.write_audio(output, lib='pedalboard.io')` - writes the audio. You are less likely to need this because all quick functions write audio already, unless `output` is set to `None`. This one doesn't automatically generate an output string, so make sure output ends with `.mp3` or `.wav`.

`bm.fix_beatmap(filename, lib='madmom.BeatDetectionProcessor', scale=1, shift=0)` - `filename` is path to the song, this function loads the songs beatmap, applies shift and scale to it and writes it back to SavedBeatmaps, where cached beatmaps are saved. Basically this permanently applies scale and shift to a beatmap.

`wrapper.py` and `presets.json` are basically my examples of using this library. They will eventually turn into a GUI app so that actual people can use it as well. `presets.json` has some cool patterns!

```
song=bm.song(filename)
song.generate_hitmap()
song.osu()
```
will generate an osu beatmap. The .osz file that you can open with osu will be put next to the .py file

There is more stuff. I will write how to use that later

# Notes
- libraries used - `madmom` for beat detection, `librosa` and `pedalboard.io` for import/export, `numpy` for some effects

# Installing requirements
### pip
- `pip install numpy cython soundfile ffmpeg-python pedalboard librosa`
- `pip install madmom`
### conda
- you need conda forge channel: `conda config --append channels conda-forge`
- some requirements are pip only, so you might want to create a new environment
- `conda install pip cython mido numpy scipy pysoundfile librosa ffmpeg pytest pyaudio pyfftw`
- either `pip install madmom pedalboard`, or follow https://github.com/CPJKU/madmom instructions for manual install if you are on 3.10
- You will have exactly 2 pip packages, madmom and pedalboard, all dependencies will be from conda.
