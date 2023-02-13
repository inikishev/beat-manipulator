import numpy
numpy.set_printoptions(suppress=True)

def open_audio(filename=None, lib='auto'):
    if filename is None:
        from tkinter.filedialog import askopenfilename
        filename = askopenfilename(title='select song', filetypes=[("mp3", ".mp3"),("wav", ".wav"),("flac", ".flac"),("ogg", ".ogg"),("wma", ".wma")])
    filename=filename.replace('\\', '/')
    if lib=='pedalboard.io':
        import pedalboard.io
        with pedalboard.io.AudioFile(filename) as f:
            audio = f.read(f.frames)
            samplerate = f.samplerate
    elif lib=='librosa':
        import librosa
        audio, samplerate = librosa.load(filename, sr=None, mono=False)
    elif lib=='soundfile':
        import soundfile
        audio, samplerate = soundfile.read(filename)
        audio=audio.T
    elif lib=='madmom':
        import madmom
        audio, samplerate = madmom.io.audio.load_audio_file(filename, dtype=float)
        audio=audio.T
    # elif lib=='pydub':
    #     from pydub import AudioSegment
    #     song=AudioSegment.from_file(filename)
    #     audio = song.get_array_of_samples()
    #     samplerate=song.frame_rate
    #     print(audio)
    #     print(filename)
    elif lib=='auto':
        for i in ('madmom', 'soundfile', 'librosa', 'pedalboard.io'):
            try: 
                audio,samplerate=open_audio(filename, i)
                break
            except Exception as e:
                print(f'open_audio with {i}: {e}')
    if len(audio)<2: audio=[audio,audio]
    return audio,samplerate


def generate_sidechain(samplerate=44100, length=0.5, curve=2, vol0=0, vol1=1, smoothing=40) ->numpy.array:
    x=numpy.concatenate((numpy.linspace(1,0,smoothing),numpy.linspace(vol0,vol1,int(length*samplerate))**curve))
    return(x,x)

def outputfilename(output, filename, suffix=' (beatswap)', ext='mp3'):
    if not (output.lower().endswith('.mp3') or output.lower().endswith('.wav') or output.lower().endswith('.flac') or output.lower().endswith('.ogg') or 
            output.lower().endswith('.aac') or output.lower().endswith('.ac3') or output.lower().endswith('.aiff')  or output.lower().endswith('.wma')):
                return output+'.'.join(''.join(filename.split('/')[-1]).split('.')[:-1])+suffix+'.'+ext
    

def generate_sine(len, freq, samplerate, volume=1):
    return numpy.sin(numpy.linspace(0, freq*3.1415926*2*len, int(len*samplerate)))*volume

def generate_saw(len, freq, samplerate, volume=1):
    return (numpy.linspace(0, freq*2*len, int(len*samplerate))%2 - 1)*volume

