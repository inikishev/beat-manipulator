## dpe's beat manipulator
Advanced beat swapping, WIP

# Basic how to use
BeatManipulator.py is the only file you need (put it next to your .py file so that you can import it, also put ffmpeg.exe next to it if it asks). Copy the following into your .py, change `'path/to/audio'`, and it shall work.
```
import BeatManipulator as bm
# open the audio file with pedalboard:
(audio, samplerate)=bm.r_pedalboard('path/to/audio')
# break it into beats with madmom
beats=bm.beats_madmom_constant('path/to/audio', samplerate) # yes it needs to open the file again, i will fix that at some point
# apply effects (removes every 2nd and 4th beat)
audio=bm.beatswap(audio, beats, '1,3,4-`)
# export audio
bm.w_pedalboard(audio, samplerate, output='pedalboard_output.mp3')
```
Alternatively you can import/export audio directly with pedalboard or any other library. You can also use beat detection directly from madmom or anything else. Just multiply beats by samplerate because madmom stores them in seconds and I store them in samples.

# Notable implemented effects:
### beatswap(audio, beats, swap:str,  scale=1, shift=0, smoothing=50)
make "every other beat is missing/swapped" type remixes
- **audio** - audio in numpy array format, you can get it using `(audio, samplerate)=bm.r_pedalboard('path/to/audio')`
- **beats** - beats in numpy array format, obtain using madmom: `beats=bm.beats_madmom_constant('path/to/audio', samplerate)`
- **swap** - a string with numbers separated by commas, that represents the order of the beats. It has a hole Bunch of other functions as well. The syntax is explained below.
- **scale** (optional) - this converts beats, for example if it is set to 0.5 it will convert every beat to two beats, and vice versa. It even supports uneven fractions.
- **shift** (optional) - shifts all beats, because sometimes first beat isn't actually the first in the song (only supports integers)
- **smoothing** (optional) - removes clicking where beats are stitched together, default value is 50.
#### swap syntax
It is a string with integers separated by commas. Spaces can be used for formatting as they will be ignored. Example: `'4,1,1'`. That would mean it will play 4st, 1st, and 1st beat. Then it will loop and 8th, 5th, and 5th beats, and so on. It looped 4 beats because 4 was the biggest number in the sequence.

`-` after a number removes that beat. For example, `'1, 2-, 3, 4'` means 2nd beat is removed, which is equvalent to `'1, 3, 4'`. However it is useful when you want to remove the last beat: `'1, 2, 3, 4-'` will properly loop 4 beats, while `'1, 2, 3'` will loop 3 beats and do nothing.

`r` after a number means that beat will be reversed. Example: `'1, 2r'` - every second beat will be reversed.

`c` after a number allows you to cut that beat, must be followed by new `swap` string in brackets. Example: `'1, 2c(1, 2r, 4-), 3, 4`. That will cut 2nd beat into 4 parts and run all commands inside brackets. `c(1, 2-)` will cut beat in half; `c(1r, 2)` will reverse 1st half of the beat, etc. You can't do cut inside cut tho because there is no point. Also an alternative to cut is reducing the scale parameter.

`l` - makes beat loud, useful for understanding which beat is which

`m` - mutes the beat

#### examples:
`audio=ba.beatswap(audio, beats, '1, 3, 2, 4')` - swaps every 2nd and 3rd beat

`audio=ba.beatswap(audio, beats, '1, 2, 4')` - removes 3nd beat every 4 beats

`audio=ba.beatswap(audio, beats, '1, 2, 4-')` - removes every 3rd and 4th beat every 4 beats

`audio=ba.beatswap(audio, beats, '1, 1')` - plays every beat two times

`audio=ba.beatswap(audio, beats, '8')` - plays only every 8th beat

`audio=ba.beatswap(audio, beats, '1r')` - reverses every beat

`audio=ba.beatswap(audio, beats, '1c(1, 2-)' )` - cuts every beat in half

`audio=ba.beatswap(audio, beats, '1c(1r 2r)' )` - reverses every half-beat


### b_each(audio, audio2, beats, scale=1, shift=0)
play a sample every n beats
- **audio** - song audio in numpy array format, you can get it using `(audio, samplerate)=bm.r_pedalboard('path/to/audio')`
- **audio2** - sample audio in numpy array format, same deal
- **beats** - beats in numpy array format, obtain using madmom: `beats=ba.beats_madmom_constant('path/to/audio', samplerate)`
- **scale** (optional) - if set to 0.5 it will play sample every 0.5 beats and so on.
- **shift** (optional) - amount of beats to shift samples by. For example at 0.3 samples will be played on 1.3 beat, 2.3 beat and so on.
#### example:
```
audio=bm.b_each(audio, kick, beats) # kick plays every beat
audio=bm.b_each(audio, snare, beats, scale=2, shift=1) # snares 
audio=bm.b_each(audio, hhat, beats, scale=0.5) # highhats every 0.5 beats
```
adds basic 4/4 beat to any song. If you find good samples it could make nice nightcore or something.
Note - samples are added to the song which will probably cause clipping. I will fix at some point and also add sidechaining.


### Other
there are a ton of other effects but they are all kinda boring like volume. There are some weird saturation effects. I will add them here at some point

# Notes
- libraries used - `madmom` for BPM detection, `numpy` for most effects including beatswapping.
- this was coded by Big ounce, gort and Quandale dingle
- will work on python 3.9, maybe lower, not higher because of madmom, also if it doesn't work download and put ffmpeg.exe next to your .py file
- I started porting it from numpy to .extend() which is like 100 times faster.
