# stunlocked's beat manipulator
Advanced beat swapping powered by [madmom](https://github.com/CPJKU/madmom).
### [Try on Hugging Face](https://huggingface.co/spaces/dpe1/BeatManipulator)
### [Try on Google Colab](https://colab.research.google.com/drive/1gEsZCCh2zMKqLmaGH5BPPLrImhEGVhv3?usp=sharing)

## installation
For most people I recommend using Hugging Face or Google Colab. However if you want to run it locally and have access to more advanced features, here is how to do that.
1. Use python 3.8 - 3.10 (I use 3.9)
2. I recommend creating a new python environment to avoid dependency issues. With conda, run `conda create --name beat_manipulator`.
3. If you are using conda, run `conda install pip cython mido numpy scipy pysoundfile librosa ffmpeg-python pytest pyaudio pyfftw`. Then, if you have python 3.8 and 3.9 run `pip install madmom pedalboard`. If you have 3.10 run `pip install pedalboard`, and then install madmom from source as described on their github - [madmom](https://github.com/CPJKU/madmom). You will only have two pip packages - madmom and pedalboard. 
4. If you are using pip, run `pip install numpy cython soundfile ffmpeg-python pedalboard librosa`, and then `pip install madmom`.
5. After installing all necessary libraries, to download beat manipulator, download and extract this repo using green "Code" button > Download ZIP, or run `git clone https://github.com/stunlocked1/beat_manipulator`. You can now open examples.py, jupiter.ipynb, or app.py for gradio interface.

## usage
First, import beat_manipulator and load a song
```
import beat_manipulator as bm
your_song = bm.song(audio = 'path or numpy array')
```
It accepts absolute or relative path to audio file, or you can directly load audio array into it. If you are loading audio array directly, make sure to also add sr=sample_rate argument. Array should be in -1 to 1 format, which is how most libraries load audio.

Now, generate the beatmap:
```
your_song.beatmap_generate()
```
Beatmap is generated using madmom library. When you generate it for the first time, it might take up to a minute. However all beatmaps are saved to `beat_manipulator/beatmaps`, so when you load the same file for the second time, it will be instant.

You can access beatmap in `your_song.beatmap` variable. It is a list of values that represent position of each beat in samples.

After generating the beatmap, you can do a bunch of stuff. 
### slicing
Song object supports slicing - `your_song[5]` will return audio of the 5th beat (indexing starts from 0, so the first beat is the 0th beat). `your_song[4:8.5]` returns audio starting from 4th beat, ending halfway between 8th and 9th beat. `your_song['your_pattern']` returns a beatswapped audio using the pattern you provided. Patterns are the main feature if this app and you can do a whole bunch of stuff with them. There is a section below that explains how to write those patterns.

Another way to beatswap is `your_song.beatswap(pattern = '1, 3, 2, 4', scale = 1, shift = 0, length = None)`. This one doesn't return anything, instead it modifies the song in place.

### scale
`scale = 0.5` will insert a new beat position between every existing beat position in the beatmap. That allows you to make patterns on smaller intervals.

`scale = 2`, on the other hand, will merge every two beat positions in the beatmap. Useful, for example, when beat map detection puts sees BPM as two times faster than it actually is, and puts beats in between every actual beat.

To scale the beatmap, you can use `your_song.beatmap_scale(0.5)`, or specify scale directly in `your_song.beatswap(..., scale = float)`

### shift
Shifts the beatmap, in beats. For example, if you want to remove 4th beat every four beats, you can do it by writing `1, 2, 3, 4!`. 
However sometimes it doesn't properly detect which beat is first, and for example remove 2nd beat every 4 beats instead. In that case, if you want 4th beat, use `shift = 2`. Also sometimes beats are detected right in between actual beats, so shift = 0.5 or -0.5 will fix it.

To shift the beatmap, you can use `your_song.beatmap_shift(0.5)`, or specify shift directly in `your_song.beatswap(..., shift = float)`

### saving scale and shift
If you run `your_song.beatmap_save_settings(scale: float, shift: float)`, it will save a file in `beat_manipulator/beatmaps` with your scale and shift. That way, next time you load that song, it will automatically apply those scale and shift values.

### writing audio
To write audio, use `my_song.write(output = '')`. If output is empty string, this will write the song next to your .py file, using the original filename.

# pattern syntax
The pattern syntax is quite powerful and you can do a whole bunch of stuff with it. Basic syntax is - `1, 3, 2, 4` means every 4 beats, swap 2nd and 3rd beats, but you can do much more, like applying audio effects, shuffling beats, slicing them, mixing two songs, adding samples, sidechain.

You can use spaces freely in patterns for formatting. Most other symbols have some use though. Here is how to write patterns:
#### beats
- `1` meas the first beat. You can also slice beats:
- `1>0.5` means first half of first beat
- `1<0.5 means second half of first beat
- `0:0.5` - range of beats, this also means first half of first beat, but with this you can do complex stuff like `1.25:1.5`. However this one is a bit more confusing because indexing starts from 0, so 1:2 is second beat, not first.
- Also sometimes it is more convenient to use smaller `scale`, like 0.5 or 0.25, instead of slicing beats.
#### basic patterns
- `1, 3, 2, 4` means 3rd and 2nds beats will be swapped every 4 beats. Happens every 4 beats because 4 is the biggest number in the pattern.
- `1, 2, 3, 4!` means every 4 beats, it will remove the 4th beat. `!` allows you to skip a beat but it still counts for pattern size.
- Specifying pattern length: `pattern = '1,2,3', length = 4` is another way to remove 4th beat every 4 beats.
- `1,4` skips 2nd and 3rd beat
- `1; 2` plays 1st and 2nd beat same time. They will automatically be normalzied to avoid clipping. Length of the first beat will be preserved.
#### joining operators
`,` and `;` are beat joining operators, that join beats together. Here are all available joiners:
  - `,` puts the beat next to previous beat
  - `;` puts the beat on top of previous beat. Normalizes the volume to avoid clipping. If previous beat is shorter, your beat will be shortened to match it.
  - `^` multiplies previous beat by your beat. This can be used for fake sidechain.
  - `$` adds the beat on top of previous beat + sidechains previous beat by your beat.
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
You can also define your own effects. Check `BM_EFFECTS` dictionary from `beat_manipulator/effects.py`, this is where it reads effects from. You can add new stuff to that dictionary and use your own effects this way, or specify your own dictionary when using `your_song.beatswap(..., effects: dict)` with your `effects` argument. 
By default that argument points to `BM_EFFECTS` dictionary.
#### math
mathematical expressions with `+`, `-`, `*`, `/`, and `**` are supported. For example, if you write `1/3` anywhere in the pattern, to slice beats or as effect value, it will be replaced by 0.3333...
#### using samples
To use samples, provide them in `samples` argument to `your_song.beatswap(..., samples: dict)`. The dictionary should look like this: `{'sample name' : 'path to your sample or numpy array of your sample or bm.song object', 'sample2 name' : 'path or audio 2', ...}`. It supports both loading audio files from a path, and directly loading arrays.

Then in pattern, you can use quotes (`'`, `"`, or `` ` ``) to access samples. For example: `1; "sample_name"` will put that sample on top of 1st beat. Samples are treated just like beats, you can apply effects to them, use any joining operators.

You can also slice samples: `"sample_name">0.5` means first half of the sample.

You can use list with samples instead of a dictionary. In that case, you can access them by their index in the list, for example `"1"` is the 1st sample.
#### mixing two songs
Add the second song that you want to mix to the `samples` argument dictionary or list, as described above. It can load path to a file, directly load a numpy array, or a bm.song object.

The difference is, instead of using quotes, for songs you use square brackets: `[song_name]`

`[song_name]4` means fourth beat of that song. So you can do stuff like `1, [song_name]2`, which will alternate beats between your two songs.
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
You should be able to use all of the above operators in any combination, as complex as you want. Very low scales should also be fine, up to 0.001.

### creating images
You can create cool images based on beat positions. Each song produces its own unique image. Write:
```
your_song.image_generate()
```
image will be saved as a numpy array to your_song.image variable. To export it to a file, use:
```
your_song.image_write()
```
The image will by default be resized to 4096x4096. It is also possible to export original image, which usually is too big for most image viewers to handle it. However the cool thing is that you can apply image effects to it, and then turn it back into audio. I will soon add info on how to do that.

### quick functions
```
bm.beatswap(song = 'path or numpy array', pattern = '1,3,2,4', scale=1, shift=0, output='')
```
allows you to beatswap and write a song loaded from path or numpy array in one line. Returns path to the exported beatswapped song file.

```
bm.image(song = 'path or numpy array', max_size = 4096, scale=1, shift=0, output='')
```
creates an image and writes it in one line, returns path to exported image.

### patterns
some cool patterns are in `beat_manipulator/presets.yaml` file. Those are supposed to be used on normalized beat maps, where kick + snare is two beats, so make sure to adjust beatmaps using `scale` and `shift`.
To use one of the presets from that file, write: 
```
bm.presets.use(song = song, preset = 'preset name', scale = 1, shift = 0)
```
