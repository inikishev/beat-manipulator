# BigOuncesAudioEffects
Beat swapping and a whole bunch of other audio effects and stuff you can try with your music. Big ounce hasn't finished coding this one yet. Don't worry, he is being helped by none other than Gort and Quandale Dingle. Your beatswapping desires will be fulfilled very soon.

# How to use
BigOuncesAudioEffects.py is the only file you need (put it next to your .py file so that you can import it). Copy the following into your .py, change 'path/to/audio', and it shall work.
```import BigOuncesAudioEffects as ba
# open the audio file with pedalboard:
(audio, samplerate)=ba.r_pedalboard('path/to/audio')
# break it into beats with madmom
beats=ba.beats_madmom_constant('path/to/audio', samplerate) # yes it needs to open the file again, i will fix that at some point
# apply effects (removes every 2nd and 4th beat)
beatswap(audio, beats, '1,3,4-)
# export audio
ba.w_pedalboard(audio, samplerate, output='pedalboard_output.mp3')
```
You can import/export a file directly with pedalboard or any other library. You can also use beat detection directly from madmom or anything else. Just multiply beats by samplerate because madmom stores them in seconds and I store them in samples.

# Notable implemented effects:
### beatswap(audio, beats, swap:str,  scale=1, shift=0, smoothing=50)
make "every other beat is missing/swapped" type remixes
- **audio** - audio in numpy array format, you can get it using `(audio, samplerate)=ba.r_pedalboard('path/to/audio')`
- **beats** - beats in numpy array format, obtain using madmom: `beats=ba.beats_madmom_constant('path/to/audio', samplerate)`
- **swap** - a string with numbers separated by commas, that represents the order of the beats. For example '1,4,3', where biggest number is 4, so the order will repeat every 4 beats. To remove the last beat, add '-' after it, like '1,2,3,4-'. More functions will come later. You can also use spaces and brackets for formatting, they will be ignored.
- **scale** (optional) - this converts beats, for example if it is set to 0.5 it will convert every beat to two beats, and vice versa. It even supports uneven fractions.
- **shift** (optional) - shifts all beats, because sometimes first beat isn't actually the first in the song (only supports integers)
- **smoothing** (optional) - removes clicking where beats are stitched together, default value is 50.
#### examples:
`audio=ba.beatswap(audio, beats, '1,3,2,4')` - swaps every 2nd and 3rd beat
`audio=ba.beatswap(audio, beats, '1,3,4')` - removes 2nd beat every 4 beats
`audio=ba.beatswap(audio, beats, '1,2,3,4-')` - removes every 4th beat
`audio=ba.beatswap(audio, beats, '8')` - plays only every 8th beat

### b_each(audio, audio2, beats, scale=1, shift=0)
play a sample every n beats
- **audio** - song audio in numpy array format, you can get it using `(audio, samplerate)=ba.r_pedalboard('path/to/audio')`
- **audio2** - sample audio in numpy array format, same deal
- **beats** - beats in numpy array format, obtain using madmom: `beats=ba.beats_madmom_constant('path/to/audio', samplerate)`
- **scale** (optional) - if set to 0.5 it will play sample every 0.5 beats and so on.
- **shift** (optional) - amount of beats to shift samples by. For example at 0.3 samples will be played on 1.3 beat, 2.3 beat and so on.
#### example:
```audio=ba.b_each(audio, kick, beats) # kick plays every beat
audio=ba.b_each(audio, snare, beats, scale=2, shift=1) # snares 
audio=ba.b_each(audio, hhat, beats, scale=0.5) # highhats every 0.5 beats``` - adds basic 4/4 beat to any song. If you find good samples it could make nice nightcore or something.
Note - samples are added to the song which will probably cause clipping. I will fix at some point and also add sidechaining.
