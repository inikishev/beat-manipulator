import numpy as np, scipy.interpolate
from . import io, utils
from .effects import BM_EFFECTS
from .metrics import BM_METRICS
from .presets import BM_SAMPLES


class song:
    def __init__(self, audio = None, sr:int=None, log=True):
        if audio is None: 
            from tkinter import filedialog
            audio = filedialog.askopenfilename()
        
        if isinstance(audio, song): self.path = audio.path
        self.audio, self.sr = io._load(audio=audio, sr=sr)

        # unique filename is needed to generate/compare filenames for cached beatmaps
        if isinstance(audio, str):
            self.path = audio
        elif not isinstance(audio, song):
            self.path = 'unknown_' + str(hex(int(np.sum(self.audio)*(10**18))))

        self.log = log
        self.beatmap = None

    def _slice(self, a):
        if a is None: return None
        elif isinstance(a, float):
            if (a_dec:=a%1) != 0:
                a_int = int(int(a)//1)
                start = self.beatmap[a_int]
                return int(start + a_dec * (self.beatmap[a_int+1] - start))
            else:
                return self.beatmap[int(a)]
        elif isinstance(a, int): return self.beatmap[a]
        else: raise TypeError(f'slice indices must be int, float, or None, not {type(a)}. Indice is {a}')

    def __getitem__(self, s):
        if isinstance(s, slice): 
            start = s.start
            stop = s.stop
            step = s.step
            if start is not None and stop is not None:
                if start > stop:
                    is_reversed = -1
                    start, stop = stop, start
                else: is_reversed = None
            if step is None or step == 1:
                start = self._slice(start)
                stop = self._slice(stop)
                if isinstance(self.audio, list): return [self.audio[0][start:stop:is_reversed],self.audio[1][start:stop:is_reversed]]
                else: return self.audio[:,start:stop:is_reversed]
            else:
                i = s.start if s.start is not None else 0
                end = s.stop if s.stop is not None else len(self.beatmap)
                if i > end: 
                    step = -step
                    if step > 0: i, end = end-2, i
                elif step < 0: i, end = end-2, i
                if step < 0: 
                    is_reversed = True
                    end -= 1
                else: is_reversed = False
                pattern = ''
                while ((i > end) if is_reversed else (i < end)):
                    pattern+=f'{i},'
                    i+=step
                song_copy = song(audio = self.audio, sr = self.sr, log = False)
                song_copy.beatmap = self.beatmap.copy()
                song_copy.beatmap = np.insert(song_copy.beatmap, 0, 0)
                result = song_copy.beatswap(pattern = pattern, return_audio = True)
                if isinstance(self.audio, np.ndarray): return result
                else: return result.tolist()

        elif isinstance(s, float):
            start = self._slice(s-1)
            stop = self._slice(s)
            if isinstance(self.audio, list): return [self.audio[0][start:stop],self.audio[1][start:stop]]
            else: return self.audio[:,start:stop]
        elif isinstance(s, int):
            start = self.beatmap[s-1]
            stop = self.beatmap[s]
            if isinstance(self.audio, list): return [self.audio[0][start:stop],self.audio[1][start:stop]]
            else: return self.audio[:,start:stop]
        elif isinstance(s, tuple):
            start = self._slice(s[0])
            stop = self._slice(s[0] + s[1])
            if stop<0:
                start -= stop
                stop = -stop
                step = -1
            else: step = None
            if isinstance(self.audio, list): return [self.audio[0][start:stop:step],self.audio[1][start:stop:step]]
            else: return self.audio[:,start:stop:step]
        elif isinstance(s, list):
            start = s[0]
            stop = s[1] if len(s) > 1 else None
            if start > stop:
                step = -1
                start, stop = stop, start
            else: step = None
            start = self._slice(start)
            stop = self._slice(stop)
            if step is not None and stop is None: stop = self._slice(start + s.step)
            if isinstance(self.audio, list): return [self.audio[0][start:stop:step],self.audio[1][start:stop:step]]
            else: return self.audio[:,start:stop:step]
        elif isinstance(s, str):
            return self.beatswap(pattern = s, return_audio = True)

        
        else: raise TypeError(f'list indices must be int/float/slice/tuple, not {type(s)}; perhaps you missed a comma? Slice is `{s}`')


    def _print(self, *args, end=None, sep=None):
        if self.log: print(*args, end=end, sep=sep)


    def write(self, output='', ext='mp3', suffix=' (beatswap)', literal_output=False):
        """writes"""
        if literal_output is False: output = io._outputfilename(output, filename=self.path, suffix=suffix, ext=ext)
        io.write_audio(audio=self.audio, sr=self.sr, output=output, log=self.log)
        return output


    def beatmap_generate(self, lib='madmom.BeatDetectionProcessor', caching = True, load_settings = True):
        """Find beat positions"""
        from . import beatmap
        self.beatmap = beatmap.generate(audio = self.audio, sr = self.sr, lib=lib, caching=caching, filename = self.path, log = self.log, load_settings = load_settings)
        
        self.beatmap_default = self.beatmap.copy()
        self.lib = lib

    def beatmap_scale(self, scale:float):
        from . import beatmap
        self.beatmap = beatmap.scale(beatmap = self.beatmap, scale = scale, log = self.log)

    def beatmap_shift(self, shift:float, mode = 1):
        from . import beatmap
        self.beatmap = beatmap.shift(beatmap = self.beatmap, shift = shift, log = self.log, mode = mode)

    def beatmap_reset(self):
        self.beatmap = self.beatmap_default.copy()

    def beatmap_adjust(self, adjust = 500):
        self.beatmap = np.append(np.sort(np.absolute(self.beatmap - adjust)), len(self.audio[0]))

    def beatmap_save_settings(self, scale: float = None, shift: float = None, adjust: int = None, overwrite = 'ask'):
        from . import beatmap
        if self.beatmap is None: self.beatmap_generate()
        beatmap.save_settings(audio = self.audio, filename = self.path, scale = scale, shift = shift,adjust = adjust, log=self.log, overwrite=overwrite, lib = self.lib)

    def beatswap(self, pattern = '1;"cowbell"s3v2, 2;"cowbell"s2, 3;"cowbell", 4;"cowbell"s0.5, 5;"cowbell"s0.25, 6;"cowbell"s0.4, 7;"cowbell"s0.8, 8;"cowbell"s1.6', 
        scale:float = 1, shift:float = 0, length = None, samples:dict = BM_SAMPLES, effects:dict = BM_EFFECTS, metrics:dict = BM_METRICS, smoothing: int = 100, adjust=500, return_audio = False):
        
        pattern_text = pattern
        if self.beatmap is None: self.beatmap_generate()
        beatmap_default = self.beatmap.copy()
        self.beatmap = np.append(np.sort(np.absolute(self.beatmap - adjust)), len(self.audio[0]))
        self.beatmap_shift(shift)
        self.beatmap_scale(scale)
        
        from . import parse
        pattern, operators, pattern_length, shuffle_groups, shuffle_beats, c_slice, c_misc, c_join = parse.parse(pattern = pattern, samples = samples, pattern_length = length, log = self.log)
        
        #print(f'pattern length = {pattern_length}')

        # beatswap
        n=-1
        tries = 0
        metric = None
        result=[self.audio[:,:self.beatmap[0]]]
        #for i in pattern: print(i)

        # baked in presets
        #reverse
        if pattern_text.lower() == 'reverse':
            if return_audio is False:
                self.audio = self[::-1]
                self.beatmap = beatmap_default.copy()
                return
            else:
                result = self[::-1]
                self.beatmap = beatmap_default.copy()
                return result
        # shuffle
        elif pattern_text.lower() == 'shuffle':
            import random
            beats = list(range(len(self.beatmap)))
            random.shuffle(beats)
            beats = ','.join(list(str(i) for i in beats))
            if return_audio is False:
                self.beatswap(beats)
                self.beatmap = beatmap_default.copy()
                return
            else:
                result = self.beatswap(beats, return_audio = True)
                self.beatmap = beatmap_default.copy()
                return result
        # test
        elif pattern_text.lower() == 'test':
            if return_audio is False:
                self.beatswap('1;"cowbell"s3v2, 2;"cowbell"s2, 3;"cowbell", 4;"cowbell"s0.5, 5;"cowbell"s0.25, 6;"cowbell"s0.4, 7;"cowbell"s0.8, 8;"cowbell"s1.6')
                self.beatmap = beatmap_default.copy()
                return
            else:
                result = self.beatswap('1;"cowbell"s3v2, 2;"cowbell"s2, 3;"cowbell", 4;"cowbell"s0.5, 5;"cowbell"s0.25, 6;"cowbell"s0.4, 7;"cowbell"s0.8, 8;"cowbell"s1.6', return_audio = True)
                self.beatmap = beatmap_default.copy()
                return result
            
        
        # loop over pattern until it reaches the last beat
        while n*pattern_length <= len(self.beatmap):
            n+=1

            # Every time pattern loops, shuffles beats with #
            if len(shuffle_beats) > 0:
                pattern = parse._shuffle(pattern, shuffle_beats, shuffle_groups)

            # Loops over all beats in pattern
            for num, b in enumerate(pattern):
                if len(b) == 4: beat = b[3] # Sample has length 4
                else: beat = b[0] # Else take the beat

                if beat is not None:
                    beat_as_string = ''.join(beat) if isinstance(beat, list) else beat
                    # Skips `!` beats
                    if c_misc[9] in beat_as_string: continue

                # Audio is a sample or a song
                if len(b) == 4: 
                    audio = b[0]

                    # Audio is a song
                    if b[2] == c_misc[10]:
                        try:

                            # Song slice is a single beat, takes it
                            if isinstance(beat, str):
                                # random beat if `@` in beat (`_` is separator)
                                if c_misc[4] in beat: beat = parse._random(beat, rchar = c_misc[4], schar = c_misc[5], length = pattern_length)
                                beat = utils._safer_eval(beat) + pattern_length*n
                                while beat > len(audio.beatmap)-1: beat = 1 + beat - len(audio.beatmap)
                                beat = audio[beat]

                            # Song slice is a range of beats, takes the beats
                            elif isinstance(beat, list):
                                beat = beat.copy()
                                for i in range(len(beat)-1): # no separator
                                    if c_misc[4] in beat[i]: beat[i] = parse._random(beat[i], rchar = c_misc[4], schar = c_misc[5], length = pattern_length)
                                    beat[i] = utils._safer_eval(beat[i])
                                    while beat[i] + pattern_length*n > len(audio.beatmap)-1: beat[i] = 1 + beat[i] - len(audio.beatmap)
                                if beat[2] == c_slice[0]: beat = audio[beat[0] + pattern_length*n : beat[1] + pattern_length*n]
                                elif beat[2] == c_slice[1]: beat = audio[beat[0] - 1 + pattern_length*n: beat[0] - 1 + beat[1] + pattern_length*n]
                                elif beat[2] == c_slice[2]: beat = audio[beat[0] - beat[1] + pattern_length*n : beat[0] + pattern_length*n]

                            # No Song slice, take whole song
                            elif beat is None: beat = audio.audio

                        except IndexError as e:
                            print(e) 
                            tries += 1
                            if tries > 30: break
                            continue
                    
                    # Audio is an audio file
                    else:
                        # No audio slice, takes whole audio
                        if beat is None: beat = audio

                        # Audio slice, takes part of the audio
                        elif isinstance(beat, list):
                            audio_length = len(audio[0])
                            beat = [min(int(utils._safer_eval(beat[0])*audio_length), audio_length-1), min(int(utils._safer_eval(beat[1])*audio_length), audio_length-1)]
                            if beat[0] > beat[1]: 
                                beat[0], beat[1] = beat[1], beat[0]
                                step = -1
                            else: step = None
                            beat = audio[:, beat[0] : beat[1] : step]
                
                # Audio is a beat
                else:
                    try:
                        beat_str = beat if isinstance(beat, str) else ''.join(beat)
                        # Takes a single beat
                        if isinstance(beat, str):
                            if c_misc[4] in beat: beat = parse._random(beat, rchar = c_misc[4], schar = c_misc[5], length = pattern_length)
                            beat = self[utils._safer_eval(beat) + pattern_length*n]

                        # Takes a range of beats
                        elif isinstance(beat, list):
                            beat = beat.copy()
                            for i in range(len(beat)-1): # no separator
                                if c_misc[4] in beat[i]: beat[i] = parse._random(beat[i], rchar = c_misc[4], schar = c_misc[5], length = pattern_length)
                                beat[i] = utils._safer_eval(beat[i])
                            if beat[2] == c_slice[0]: beat = self[beat[0] + pattern_length*n : beat[1] + pattern_length*n]
                            elif beat[2] == c_slice[1]: beat = self[beat[0] - 1 + pattern_length*n: beat[0] - 1 + beat[1] + pattern_length*n]
                            elif beat[2] == c_slice[2]: beat = self[beat[0] - beat[1] + pattern_length*n : beat[0] + pattern_length*n]

                        # create a variable if `%` in beat
                        if c_misc[7] in beat_str: metric = parse._metric_get(beat_str, beat, metrics, c_misc[7])

                    except IndexError: 
                        tries += 1
                        if tries > 30: break
                        continue

                if len(beat[0])<1: continue #Ignores empty beats
                
                # Applies effects
                effect = b[1]
                for e in effect:
                    if e[0] in effects:
                        v = e[1]
                        e = effects[e[0]]
                        # parse effect value
                        if isinstance(v, str):
                            if metric is not None: v = parse._metric_replace(v, metric, c_misc[7])
                            v = utils._safer_eval(v)

                        # effects
                        if e == 'volume':
                            if v is None: v = 0
                            beat = beat * v
                        elif e == 'downsample':
                            if v is None: v = 8
                            beat = np.repeat(beat[:,::v], v, axis=1)
                        elif e == 'gradient':
                            beat = np.gradient(beat, axis=1)
                        elif e == 'reverse':
                            beat = beat[:,::-1]
                        else:
                            beat = e(beat, v)

                beat = np.clip(beat, -1, 1)
                
                # Adds the processed beat to list of beats.
                # Separator is `,`
                if operators[num] == c_join[0]:
                    result.append(beat)
                
                # Makes sure beat doesn't get added on top of previous beat multiple times when pattern is out of range of song beats, to avoid distorted end.
                elif tries<2:
                    # Separator is `;` - always use first beat length
                    if operators[num] == c_join[1]:
                        length = len(beat[0])
                        prev_length = len(result[-1][0])
                        if length > prev_length: 
                            result[-1] += beat[:,:prev_length]
                        else:
                            result[-1][:,:length] += beat
                    
                    # Separator is `~` - cuts to shortest
                    elif operators[num] == c_join[2]:
                        minimum = min(len(beat[0]), len(result[-1][0]))
                        result[-1] = beat[:,:minimum-1] + result[-1][:,:minimum-1]

                    # Separator is `&` - extends to longest
                    elif operators[num] == c_join[3]:
                        length = len(beat[0])
                        prev_length = len(result[-1][0])
                        if length > prev_length: 
                            beat[:,:prev_length] += result[-1]
                            result[-1] = beat
                        else:
                            result[-1][:,:length] += beat

                    # Separator is `^` - uses first beat length and multiplies beats, used for sidechain
                    if operators[num] == c_join[4]:
                        length = len(beat[0])
                        prev_length = len(result[-1][0])
                        if length > prev_length: 
                            result[-1] *= beat[:,:prev_length]
                        else:
                            result[-1][:,:length] *= beat

                    # Separator is `$` - always use first beat length, normalizes volume to 1.5
                    if operators[num] == c_join[5]:
                        length = len(beat[0])
                        prev_length = len(result[-1][0])
                        if length > prev_length: 
                            result[-1] += beat[:,:prev_length]
                        else:
                            result[-1][:,:length] += beat
                        limit = np.max(result[-1])
                        if limit > 1.5:
                            result[-1] /= limit*0.75

                    # Separator is `}` - always use first beat length, additionally sidechains first beat by second
                    if operators[num] == c_join[6]:
                        from . import effects
                        length = len(beat[0])
                        prev_length = len(result[-1][0])
                        if length > prev_length: 
                            result[-1] *= effects.to_sidechain(beat[:,:prev_length])
                            result[-1] += beat[:,:prev_length]
                        else:
                            result[-1][:,:length] *= effects.to_sidechain(beat)
                            result[-1][:,:length] += beat
        # smoothing
        for i in range(len(result)-1):
            current1 = result[i][0][-2]
            current2 = result[i][0][-1]
            following1 = result[i+1][0][0]
            following2 = result[i+1][0][1]
            num = (abs(following1 - (current2 + (current2 - current1))) + abs(current2 - (following1 + (following1 - following2))))/2
            if num > 0.0: 
                num = int(smoothing*num)
                if num>3:
                    try:
                        line = scipy.interpolate.CubicSpline([0, num+1], [0, following1], bc_type='clamped')(np.arange(0, num, 1))
                        #print(line)
                        line2 = np.linspace(1, 0, num)**0.5
                        result[i][0][-num:] *= line2
                        result[i][1][-num:] *= line2
                        result[i][0][-num:] += line
                        result[i][1][-num:] += line
                    except (IndexError, ValueError): pass

        self.beatmap = beatmap_default.copy()
        # Beats are conjoined into a song
        import functools
        import operator
        # Makes a [l, r, l, r, ...] list of beats (left and right channels)
        result = functools.reduce(operator.iconcat, result, [])

        # Every first beat is conjoined into left channel, every second beat is conjoined into right channel
        if return_audio is False: self.audio = np.array([functools.reduce(operator.iconcat, result[::2], []), functools.reduce(operator.iconcat, result[1:][::2], [])])
        else: return np.array([functools.reduce(operator.iconcat, result[::2], []), functools.reduce(operator.iconcat, result[1:][::2], [])])


    def image_generate(self, scale=1, shift=0, mode = 'median'):
        if self.beatmap is None: self.beatmap_generate()
        beatmap_default = self.beatmap.copy()
        self.beatmap_shift(shift)
        self.beatmap_scale(scale)
        from .image import generate as image_generate
        self.image = image_generate(song = self, mode = mode, log = self.log)
        self.beatmap = beatmap_default.copy()

    def image_write(self, output='', mode = 'color', max_size = 4096, ext = 'png', rotate=True, suffix = ''):
        from .image import write as image_write
        output = io._outputfilename(output, self.path, ext=ext, suffix = suffix)
        image_write(self.image, output = output, mode = mode, max_size = max_size , rotate = rotate)
        return output



def beatswap(audio = None, pattern = 'test', scale = 1, shift = 0, length = None, sr = None, output = '', log = True, suffix = ' (beatswap)', copy = True):
    if not isinstance(audio, song): audio = song(audio = audio, sr = sr, log = log)
    elif copy is True: 
        beatmap = audio.beatmap
        path = audio.path
        audio = song(audio = audio.audio, sr = audio.sr)
        audio.beatmap = beatmap
        audio.path = path
    audio.beatswap(pattern = pattern, scale = scale, shift = shift, length = length)
    if output is not None: 
        return audio.write(output = output, suffix = suffix)
    else: return audio

def image(audio, scale = 1, shift = 0, sr = None, output = '', log = True, suffix = '', max_size = 4096):
    if not isinstance(audio, song): audio = song(audio = audio, sr = sr, log = log)
    audio.image_generate(scale = scale, shift = shift)
    if output is not None: 
        return audio.image_write(output = output, max_size=max_size, suffix=suffix)
    else: return audio.image