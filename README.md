## dpe's beat manipulator
Advanced beat swapping powered by madmom https://github.com/CPJKU/madmom

# Basic how to use
BeatManipulator.py is the only file you need. Put it next to your .py file so that you can import it (if it errors also put ffmpeg.exe next to it). Copy the following into your .py:
```
import BeatManipulator as bm
bm.beatswap(pattern='1,3,2,4')
```
It will let you pick an audio file, analyze it using madmom, and swap every 2nd and 3rd beats. Analyzing beats for the first time will take some time, but it also saves beatmaps, so opening already analyzed file is much faster.

You can also specify audio file to be opened: `bm.beatswap(filename='/path/to/file', pattern='1,3,2,4')`

By default processed audio will be outputted into the same folder as your .py file, and will use original file name with a `_bm` suffix. To change that, specify output parameter: 
`bm.beatswap(pattern='1,3,2,4', output='/path/to/output')`, or add file extension to override filename: `bm.beatswap(pattern='1,3,2,4', output='/path/to/output/output.mp3')`

Alternatively you can import/export audio directly with pedalboard or any other library. Make sure the audio array looks similar to `[[-0.4, 0.3, ...],[-0.3, 1, ...]]`, which is how pedalboard imports it.

Another useful parameter is scale: `bm.beatswap(pattern='1,3,2,4', scale=0.5)` - that means all beats will be 2 times smaller.

# Pattern syntax
Patterns are sequences of numbers or ranges, separated by `,`. Numbers and ranges can be followed by letters that apply effects to them. Spaces can be freely used for formatting as they will be ignored. Any other character that isn't used in the syntax can also be used for formatting but only between beats, not inside them.
- `'1, 3, 2, 4'` - every 4 beats, swap 2nd and 3rd beat. This pattern loops every 4 beats, because 4 is the biggest number in it.
- `!` after a number makes the pattern loop this amount of times. `'1, 3, 2, 4, 8!'` - every 8 beats, swap 2nd and 3rd beat.
- `'1, 3, 4'` - skip 2nd beat
- `'1,2,2,3'` - repeat 2nd beat
- `'1, 1:1.5, 4'` - play a range of beats. `0:0.5` means first half of 1st beat. Keep that in mind, to play first half of 5th beat, you do `4:4.5`, not `5:5.5`. `1` is equivalent to `0:1`. `1.5` is equivalent to `0.5:1.5`. `1,2,3,4` is `0:4`.
- `'1, 0:1/3, 0:1/3, 2/3:1'` - you can use expressions with `+`, `-`, `*`, `/`.
- `?` after a beat makes that number not count for looping. `'1, 2, 3, 4!, 8?'` every 4 beats, 4th beat is replaced with 8th beat.
- `v` and a number after a beat changes volume of that beat. `'1v2'` means 200% volume, `1v1/3` means 33.33% volume, etc.
- `r` after a beat reverses that beat. `'1r, 2'` - every two beats first beat will be reversed
- another way to reverse - `4:0` is reversed `0:4`.
- `s` after a beat changes speed and pitch of that beat. 2 will be 2 times faster, 1/2 will be 2 times slower. Note: Only integers or 1/integer numbers are supported, everything else will be rounded.
- `c` - swaps left and right channels of the beat

### Other
There are also functions to play a sound every x beats or to sidechain every x beats, soon

# Notes
- libraries used - `madmom` for BPM detection, `pedalboard.io` for import/export, `numpy` for most effects including beatswapping.
- this was coded by Big ounce, gort and Quandale dingle
- will work on python 3.9, maybe lower, not higher because of madmom, also if it doesn't work download and put ffmpeg.exe next to your .py file