def generate_square(len, freq, samplerate, volume=1):
    return ((numpy.linspace(0, freq*2*len, int(len*samplerate)))//1%2 * 2 - 1)*volume

def effect_normalize(audio):
    audio=audio-(numpy.min(audio)+numpy.max(audio))/2
    return audio*(1-(max(numpy.max(audio), abs(numpy.min(audio)))))

def effect_pitch(audio, pitch, grain):
    grain=int(grain)
    if len(audio)>10: audio=[audio]
    if type(audio) is not list: audio=audio.tolist()
    length=len(audio[0])
    if pitch<1:
        pitch=int(1//pitch)
        if grain%2!=0: grain+=1
        for i in range(len(audio)):
            n=0
            while n+grain<length:
                #print(len(audio[i]))
                #print(n)
                audio[i][n:n+grain]=numpy.repeat(audio[i][n:n+int(grain/2)], 2)
                #print(len(audio[i]))
                n+=grain
    elif pitch>1:
        pitch=int(pitch)
        for i in range(len(audio)):
            n=0
            while n+grain<length:
                audio[i][n:n+grain]=audio[i][n:n+grain:pitch]*pitch
                n+=grain
    return audio

def effect_pitchB(audio, pitch, grain):
    grain=int(grain)
    if len(audio)>10: audio=[audio]
    if type(audio) is not list: audio=audio.tolist()
    length=len(audio[0])
    if pitch<1:
        pitch=int(1//pitch)
        if grain%2!=0: grain+=1
        for i in range(len(audio)):
            n=0
            while n+grain<length:
                #print(len(audio[i]))
                #print(n)
                audio[i][n:n+grain]=numpy.repeat(audio[i][n:n+int(grain/2)], 2)
                #print(len(audio[i]))
                n+=grain

    elif pitch>1:
        pitch=int(pitch)
        for i in range(len(audio)):
            n=0
            while n+grain<length:
                audio2=audio[i][n:n+grain:pitch]
                for j in range(pitch-1):
                    #print(j)
                    audio2.extend(audio2[::1] if j%2==1 else audio2[::-1])
                audio[i][n:n+grain]=audio2
                n+=grain
    return audio

def effect_grain(audio, grain):
    grain=int(grain)
    if len(audio)>10: audio=[audio]
    if type(audio) is not list: audio=audio.tolist()
    length=len(audio[0])
    n=0
    for i in range(len(audio)):
        while n+2*grain<length:
            audio[i][n+grain:n+2*grain]=audio[i][n:n+grain]
            n+=grain*2
    return audio

def effect_ftt(audio, inverse=True):
    """headphone warning: cursed effect"""
    import scipy.fft
    audio=numpy.asarray(audio).copy()
    for i in range(len(audio)):
        if inverse is False:
            audio[i]= scipy.fft.fft(audio[i], axis=0)
        else: 
            audio[i]= scipy.fft.ifft(audio[i], axis=0)
    audio=(audio*(2/numpy.max(audio)))-1
    return effect_normalize(audio)
    
def effect_fourier_shift(audio, value=5):
    """modulates volume for some reason"""
    import scipy.ndimage
    audio=numpy.asarray(audio).copy()
    audio= numpy.asarray(list(scipy.ndimage.fourier_shift(i, value, axis=-1) for i in audio)).astype(float)
    return effect_normalize(audio)

def effect_gradient(audio):
    """acts as an interesting high pass filter that removes drums"""
    audio=numpy.asarray(audio).copy()
    return numpy.gradient(audio, axis=0)

def effect_inverse_gradient(audio):
    """supposed to be inverse of a gradient, but it just completely destroys the audio into a distorted mess"""
    audio=numpy.asarray(audio).copy()
    for i in range(len(audio)):
        a = audio[i]
        audio[i] = a[0] + 2 * numpy.c_[numpy.r_[0, a[1:-1:2].cumsum()], a[::2].cumsum() - a[0] / 2].ravel()[:len(a)]
    audio=effect_normalize(audio)
    return numpy.gradient(audio, axis=0)

def image_effect_blur(image, value=(5,5)):
    """similar to echo"""
    import cv2
    if isinstance(value, int) or isinstance(value, float): value = (value,value)
    image=cv2.blur(image,value)
    return image

def image_effect_median(image, value=5):
    """similar to echo"""
    import scipy.signal
    image=scipy.signal.medfilt2d(image,value)
    return image

def image_effect_uniform(image, value=5):
    """similar to echo"""
    import scipy.ndimage
    image= scipy.ndimage.uniform_filter(image,value)
    return image

def image_effect_fourier_shift1d(image, value=5):
    """quickly modulates volume for some reason"""
    import scipy.ndimage
    image=scipy.ndimage.fourier_shift(image,value, axis=1)
    return image

def image_effect_fourier_shift2d(image, value=5):
    """very weird effect, mostly produces silence"""
    import scipy.ndimage
    image= scipy.ndimage.fourier_gaussian(image,value)
    image=image*(255/numpy.max(image))
    return image

def image_effect_spline(image, value=3):
    """barely noticeable echo"""
    import scipy.ndimage
    image= scipy.ndimage.spline_filter(image,value)
    return image

def image_effect_rotate(image, value=0.1):
    """roatates image in degrees"""
    import scipy.ndimage
    image= scipy.ndimage.rotate(image,value)
    return image

def image_effect_shapren(image, value=3):
    """sharpens image"""
    import scipy.ndimage
    blurred_f = scipy.ndimage.gaussian_filter(image, value)
    filter_blurred_f = scipy.ndimage.gaussian_filter(blurred_f, 1)
    sharpened = blurred_f + 30 * (blurred_f - filter_blurred_f)
    sharpened=sharpened*(255/numpy.max(sharpened))
    return sharpened

def mix_shuffle_approx_random(audio1, audio2, iterations, minlength=0, maxlength=None, bias=0):
    import random
    if isinstance(audio1, song): 
        minlength*=audio1.samplerate
        if maxlength is not None: maxlength*=audio1.samplerate
        audio1=audio1.audio
    else:
        minlength*=44100
        if maxlength is not None: maxlength*=44100
    if isinstance(audio2, song): audio2=audio2.audio
    if len(audio1)>16: audio1=numpy.asarray([audio1,audio1])
    if len(audio2)>16: audio1=numpy.asarray([audio2,audio2])
    shape2=len(audio2)
    mono1=numpy.abs(numpy.gradient(audio1[0]))
    mono2=numpy.abs(numpy.gradient(audio2[0]))
    length1=len(mono1)
    length2=len(mono2)
    result=numpy.zeros(shape=(shape2, length2))
    result_diff=numpy.zeros(shape=length2)
    old_difference=numpy.sum(mono2)
    random_result=result_diff.copy()
    for i in range(iterations):
        rstart=random.randint(0, length1)
        if maxlength is not None:
            rlength=random.randint(minlength, min(length1-rstart, maxlength))
        else: rlength=random.randint(minlength, minlength+length1-rstart)
        rplace=random.randint(0, length2-rlength)
        random_result=numpy.array(result_diff, copy=True)
        random_result[rplace:rplace + rlength] = mono1[rstart:rstart + rlength]
        difference = numpy.sum(numpy.abs(mono2 - random_result))
        if difference<old_difference-bias:
            print(i, difference)
            result[:, rplace:rplace + rlength] = audio1[:, rstart:rstart + rlength]
            result_diff=random_result
            old_difference = difference
    return result
# 10 5 4 1
# 10 0 0 0
# 0  5 4 1 10
# 10 5 4 1
# 10 5 4 1

#@njit SLOWER
def detect_bpm(audio, samplerate, bpm_low=40, bpm_high=300, bpm_step=0.1, mode=1, shift_step=10):
    """A very slow and inefficient algorithm!"""
    audio = numpy.asarray(audio)
    audio = (audio[0] + audio[1]).astype(numpy.float32)
    length=len(audio)
    mlength=length- int( 1 / ((bpm_low / 60) / samplerate) )  # to make sure those parts do not affect the calculation as they will be cut sometimes
    #audio[:int(spb_low)]=0 # to make sure those parts do not affect the calculation as they will be cut sometimes
    bpmdiffs=[]
    bpmdiffsi=[]
    minimum=100000000
    for i in range(int((bpm_high-bpm_low)/bpm_step)):
        spb=int(round(1/(((bpm_low + i*bpm_step) / 60) / samplerate)))
        # audio is reshaped into a 2d array with bpm
        end=-int(length % spb)
        if end == 0: end = length
        image = audio[:end].reshape(-1, spb)
        if mode == 1: image=image.T
        # diff21, diff22, diff41, diff42 = image[:-2].flatten(), image[2:].flatten(), image[:-4].flatten(), image[4:].flatten()
        # difference=abs( numpy.dot(diff21, diff22)/(numpy.linalg.norm(diff21)*numpy.linalg.norm(diff22)) + numpy.dot(diff41, diff42)/(numpy.linalg.norm(diff41)*numpy.linalg.norm(diff42)) )
        diff2=numpy.abs ( (image[:-2] - image[2:]).flatten()[:mlength] )
        diff4=numpy.abs ( (image[:-4] - image[4:]).flatten()[:mlength] )
        difference=numpy.sum(diff2*diff2*diff2*diff2) + numpy.sum(diff4*diff4*diff4*diff4)
        # for i in range(len(image)-1):
        #     difference.append(numpy.sum(image[i]-image[i]+1))
        if mode == 3: 
            image=image.T
            diff2=numpy.abs ( (image[:-2] - image[2:]).flatten()[:mlength] )
            diff4=numpy.abs ( (image[:-4] - image[4:]).flatten()[:mlength] )
            difference=numpy.sum(diff2*diff2*diff2*diff2) + numpy.sum(diff4*diff4*diff4*diff4)
        bpmdiffs.append(spb)
        bpmdiffsi.append(difference)
        if difference<minimum: 
            #print(f'{spb}: testing BPM = {(1/spb)*60*samplerate}; value = {difference}')
            print(i)
            minimum=difference
    spb = bpmdiffs[numpy.argmin(numpy.asarray(bpmdiffsi))]
    #print(f'BPM = {(1/spb)*60*samplerate}')
    bpmdiffs=[]
    bpmdiffsi=[]
    #audio[int(spb):]=0
    print(spb)
    for shift in range(0, spb, shift_step):
        #print(shift)
        end=-int(length % spb)
        if end == 0: end = length+shift
        image = audio[shift:end].reshape(-1, spb)
        length-=shift_step
        if mode == 1: image=image.T
        diff =  numpy.abs ( (image[:-1] - image[1:]).flatten()[:mlength] )
        difference=numpy.sum(diff*diff)
        if mode == 3: 
            image=image.T
            diff =  numpy.abs ( (image[:-1] - image[1:]).flatten()[:mlength] )
            difference += numpy.sum(diff*diff)
        bpmdiffs.append(shift)
        bpmdiffsi.append(difference)
        #if shift%1000==0: print(f'testing shift = {shift}; value = {difference}')
    shift = bpmdiffs[numpy.argmin(numpy.asarray(bpmdiffsi))]
    #print(f'BPM = {(1/spb)*60*samplerate}; shift = {shift/samplerate} sec.')
    return numpy.arange(shift, length, spb)
    
class song:
    def __init__(self, path:str=None, audio:numpy.array=None, samplerate:int=None, beatmap:list=None, caching=True, filename=None, copied=False, log=True):
        """song can be loaded from path to an audio file, or from a list/numpy array and samplerate. Audio array should have values from -1 to 1, multiple channels should be stacked vertically. Optionally you can provide your own beat map."""
        self.audio=audio
        self.samplerate=samplerate
        if path is None and filename is None:
            from tkinter.filedialog import askopenfilename
            self.path = askopenfilename(title='select song')
            #self.audio, self.samplerate=open_audio(self.path)
        else: 
            if path is None: self.path=filename
            else: self.path=path

        if self.path.lower().endswith('.zip'): 
            import shutil,os
            if os.path.exists('BeatManipulator_TEMP'): shutil.rmtree('BeatManipulator_TEMP')
            os.mkdir('BeatManipulator_TEMP')
            shutil.unpack_archive(self.path, 'BeatManipulator_TEMP')
            for root,dirs,files in os.walk('BeatManipulator_TEMP'):
                for fname in files:
                    if fname.lower().endswith('.mp3') or fname.lower().endswith('.wav') or fname.lower().endswith('.ogg') or fname.lower().endswith('.flac'):
                        self.audio, self.samplerate=open_audio(root.replace('\\','/')+'/'+fname)
                        stop=True
                        break
                if stop is True: break
            shutil.rmtree('BeatManipulator_TEMP')
    
        if self.audio is None or self.samplerate is None:
            self.audio, self.samplerate=open_audio(self.path)

        if len(self.audio)>16:
            self.audio=numpy.asarray((self.audio,self.audio))

        self.beatmap=beatmap
        self.path=self.path.replace('\\', '/')
        if filename is None: self.filename=path
        else: self.filename=filename.replace('\\', '/')
        self.samplerate=int(self.samplerate)
        if ' - ' in self.path.split('/')[-1]:
            self.artist = self.path.split('/')[-1].split(' - ')[0]
            self.title= '.'.join(self.path.split('/')[-1].split(' - ')[1].split('.')[:-1])
        else:
            self.title=''.join(self.path.split('/')[-1].split('.')[:-1])
            self.artist=None
        self.caching=caching
        self.log=log
        if copied is False and self.log is True: print(f'Loaded {self.artist} - {self.title}; ')
        self.audio_isarray = True
    
    def printlog(self, string, end=None):
        if self.log is True:
            if end is None: print(string)
            else:print(string,end=end)
    
    def _audio_tolist(self):
        if self.audio_isarray:
            self.audio = self.audio.tolist()
            self.audio_isarray = False

    def _audio_toarray(self):
        if not self.audio_isarray:
            self.audio = numpy.asarray(self.audio)
            self.audio_isarray = True

    def write_audio(self, output:str, lib:str='auto', libs=('pedalboard.io', 'soundfile')):
        """"writes audio"""
        self._audio_toarray()
        if lib!='auto': song.printlog(self, f'writing {output} with {lib}')
        if lib=='pedalboard.io':
            #print(audio)
            import pedalboard.io
            with pedalboard.io.AudioFile(output, 'w', self.samplerate, self.audio.shape[0]) as f:
                f.write(self.audio)
        elif lib=='soundfile':
            audio=self.audio.T
            import soundfile
            soundfile.write(output, audio, self.samplerate)
            del audio
        elif lib=='auto':
            for i in libs:
                try: 
                    song.write_audio(self, output, i)
                    break
                except Exception as e:
                    print(e)

        # elif lib=='pydub':
        #     from pydub import AudioSegment
        #     song = AudioSegment(self.audio.tobytes(), frame_rate=self.samplerate, sample_width=2, channels=2)
        #     format = output.split('.')[-1]
        #     if len(format) > 4: 
        #         format='mp3' 
        #         output = output + '.' + format
        #     song.export(output, format=format)

    def beatmap_scale(self, scale:float):
        scale=float(scale)
        
        #print(self.beatmap)
        import math
        if scale!=1:
            if self.log is True: print(f'scale={scale}; ')
            a=0
            b=numpy.array([], dtype=int)
            if scale%1==0:
                while a <len( self.beatmap):
                    #print(a, self.beatmap[int(a)], end=',       ')
                    b=numpy.append(b,self.beatmap[int(a)])
                    a+=scale
                    #print(self.beatmap[int(a)])
            else:
                while a+1 <len( self.beatmap):
                    #print(a,b)
                    b=numpy.append(b, int((1-(a%1))*self.beatmap[math.floor(a)]+(a%1)*self.beatmap[math.ceil(a)]))
                    a+=scale
            self.beatmap=b

    def analyze_beats(self, lib='madmom.BeatDetectionProcessor', caching=True, split=None):
        if self.log is True: print(f'analyzing beats using {lib}; ', end='')
        #if audio is None and filename is None: (audio, samplerate) = open_audio()
        if caching is True and self.caching is True:
            id=hex(len(self.audio[0]))
            import os
            if not os.path.exists('SavedBeatmaps'):
                os.mkdir('SavedBeatmaps')
            cacheDir="SavedBeatmaps/" + ''.join(self.filename.split('/')[-1]) + "_"+lib+"_"+id+'.txt'
            try: 
                self.beatmap=numpy.loadtxt(cacheDir, dtype=int)
                self.bpm=numpy.average(self.beatmap)/self.samplerate
                if self.log is True: print('loaded cached beatmap.')
                return
            except OSError: 
                if self.log is True:print("beatmap hasn't been generated yet. Generating...")

        if lib.split('.')[0]=='madmom':
            from collections.abc import MutableMapping, MutableSequence
            import madmom
        if lib=='madmom.BeatTrackingProcessor':
            proc = madmom.features.beats.BeatTrackingProcessor(fps=100)
            act = madmom.features.beats.RNNBeatProcessor()(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            self.beatmap= proc(act)*self.samplerate
        if lib=='madmom.BeatTrackingProcessor.constant':
            proc = madmom.features.beats.BeatTrackingProcessor(fps=100, look_ahead=None)
            act = madmom.features.beats.RNNBeatProcessor()(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            self.beatmap= proc(act)*self.samplerate
        if lib=='madmom.BeatTrackingProcessor.consistent':
            proc = madmom.features.beats.BeatTrackingProcessor(fps=100, look_ahead=None, look_aside=0)
            act = madmom.features.beats.RNNBeatProcessor()(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            self.beatmap= proc(act)*self.samplerate
        elif lib=='madmom.BeatDetectionProcessor':
            proc = madmom.features.beats.BeatDetectionProcessor(fps=100)
            act = madmom.features.beats.RNNBeatProcessor()(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            self.beatmap= proc(act)*self.samplerate
        elif lib=='madmom.BeatDetectionProcessor.consistent':
            proc = madmom.features.beats.BeatDetectionProcessor(fps=100, look_aside=0)
            act = madmom.features.beats.RNNBeatProcessor()(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            self.beatmap= proc(act)*self.samplerate
        elif lib=='madmom.CRFBeatDetectionProcessor':
            proc = madmom.features.beats.CRFBeatDetectionProcessor(fps=100)
            act = madmom.features.beats.RNNBeatProcessor()(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            self.beatmap= proc(act)*self.samplerate
        elif lib=='madmom.CRFBeatDetectionProcessor.constant':
            proc = madmom.features.beats.CRFBeatDetectionProcessor(fps=100, use_factors=True, factors=[0.5, 1, 2])
            act = madmom.features.beats.RNNBeatProcessor()(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            self.beatmap= proc(act)*self.samplerate
        elif lib=='madmom.DBNBeatTrackingProcessor':
            proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=100)
            act = madmom.features.beats.RNNBeatProcessor()(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            self.beatmap= proc(act)*self.samplerate
        elif lib=='madmom.DBNBeatTrackingProcessor.1000':
            proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=100, transition_lambda=1000)
            act = madmom.features.beats.RNNBeatProcessor()(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            self.beatmap= proc(act)*self.samplerate
        elif lib=='madmom.DBNDownBeatTrackingProcessor':
            proc = madmom.features.downbeats.DBNDownBeatTrackingProcessor(beats_per_bar=[4], fps=100)
            act = madmom.features.downbeats.RNNDownBeatProcessor()(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            self.beatmap= proc(act)*self.samplerate
            self.beatmap=self.beatmap[:,0]
        elif lib=='madmom.PatternTrackingProcessor': #broken
            from madmom.models import PATTERNS_BALLROOM
            proc = madmom.features.downbeats.PatternTrackingProcessor(PATTERNS_BALLROOM, fps=50)
            from madmom.audio.spectrogram import LogarithmicSpectrogramProcessor, SpectrogramDifferenceProcessor, MultiBandSpectrogramProcessor
            from madmom.processors import SequentialProcessor
            log = LogarithmicSpectrogramProcessor()
            diff = SpectrogramDifferenceProcessor(positive_diffs=True)
            mb = MultiBandSpectrogramProcessor(crossover_frequencies=[270])
            pre_proc = SequentialProcessor([log, diff, mb])
            act = pre_proc(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            self.beatmap= proc(act)*self.samplerate
            self.beatmap=self.beatmap[:,0]
        elif lib=='madmom.DBNBarTrackingProcessor': #broken
            beats = song.analyze_beats(self,lib='madmom.DBNBeatTrackingProcessor', caching = caching)
            proc = madmom.features.downbeats.DBNBarTrackingProcessor(beats_per_bar=[4], fps=100)
            act = madmom.features.downbeats.RNNBarProcessor()(((madmom.audio.signal.Signal(self.audio.T, self.samplerate)), beats))
            self.beatmap= proc(act)*self.samplerate
        elif lib=='librosa': #broken in 3.9, works in 3.8
            import librosa
            beat_frames = librosa.beat.beat_track(y=self.audio[0], sr=self.samplerate,hop_length=512)
            self.beatmap = librosa.frames_to_samples(beat_frames[1])
        # elif lib=='BeatNet':
        #     from BeatNet.BeatNet import BeatNet # doesn't seem to work well for some reason
        #     estimator = BeatNet(1, mode='offline', inference_model='DBN', plot=[], thread=False)
        #     beatmap = estimator.process(filename)
        #     beatmap=beatmap[:,0]*samplerate
        # elif lib=='jump-reward-inference': # doesn't seem to work well for some reason
        #     from jump_reward_inference.joint_tracker import joint_inference
        #     estimator = joint_inference(1, plot=False)
        #     beatmap = estimator.process(filename)
        #     beatmap=beatmap[:,0]*samplerate

        elif lib=='split':
            self.beatmap= list(range(0, len(self.audio), len(self.audio)//split))
        elif lib=='stunlocked':
            self.beatmap = detect_bpm(self.audio, self.samplerate)


        if lib.split('.')[0]=='madmom':
            self.beatmap=numpy.absolute(self.beatmap-500)
            
        if caching is True and self.caching is True: numpy.savetxt(cacheDir, self.beatmap.astype(int), fmt='%d')
        self.bpm=numpy.average(self.beatmap)/self.samplerate
        if isinstance(self.beatmap, list): self.beatmap=numpy.asarray(self.beatmap, dtype=int)
        self.beatmap=self.beatmap.astype(int)

    def generate_hitmap(self, lib='madmom.RNNBeatProcessor', caching=True):
        if self.log is True: print(f'analyzing hits using {lib}; ')
        self.hitlib=lib
        """among us big chungus"""
        if caching is True and self.caching is True:
            id=hex(len(self.audio[0]))
            import os
            if not os.path.exists('SavedBeatmaps'):
                os.mkdir('SavedBeatmaps')
            cacheDir="SavedBeatmaps/" + ''.join(self.filename.split('/')[-1]) + "_"+lib+"_"+id+'.txt'
            try: 
                cached=False
                self.beat_probabilities=numpy.loadtxt(cacheDir)
                cached=True
            except OSError: cached=False
        if cached is False:
            if lib=='madmom.RNNBeatProcessor':
                import madmom
                proc = madmom.features.beats.RNNBeatProcessor()
                self.beat_probabilities = proc(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
            elif lib=='madmom.MultiModelSelectionProcessor':
                import madmom
                proc = madmom.features.beats.RNNBeatProcessor(post_processor=None)
                predictions = proc(madmom.audio.signal.Signal(self.audio.T, self.samplerate))
                mm_proc = madmom.features.beats.MultiModelSelectionProcessor(num_ref_predictions=None)
                self.beat_probabilities= mm_proc(predictions)*self.samplerate
                self.beat_probabilities/= numpy.max(self.beat_probabilities)

            if caching is True and self.caching is True: numpy.savetxt(cacheDir, self.beat_probabilities)
    
    def osu(self):
        if self.log is True: print(f'generating osu file')
        def process(self, threshold):
            hitmap=[]
            actual_samplerate=int(self.samplerate/100)
            beat_middle=int(actual_samplerate/2)
            for i in range(len(self.beat_probabilities)):
                if self.beat_probabilities[i]>threshold: hitmap.append(i*actual_samplerate + beat_middle)
            hitmap=numpy.asarray(hitmap)
            clump=[]
            for i in range(len(hitmap)-1):
                #print(i, abs(self.hitmap[i]-self.hitmap[i+1]), clump)
                if abs(hitmap[i] - hitmap[i+1]) < self.samplerate/16: clump.append(i)
                elif clump!=[]: 
                    clump.append(i)
                    actual_time=hitmap[clump[0]]
                    hitmap[numpy.array(clump)]=0
                    #print(self.hitmap)
                    hitmap[clump[0]]=actual_time
                    clump=[]
            
            hitmap=hitmap[hitmap!=0]
            return hitmap
        
        osufile=lambda title,artist,version: ("osu file format v14\n"
        "\n"
        "[General]\n"
        f"AudioFilename: {self.path.split('/')[-1]}\n"
        "AudioLeadIn: 0\n"
        "PreviewTime: -1\n"
        "Countdown: 0\n"
        "SampleSet: Normal\n"
        "StackLeniency: 0.5\n"
        "Mode: 0\n"
        "LetterboxInBreaks: 0\n"
        "WidescreenStoryboard: 0\n"
        "\n"
        "[Editor]\n"
        "DistanceSpacing: 1.1\n"
        "BeatDivisor: 4\n"
        "GridSize: 8\n"
        "TimelineZoom: 1.6\n"
        "\n"
        "[Metadata]\n"
        f"Title:{title}\n"
        f"TitleUnicode:{title}\n"
        f"Artist:{artist}\n"
        f"ArtistUnicode:{artist}\n"
        f'Creator:{self.hitlib} + BeatManipulator\n'
        f'Version:{version} {self.hitlib}\n'
        'Source:\n'
        'Tags:BeatManipulator\n'
        'BeatmapID:0\n'
        'BeatmapSetID:-1\n'
        '\n'
        '[Difficulty]\n'
        'HPDrainRate:4\n'
        'CircleSize:4\n'
        'OverallDifficulty:7.5\n'
        'ApproachRate:10\n'
        'SliderMultiplier:3.3\n'
        'SliderTickRate:1\n'
        '\n'
        '[Events]\n'
        '//Background and Video events\n'
        '//Break Periods\n'
        '//Storyboard Layer 0 (Background)\n'
        '//Storyboard Layer 1 (Fail)\n'
        '//Storyboard Layer 2 (Pass)\n'
        '//Storyboard Layer 3 (Foreground)\n'
        '//Storyboard Layer 4 (Overlay)\n'
        '//Storyboard Sound Samples\n'
        '\n'
        '[TimingPoints]\n'
        '0,140.0,4,1,0,100,1,0\n'
        '\n'
        '\n'
        '[HitObjects]\n')
        # remove the clumps
        #print(self.hitmap)

        #print(self.hitmap)

        
        #print(len(osumap))
        #input('banana')
        import shutil, os
        if os.path.exists('BeatManipulator_TEMP'): shutil.rmtree('BeatManipulator_TEMP')
        os.mkdir('BeatManipulator_TEMP')
        hitmap=[]
        import random
        for difficulty in [0.2, 0.1, 0.08, 0.06, 0.04, 0.02, 0.01, 0.005]:
            for i in range(4):
                #print(i)
                this_difficulty=process(self, difficulty)
            hitmap.append(this_difficulty)
        for k in range(len(hitmap)):
            osumap=numpy.vstack((hitmap[k],numpy.zeros(len(hitmap[k])),numpy.zeros(len(hitmap[k])))).T
            difficulty= [0.2, 0.1, 0.08, 0.06, 0.04, 0.02, 0.01, 0.005][k]
            for i in range(len(osumap)-1):
                if i==0:continue
                dist=(osumap[i,0]-osumap[i-1,0])*(1-(difficulty**0.3))
                if dist<1000: dist=0.005
                elif dist<2000: dist=0.01
                elif dist<3000: dist=0.015
                elif dist<4000: dist=0.02
                elif dist<5000: dist=0.25
                elif dist<6000: dist=0.35
                elif dist<7000: dist=0.45
                elif dist<8000: dist=0.55
                elif dist<9000: dist=0.65
                elif dist<10000: dist=0.75
                elif dist<12500: dist=0.85
                elif dist<15000: dist=0.95
                elif dist<20000: dist=1
                #elif dist<30000: dist=0.8
                prev_x=osumap[i-1,1]
                prev_y=osumap[i-1,2]
                if prev_x>0: prev_x=prev_x-dist*0.1
                elif prev_x<0: prev_x=prev_x+dist*0.1
                if prev_y>0: prev_y=prev_y-dist*0.1
                elif prev_y<0: prev_y=prev_y+dist*0.1
                dirx=random.uniform(-dist,dist)
                diry=dist-abs(dirx)*random.choice([-1, 1])
                if abs(prev_x+dirx)>1: dirx=-dirx
                if abs(prev_y+diry)>1: diry=-diry
                x=prev_x+dirx
                y=prev_y+diry
                #print(dirx,diry,x,y)
                #print(x>1, x<1, y>1, y<1)
                if x>1: x=0.8
                if x<-1: x=-0.8
                if y>1: y=0.8
                if y<-1: y=-0.8
                #print(dirx,diry,x,y)
                osumap[i,1]=x
                osumap[i,2]=y

            osumap[:,1]*=300
            osumap[:,1]+=300
            osumap[:,2]*=180
            osumap[:,2]+=220
            file=osufile(self.artist, self.title, difficulty)
            for j in osumap:
                #print('285,70,'+str(int(int(i)*1000/self.samplerate))+',1,0')
                file+=f'{int(j[1])},{int(j[2])},{str(int(int(j[0])*1000/self.samplerate))},1,0\n'
            with open(f'BeatManipulator_TEMP/{self.artist} - {self.title} [BeatManipulator {difficulty} {self.hitlib}].osu', 'x', encoding="utf-8") as f:
                f.write(file)
        if self.path is not None: 
            shutil.copyfile(self.path, 'BeatManipulator_TEMP/'+self.path.split('/')[-1])
        else: song.write_audio(self,'BeatManipulator_TEMP/audio.mp3')
        shutil.make_archive('BeatManipulator_TEMP', 'zip', 'BeatManipulator_TEMP')
        os.rename('BeatManipulator_TEMP.zip', outputfilename('', self.path, '_'+self.hitlib, 'osz'))
        shutil.rmtree('BeatManipulator_TEMP')



    def audio_autotrim(self):
        if self.log is True: print(f'autotrimming; ')
        n=0
        for i in self.audio[0]:
            if i>=0.0001:break
            n+=1
        if type(self.audio) is tuple or list: self.audio = numpy.asarray(self.audio)
        self.audio = numpy.asarray([self.audio[0,n:], self.audio[1,n:]])
        #print(beatmap)
        if self.beatmap is not None: 
            self.beatmap=numpy.absolute(self.beatmap-n)
        else: 
            print('It is recommended to only use autotrim after computing the beatmap')

    def beatmap_autoscale(self):
        if self.log is True: print(f'autoscaling; ')
        bpm=(self.beatmap[-1]-self.beatmap[0])/(len(self.beatmap)-1)
        #print('BPM =', (bpm/samplerate) * 240, bpm)
        if bpm>=160000: scale=1/8
        elif (bpm)>=80000: scale=1/4
        elif (bpm)>=40000: scale=1/2
        elif (bpm)<=20000: scale=2
        elif (bpm)<=10000: scale=4
        elif (bpm)<=5000: scale=8
        song.beatmap_scale(self,scale)        

    def beatmap_autoinsert(self):
        if self.log is True: print(f'autoinserting; ')
        diff=(self.beatmap[1]-self.beatmap[0])
        a=0
        while diff<self.beatmap[0] and a<100:
            self.beatmap=numpy.insert(self.beatmap, 0, self.beatmap[0]-diff)
            a+=1

    def beatmap_shift(self, shift: float):
        shift=float(shift)
        if shift!=0 and self.log is True: print(f'shift={shift}; ')
        elif shift==0: return
        if shift<0:
            shift=-shift # so that floor division works correctly
            # add integer number of beats to the start
            if shift >= 1: self.beatmap=numpy.insert(self.beatmap, 0, list(i+1 for i in range(int(shift//1))))
            if shift%1!=0:
                # shift by modulus from the end
                shift=shift%1
                for i in reversed(range(len(self.beatmap))):
                    if i==0: continue
                    #print(i, ', ',self.beatmap[i], '-', shift, '* (', self.beatmap[i], '-', self.beatmap[i-1],') =', self.beatmap[i] - shift * (self.beatmap[i] - self.beatmap[i-1]))
                    self.beatmap[i] = int(self.beatmap[i] - shift * (self.beatmap[i] - self.beatmap[i-1]))

        
        elif shift>0:
            # remove integer number of beats from the start
            if shift >= 1: self.beatmap=self.beatmap[int(shift//1):]
            if shift%1!=0:
                # shift by modulus
                shift=shift%1
                for i in range(len(self.beatmap)-int(shift)-1):
                    #print(self.beatmap[i], '+', shift, '* (', self.beatmap[i+1], '-', self.beatmap[i],') =', self.beatmap[i] + shift * (self.beatmap[i+1] - self.beatmap[i]))
                    self.beatmap[i] = int(self.beatmap[i] + shift * (self.beatmap[i+1] - self.beatmap[i]))
        
        self.beatmap=sorted(list(self.beatmap))
        while True:
            n,done=0,[]
            for i in range(len(self.beatmap)):
                if self.beatmap.count(self.beatmap[i])>1 and i not in done:
                    self.beatmap[i]+=1
                    n+=1
                    done.append(i)
            if n==0: break
        self.beatmap=sorted(list(self.beatmap))

    def beatmap_trim(self, start=0, end=None):
        if start!=0 or end is not None and self.log is True: print(f'start={start}; end={end}; ')
        start*=self.samplerate
        self.beatmap=self.beatmap[self.beatmap>=start].astype(int)
        if end is not None: self.beatmap=self.beatmap[self.beatmap<=end].astype(int)


    def beatswap(self, pattern: str, sep=',', smoothing=40, smoothing_mode='replace'):
        import math, numpy
        # get pattern size
        size=0    
        #cut processing??? not worth it, it is really fast anyways
        pattern=pattern.replace(' ', '').split(sep)
        if self.log is True: print(f"beatswapping with {' '.join(pattern)}; ")
        for j in pattern:
            s=''
            if '?' not in j:
                for i in j:
                    if i.isdigit() or i=='.' or i=='-' or i=='/' or i=='+' or i=='%': s=str(s)+str(i)
                    elif i==':':
                        if s=='': s='0'
                        #print(s, ast.literal_eval(s))
                        size=max(math.ceil(float(ast.literal_eval(s))), size)
                        s=''
                    elif s!='': break
                if s=='': s='0'
            if s=='': s='0'
            size=max(math.ceil(float(ast.literal_eval(s))), size)

        if isinstance(self.audio,numpy.ndarray): self.audio=numpy.ndarray.tolist(self.audio)
        if isinstance(self.beatmap, list): self.beatmap=numpy.asarray(self.beatmap, dtype=int)

        # turns audio into a tuple with L and R channels
        self.audio=(self.audio[0], self.audio[1])

        # adds the part before the first beat
        result=(self.audio[0][:self.beatmap[0]],self.audio[1][:self.beatmap[0]])
        beat=numpy.asarray([[],[]])

        # size, iterations are integers
        size=int(max(size//1, 1))
    

        # add beat to the end
        self.beatmap=numpy.abs(numpy.append(self.beatmap, len(self.audio[0])))
        self.beatmap=self.beatmap.astype(int)

        iterations=int(len(self.beatmap)//size)
        
        if 'random' in pattern[0].lower():
            import random
            for i in range(len(self.beatmap)):

                choice=random.randint(1,len(self.beatmap)-1)
                for a in range(len(self.audio)): 
                    try:
                        beat=self.audio[a][self.beatmap[choice-1]:self.beatmap[choice]-smoothing]
                        if smoothing>0: result[a].extend(numpy.linspace(result[a][-1],beat[0],smoothing))
                        result[a].extend(beat)
                    except IndexError: pass
            self.audio = result
            return
        
        if 'reverse' in pattern[0].lower():
            for a in range(len(self.audio)): 
                for i in list(reversed(range(len(self.beatmap))))[:-1]:
                    try:
                        beat=self.audio[a][self.beatmap[i-1]:self.beatmap[i]-smoothing]
                        #print(self.beatmap[i-1],self.beatmap[i])
                        #print(result[a][-1], beat[0])
                        if smoothing>0: result[a].extend(numpy.linspace(result[a][-1],beat[0],smoothing))
                        result[a].extend(beat)
                    except IndexError: pass

            self.audio = result
            return
                    
        #print(len(result[0]))
        def beatswap_getnum(i: str, c: str):
            if c in i:
                try: 
                    x=i.index(c)+1
                    z=''
                    try:
                        while i[x].isdigit() or i[x]=='.' or i[x]=='-' or i[x]=='/' or i[x]=='+' or i[x]=='%': 
                            z+=i[x]
                            x+=1
                        return z
                    except IndexError:
                        return z
                except ValueError: return None

        #print(len(self.beatmap), size, iterations)
        # processing
        for j in range(iterations+1):
            for i in pattern:
                if '!' not in i:
                    n,s,st,reverse,z=0,'',None,False,None
                    for c in i:
                        n+=1
                        #print('c =', s, ',  st =', st, ',   s =', s, ',   n =,',n)

                        # Get the character
                        if c.isdigit() or c=='.' or c=='-' or c=='/' or c=='+' or c=='%': 
                            s=str(s)+str(c)
                        
                        # If character is : - get start
                        elif s!='' and c==':':
                            #print ('Beat start:',s,'=', ast.literal_eval(s),'=',int(ast.literal_eval(s)//1), '+',j,'*',size,'    =',int(ast.literal_eval(s)//1)+j*size, ',   mod=',ast.literal_eval(s)%1)
                            try: st=self.beatmap[int(ast.literal_eval(s)//1)+j*size ] + ast.literal_eval(s)%1* (self.beatmap[int(ast.literal_eval(s)//1)+j*size +1] - self.beatmap[int(ast.literal_eval(s)//1)+j*size])
                            except IndexError: break
                            s=''
                        
                        # create a beat
                        if s!='' and (n==len(i) or not(c.isdigit() or c=='.' or c=='-' or c=='/' or c=='+' or c=='%')):

                            # start already exists
                            if st is not None:
                                #print ('Beat end:  ',s,'=', ast.literal_eval(s),'=',int(ast.literal_eval(s)//1), '+',j,'*',size,'    =',int(ast.literal_eval(s)//1)+j*size, ',   mod=',ast.literal_eval(s)%1)
                                try:
                                    s=self.beatmap[int(ast.literal_eval(s)//1)+j*size ] + ast.literal_eval(s)%1* (self.beatmap[int(ast.literal_eval(s)//1)+j*size +1] - self.beatmap[int(ast.literal_eval(s)//1)+j*size])
                                    #print(s)
                                except IndexError: break
                            else:
                                # start doesn't exist
                                #print ('Beat start:',s,'=', ast.literal_eval(s),'=',int(ast.literal_eval(s)//1), '+',j,'*',size,'- 1 =',int(ast.literal_eval(s)//1)+j*size,   ',   mod=',ast.literal_eval(s)%1)
                                #print ('Beat end:  ',s,'=', ast.literal_eval(s),'=',int(ast.literal_eval(s)//1), '+',j,'*',size,'    =',int(ast.literal_eval(s)//1)+j*size+1, ',   mod=',ast.literal_eval(s)%1)
                                try:
                                    st=self.beatmap[int(ast.literal_eval(s)//1)+j*size-1 ] + ast.literal_eval(s)%1* (self.beatmap[int(ast.literal_eval(s)//1)+j*size +1] - self.beatmap[int(ast.literal_eval(s)//1)+j*size])
                                    s=self.beatmap[int(ast.literal_eval(s)//1)+j*size ] + ast.literal_eval(s)%1* (self.beatmap[int(ast.literal_eval(s)//1)+j*size +1] - self.beatmap[int(ast.literal_eval(s)//1)+j*size])
                                except IndexError: break
                            
                            if st>s: 
                                s, st=st, s
                                reverse=True

                            # create the beat
                            if len(self.audio)>1: 
                                if smoothing_mode=='add': beat=numpy.asarray([self.audio[0][int(st):int(s)],self.audio[1][int(st):int(s)]])
                                else: beat=numpy.asarray([self.audio[0][int(st):int(s)-smoothing],self.audio[1][int(st):int(s)-smoothing]])
                            else:
                                if smoothing_mode=='add': beat=numpy.asarray([self.audio[0][int(st):int(s)]])
                                else: beat=numpy.asarray([self.audio[0][int(st):int(s)-smoothing]])

                            # process the beat
                            # channels
                            z=beatswap_getnum(i,'c')
                            if z is not None:
                                if z=='': beat[0],beat[1]=beat[1],beat[0]
                                elif ast.literal_eval(z)==0:beat[0]*=0
                                else:beat[1]*=0

                            # volume
                            z=beatswap_getnum(i,'v')
                            if z is not None:
                                if z=='': z='0'
                                beat*=ast.literal_eval(z)

                            z=beatswap_getnum(i,'t')
                            if z is not None:
                                if z=='': z='2'
                                beat**=1/ast.literal_eval(z)

                            # speed
                            z=beatswap_getnum(i,'s')
                            if z is not None:
                                if z=='': z='2'
                                z=ast.literal_eval(z)
                                if z<1: 
                                    beat=numpy.asarray((numpy.repeat(beat[0],int(1//z)),numpy.repeat(beat[1],int(1//z))))
                                else:
                                    beat=numpy.asarray((beat[0,::int(z)],beat[1,::int(z)]))
                            
                            # bitcrush
                            z=beatswap_getnum(i,'b')
                            if z is not None:
                                if z=='': z='3'
                                z=1/ast.literal_eval(z)
                                if z<1: beat=beat*z
                                beat=numpy.around(beat, max(int(z), 1))
                                if z<1: beat=beat/z

                            # downsample
                            z=beatswap_getnum(i,'d')
                            if z is not None:
                                if z=='': z='3'
                                z=int(ast.literal_eval(z))
                                beat=numpy.asarray((numpy.repeat(beat[0,::z],z),numpy.repeat(beat[1,::z],z)))

                            # convert to list
                            beat=beat.tolist()

                            # effects with list
                            # reverse
                            if ('r' in i and reverse is False) or (reverse is True and 'r' not in i):
                                beat=(beat[0][::-1],beat[1][::-1] )

                            # add beat to the result
                            for a in range(len(self.audio)): 
                                #print('Adding beat... a, s, st:', a, s, st, sep=',  ')
                                #print(result[a][-1])
                                #print(beat[a][0])
                                try:
                                    if smoothing>0: result[a].extend(numpy.linspace(result[a][-1],beat[a][0],smoothing))
                                    result[a].extend(beat[a])
                                except IndexError: pass
                                #print(len(result[0]))

                            #   
                            break

        self.audio = result

    def beatsample(self, audio2, shift=0):
        if self.log is True: print(f'beatsample; ')
        try: l=len(audio2[0])
        except (TypeError, IndexError): 
            l=len(audio2)
            audio2=numpy.vstack((audio2,audio2))
        for i in range(len(self.beatmap)):
            #print(self.beatmap[i])
            try: self.audio[:,int(self.beatmap[i]) + int(float(shift) * (int(self.beatmap[i+1])-int(self.beatmap[i]))) : int(self.beatmap[i])+int(float(shift) * (int(self.beatmap[i+1])-int(self.beatmap[i])))+int(l)]+=audio2
            except (IndexError, ValueError): pass

    def hitsample(self, audio2=None):
        if self.log is True: print(f'hitsample; ')
        if audio2 is None:audio2=generate_saw(0.05, 1000, self.samplerate)
        try: l=len(audio2[0])
        except (TypeError, IndexError): 
            l=len(audio2)
            audio2=numpy.vstack((audio2,audio2))
        #print(self.audio)
        self.audio=numpy.array(self.audio).copy()
        #print(self.audio)
        for i in range(len(self.hitmap)):
            try: 
                #print('before', self.audio[:,int(self.hitmap[i])])
                self.audio[:,int(self.hitmap[i]) : int(self.hitmap[i]+l)]+=audio2
                #print('after ', self.audio[:,int(self.hitmap[i])])
                #print(self.hitmap[i])
            except (IndexError, ValueError): pass

    def sidechain(self, audio2, shift=0, smoothing=40):
        if self.log is True: print(f'sidechain; ')
        try: l=len(audio2[0])
        except (TypeError, IndexError): 
            l=len(audio2)
            audio2=numpy.vstack((audio2,audio2))
        for i in range(len(self.beatmap)):
            try: self.audio[:,int(self.beatmap[i])-smoothing + int(float(shift) * (int(self.beatmap[i+1])-int(self.beatmap[i]))) : int(self.beatmap[i])-smoothing+int(float(shift) * (int(self.beatmap[i+1])-int(self.beatmap[i])))+int(l)]*=audio2
            except (IndexError, ValueError): break

    def quick_beatswap(self, output:str='', pattern:str=None, scale:float=1, shift:float=0, start:float=0, end:float=None, autotrim:bool=True, autoscale:bool=False, autoinsert:bool=False, suffix:str=' (BeatSwap)', lib:str='madmom.BeatDetectionProcessor'):
        """Generates beatmap if it isn't generated, applies beatswapping to the song and writes the processed song it next to the .py file. If you don't want to write the file, set output=None
        
        output: can be a relative or an absolute path to a folder or to a file. Filename will be created from the original filename + a suffix to avoid overwriting. If path already contains a filename which ends with audio file extension, such as .mp3, that filename will be used.
        
        pattern: the beatswapping pattern.
        
        scale: scales the beatmap, for example if generated beatmap is two times faster than the song you can slow it down by putting 0.5.
        
        shift: shifts the beatmap by this amount of unscaled beats
        
        start: position in seconds, beats before the position will not be manipulated
        
        end: position in seconds, same. Set to None by default.
        
        autotrim: trims silence in the beginning for better beat detection, True by default
        
        autoscale: scales beats so that they are between 10000 and 20000 samples long. Useful when you are processing a lot of files with similar BPMs, False by default.
        
        autoinsert: uses distance between beats and inserts beats at the beginning at that distance if possible. Set to False by default, sometimes it can fix shifted beatmaps and sometimes can add unwanted shift.
        
        suffix: suffix that will be appended to the filename
        
        lib: beat detection library"""
        if self.log is True: print('___')
        if self.beatmap is None: song.analyze_beats(self,lib=lib)
        if autotrim is True: song.audio_autotrim(self)
        save=self.beatmap.copy()
        if autoscale is True: song.beatmap_autoscale(self)
        if shift!=0: song.beatmap_shift(self,shift)
        if scale!=1: song.beatmap_scale(self,scale)
        if autoinsert is True: song.beatmap_autoinsert(self)
        if start!=0 or end is not None: song.beatmap_trim(self,start, end)
        if self.log is True: print('pattern =', pattern)
        if 'test' in pattern.lower():
            self.beatmap=save.copy()
            if autoinsert is True: song.beatmap_autoinsert(self)
            if start!=0 or end is not None: song.beatmap_trim(self,start, end)
            audio2, samplerate2=open_audio('samples/cowbell.mp3')
            song.quick_beatsample(self, output=None, audio2=list(i[::3] for i in audio2), scale=8*scale, shift=0+shift)
            song.quick_beatsample(self, output=None, audio2=list(i[::2] for i in audio2), scale=8*scale, shift=1*scale+shift)
            song.quick_beatsample(self, output=None, audio2=audio2, scale=8*scale, shift=2*scale+shift)
            song.quick_beatsample(self, output=None, audio2=numpy.repeat(audio2,2,axis=1), scale=8*scale, shift=3*scale+shift)
            song.quick_beatsample(self, output=None, audio2=numpy.repeat(audio2,3,axis=1), scale=8*scale, shift=4*scale+shift)
            song.quick_beatsample(self, output=None, audio2=numpy.repeat(audio2,2,axis=1), scale=8*scale, shift=5*scale+shift)
            song.quick_beatsample(self, output=None, audio2=audio2, scale=8*scale, shift=6*scale+shift)
            song.quick_beatsample(self, output=None, audio2=list(i[::2] for i in audio2), scale=8*scale, shift=7*scale+shift)

        else: song.beatswap(self,pattern)

        if output is not None:
            if not (output.lower().endswith('.mp3') or output.lower().endswith('.wav') or output.lower().endswith('.flac') or output.lower().endswith('.ogg') or 
            output.lower().endswith('.aac') or output.lower().endswith('.ac3') or output.lower().endswith('.aiff')  or output.lower().endswith('.wma')):
                output=output+'.'.join(''.join(self.path.split('/')[-1]).split('.')[:-1])+suffix+'.mp3'
            song.write_audio(self,output)

        self.beatmap=save.copy()


    def quick_sidechain(self, output:str='', audio2:numpy.array=None, scale:float=1, shift:float=0, start:float=0, end:float=None, autotrim:bool=True, autoscale:bool=False, autoinsert:bool=False, filename2:str=None, suffix:str=' (sidechain)', lib:str='madmom.BeatDetectionProcessor'):
        """Generates beatmap if it isn't generated, applies fake sidechain on each beat to the song and writes the processed song it next to the .py file. If you don't want to write the file, set output=None
        
        output: can be a relative or an absolute path to a folder or to a file. Filename will be created from the original filename + a suffix to avoid overwriting. If path already contains a filename which ends with audio file extension, such as .mp3, that filename will be used.
        
        audio2: sidechain impulse, basically a curve that the volume will be multiplied by. By default one will be generated with generate_sidechain()
        
        scale: scales the beatmap, for example if generated beatmap is two times faster than the song you can slow it down by putting 0.5.
        
        shift: shifts the beatmap by this amount of unscaled beats
        
        start: position in seconds, beats before the position will not be manipulated
        
        end: position in seconds, same. Set to None by default.
        
        autotrim: trims silence in the beginning for better beat detection, True by default
        
        autoscale: scales beats so that they are between 10000 and 20000 samples long. Useful when you are processing a lot of files with similar BPMs, False by default.
        
        autoinsert: uses distance between beats and inserts beats at the beginning at that distance if possible. Set to False by default, sometimes it can fix shifted beatmaps and sometimes can add unwanted shift.
        
        filename2: loads sidechain impulse from the file if audio2 if not specified

        suffix: suffix that will be appended to the filename
        
        lib: beat detection library"""
        if self.log is True: print('___')
        if filename2 is None and audio2 is None:
            audio2=generate_sidechain()

        if audio2 is None:
            audio2, samplerate2=open_audio(filename2)

        if self.beatmap is None: song.analyze_beats(self,lib=lib)
        if autotrim is True: song.audio_autotrim(self)
        save=self.beatmap.copy()
        if autoscale is True: song.beatmap_autoscale(self)
        if shift!=0: song.beatmap_shift(self,shift)
        if scale!=1: song.beatmap_scale(self,scale)
        if autoinsert is True: song.beatmap_autoinsert(self)
        if start!=0 or end is not None: song.beatmap_trim(self,start, end)
        song.sidechain(self,audio2)

        if output is not None:
            if not (output.lower().endswith('.mp3') or output.lower().endswith('.wav') or output.lower().endswith('.flac') or output.lower().endswith('.ogg') or 
            output.lower().endswith('.aac') or output.lower().endswith('.ac3') or output.lower().endswith('.aiff')  or output.lower().endswith('.wma')):
                output=output+'.'.join(''.join(self.path.split('/')[-1]).split('.')[:-1])+suffix+'.mp3'
            song.write_audio(self,output)
        
        self.beatmap=save.copy()

    def quick_beatsample(self, output:str='', filename2:str=None, scale:float=1, shift:float=0, start:float=0, end:float=None, autotrim:bool=True, autoscale:bool=False, autoinsert:bool=False, audio2:numpy.array=None, suffix:str=' (BeatSample)', lib:str='madmom.BeatDetectionProcessor'):
        """Generates beatmap if it isn't generated, adds chosen sample to each beat of the song and writes the processed song it next to the .py file. If you don't want to write the file, set output=None
        
        output: can be a relative or an absolute path to a folder or to a file. Filename will be created from the original filename + a suffix to avoid overwriting. If path already contains a filename which ends with audio file extension, such as .mp3, that filename will be used.
        
        filename2: path to the sample.
        
        scale: scales the beatmap, for example if generated beatmap is two times faster than the song you can slow it down by putting 0.5.
        
        shift: shifts the beatmap by this amount of unscaled beats
        
        start: position in seconds, beats before the position will not be manipulated
        
        end: position in seconds, same. Set to None by default.
        
        autotrim: trims silence in the beginning for better beat detection, True by default
        
        autoscale: scales beats so that they are between 10000 and 20000 samples long. Useful when you are processing a lot of files with similar BPMs, False by default.
        
        autoinsert: uses distance between beats and inserts beats at the beginning at that distance if possible. Set to False by default, sometimes it can fix shifted beatmaps and sometimes can add unwanted shift.
        
        suffix: suffix that will be appended to the filename
        
        lib: beat detection library"""
        if self.log is True: print('___')
        if filename2 is None and audio2 is None:
            from tkinter.filedialog import askopenfilename
            filename2 = askopenfilename(title='select sidechain impulse', filetypes=[("mp3", ".mp3"),("wav", ".wav"),("flac", ".flac"),("ogg", ".ogg"),("wma", ".wma")])

        if audio2 is None:
            audio2, samplerate2=open_audio(filename2)

        if self.beatmap is None: song.analyze_beats(self,lib=lib)
        if autotrim is True: song.audio_autotrim(self)
        save=numpy.copy(self.beatmap)
        if autoscale is True: song.beatmap_autoscale(self)
        if shift!=0: song.beatmap_shift(self,shift)
        #print(numpy.asarray(save[0:10]))
        #print(numpy.asarray(self.beatmap[0:10]))
        if scale!=1: song.beatmap_scale(self,scale)
        if autoinsert is True: song.beatmap_autoinsert(self)
        if start!=0 or end is not None: song.beatmap_trim(self,start, end)
        song.beatsample(self,audio2)

        if output is not None:
            if not (output.lower().endswith('.mp3') or output.lower().endswith('.wav') or output.lower().endswith('.flac') or output.lower().endswith('.ogg') or 
            output.lower().endswith('.aac') or output.lower().endswith('.ac3') or output.lower().endswith('.aiff')  or output.lower().endswith('.wma')):
                output=output+'.'.join(''.join(self.path.split('/')[-1]).split('.')[:-1])+suffix+'.mp3'
            song.write_audio(self,output)
        self.beatmap=save.copy()
        
    def audio_spectogram(self, hop_length:int=512):
        self.hop_length=hop_length
        import librosa
        self.spectogram=librosa.feature.melspectrogram(y=self.audio, sr=self.samplerate, hop_length=hop_length)

    def spectogram_effect(self, effect, *args, **kwargs):
        song.printlog(self,f'applying spectogram effect: {effect.__name__} with {args}, {kwargs}; ')
        self.spectogram=list(effect(i, *args, **kwargs) for i in self.spectogram)
    
    def spectogram_write(self,output, channels='combine'):
        song.printlog(self,'writing spectogram; ')
        import cv2
        if channels.lower().startswith('l'): image=self.spectogram[0]
        elif channels.lower().startswith('r'): image=self.spectogram[1]
        else: image=(self.spectogram[0]+self.spectogram[1])/2
        cv2.imwrite(output, image)

    def spectogram_audio(self):
        import librosa
        self.audio=librosa.feature.inverse.mel_to_audio(M=numpy.swapaxes(numpy.swapaxes(numpy.dstack(( self.spectogram[0,:,:],  self.spectogram[1,:,:])), 0, 2), 1,2), sr=self.samplerate, hop_length=self.hop_length)

    def audio_beatimage(self, mode='maximum'):
        song.printlog(self,'generating beat-image; ')
        """Turns song into an image based on beat positions."""
        mode=mode.lower()
        if isinstance(self.audio,numpy.ndarray): self.audio=numpy.ndarray.tolist(self.audio)
        # add the bits before first beat
        self.image=([self.audio[0][0:self.beatmap[0]],], [self.audio[1][0:self.beatmap[0]],])
        # maximum is needed to make the array homogeneous
        maximum=self.beatmap[0]
        values=[]
        values.append(self.beatmap[0])
        for i in range(len(self.beatmap)-1):
            self.image[0].append(self.audio[0][self.beatmap[i]:self.beatmap[i+1]])
            self.image[1].append(self.audio[1][self.beatmap[i]:self.beatmap[i+1]])
            maximum = max(self.beatmap[i+1]-self.beatmap[i], maximum)
            values.append(self.beatmap[i+1]-self.beatmap[i])
        if 'max' in mode: norm=maximum
        elif 'med' in mode: norm=numpy.median(values)
        elif 'av' in mode: norm=numpy.average(values)
        for i in range(len(self.image[0])):
            beat_diff=int(norm-len(self.image[0][i]))
            if beat_diff>0:
                self.image[0][i].extend([numpy.nan]*beat_diff)
                self.image[1][i].extend([numpy.nan]*beat_diff)
            elif beat_diff<0:
                self.image[0][i]=self.image[0][i][:beat_diff]
                self.image[1][i]=self.image[1][i][:beat_diff]
        self.image=numpy.asarray(self.image)*255
        self.image_combined=numpy.add(self.image[0], self.image[1])/2

    def beatimage_effect(self, effect, *args, **kwargs):
        song.printlog(self,f'applying beat-image effect: {effect.__name__} with {args}, {kwargs}; ')
        self.image=numpy.nan_to_num(self.image)
        self.image=list(effect(i, *args, **kwargs) for i in self.image)

    def beatimage_audio(self):
        song.printlog(self,'converting beat-image to audio')
        image=numpy.asarray(self.image)/255
        audio=list([] for i in range(len(image)))
        #print(audio)
        for j in range(len(image)):
            for i in range(len(image[j])):
                beat=image[j][i]
                beat=beat[~numpy.isnan(beat)]
                audio[j].extend(beat)
        self.audio=audio
    
    def beatimage_write(self,output, channels='combine', rotate=True, mode='square', maximum=4096):
        song.printlog(self,'writing beat-image; ')
        import cv2
        if channels.lower().startswith('l'): image=self.image[0]
        elif channels.lower().startswith('r'): image=self.image[1]
        else: image=self.image_combined
        if mode.lower()=='square':
            y=min(len(image), len(image[1]), maximum)
            y=max(y, maximum)
            image = cv2.resize(image, (y,y), interpolation=cv2.INTER_NEAREST)
        if rotate is True: image=image.T
        cv2.imwrite(output, image)

def fix_beatmap(filename, lib='madmom.BeatDetectionProcessor', scale=1, shift=0):
    if scale==1 and shift==0:
        print('scale = 1, shift = 0: no changes have been made.')
        return
    track=song(filename)
    track.analyze_beats(lib=lib)
    track.beatmap_shift(shift)
    track.beatmap_scale(scale)
    id=hex(len(track.audio[0]))
    import os
    if not os.path.exists('SavedBeatmaps'):
        os.mkdir('SavedBeatmaps')
    cacheDir="SavedBeatmaps/" + ''.join(track.filename.split('/')[-1]) + "_"+lib+"_"+id+'.txt'
    a=input(f'Are you sure you want to overwrite {cacheDir} using scale = {scale}; shift = {shift}? ("y" to continue): ')
    if 'n' in a.lower() or not 'y' in a.lower():
        print('Operation canceled.') 
        return
    else: 
        numpy.savetxt(cacheDir, track.beatmap.astype(int), fmt='%d')
        print('Beatmap overwritten.')

def delete_beatmap(filename, lib='madmom.BeatDetectionProcessor'):
    track=song(filename)
    id=hex(len(track.audio[0]))
    import os
    if not os.path.exists('SavedBeatmaps'):
        os.mkdir('SavedBeatmaps')
    cacheDir="SavedBeatmaps/" + ''.join(track.filename.split('/')[-1]) + "_"+lib+"_"+id+'.txt'
    a=input(f'Are you sure you want to delete {cacheDir}? ("y" to continue): ')
    if 'n' in a.lower() or not 'y' in a.lower():
        print('Operation canceled.') 
        return
    else: 
        os.remove(cacheDir)
        print('Beatmap deleted.')

