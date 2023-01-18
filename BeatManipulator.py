import numpy
numpy.set_printoptions(suppress=True)

def open_audio(filename=None, lib='auto'):
    if filename is None:
        from tkinter.filedialog import askopenfilename
        filename = askopenfilename(title='select song', filetypes=[("mp3", ".mp3"),("wav", ".wav"),("flac", ".flac"),("ogg", ".ogg"),("wma", ".wma")])
    filename=filename.replace('\\', '/')
    if lib=='pedalboard.io':
        from pedalboard.io import AudioFile
        with AudioFile(filename) as f:
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
                print(e)
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

def pitch(audio, pitch, grain):
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

def pitchB(audio, pitch, grain):
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

def grain(audio, grain):
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

class song:
    def __init__(self, filename:str=None, audio:numpy.array=None, samplerate:int=None, beatmap:list=None):
        """song can be loaded from path to an audio file, or from a list/numpy array and samplerate. Audio array should have values from -1 to 1, multiple channels should be stacked vertically. Optionally you can provide your own beat map."""
        self.audio=audio
        self.samplerate=samplerate
        if filename is None:
            from tkinter.filedialog import askopenfilename
            self.filename = askopenfilename(title='select song')
            #self.audio, self.samplerate=open_audio(self.filename)
        else: 
            self.filename=filename

        if self.filename.lower().endswith('.zip'): 
            import shutil,os
            if os.path.exists('BeatManipulator_TEMP'): shutil.rmtree('BeatManipulator_TEMP')
            os.mkdir('BeatManipulator_TEMP')
            shutil.unpack_archive(self.filename, 'BeatManipulator_TEMP')
            for root,dirs,files in os.walk('BeatManipulator_TEMP'):
                for fname in files:
                    if fname.lower().endswith('.mp3') or fname.lower().endswith('.wav') or fname.lower().endswith('.ogg') or fname.lower().endswith('.flac'):
                        self.audio, self.samplerate=open_audio(root.replace('\\','/')+'/'+fname)
                        stop=True
                        break
                if stop is True: break
            shutil.rmtree('BeatManipulator_TEMP')
    
        if self.audio is None or self.samplerate is None:
            self.audio, self.samplerate=open_audio(self.filename)
        
        self.beatmap=beatmap
        self.filename=self.filename.replace('\\', '/')
        self.samplerate=int(self.samplerate)
        self.artist = self.filename.split('/')[-1].split(' - ')[0]
        self.title= '.'.join(self.filename.split('/')[-1].split(' - ')[1].split('.')[:-1])
        print(f'Loaded {self.artist} - {self.title}; ')
    
    def write_audio(self, output:str, lib:str='auto'):
        """"writes audio"""
        if lib!='auto': print(f'writing {output} with {lib}')
        if lib=='pedalboard.io':
            if not isinstance(self.audio,numpy.ndarray): self.audio=numpy.asarray(self.audio)
            #print(audio)
            from pedalboard.io import AudioFile
            with AudioFile(output, 'w', self.samplerate, self.audio.shape[0]) as f:
                f.write(self.audio)
        elif lib=='soundfile':
            if not isinstance(self.audio,numpy.ndarray): self.audio=numpy.asarray(self.audio)
            audio=self.audio.T
            import soundfile
            soundfile.write(output, audio, self.samplerate)
            del audio
        elif lib=='auto':
            for i in ('pedalboard.io', 'soundfile'):
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
        
        #print(self.beatmap)
        import math
        if scale!=1:
            print(f'scale={scale}; ')
            a=0
            b=numpy.array([])
            if scale%1==0:
                while a <len( self.beatmap[:-int(scale)]):
                    #print(a, self.beatmap[int(a)], end=',       ')
                    b=numpy.append(b,self.beatmap[int(a)])
                    a+=scale
                    #print(self.beatmap[int(a)])
            else:
                while a <len( self.beatmap[:-math.ceil(scale)]):
                    #print(a,b)
                    b=numpy.append(b, (1-(a%1))*self.beatmap[math.floor(a)]+(a%1)*self.beatmap[math.ceil(a)])
                    a+=scale
            self.beatmap=b

    def analyze_beats(self, lib='madmom.BeatDetectionProcessor', caching=True, split=None):
        print(f'analyzing beats using {lib}; ')
        #if audio is None and filename is None: (audio, samplerate) = open_audio()
        if caching is True:
            id=hex(len(self.audio[0]))
            import os
            if not os.path.exists('SavedBeatmaps'):
                os.mkdir('SavedBeatmaps')
            cacheDir="SavedBeatmaps/" + ''.join(self.filename.split('/')[-1]) + "_"+lib+"_"+id+'.txt'
            try: 
                self.beatmap=numpy.loadtxt(cacheDir, dtype=int)
                self.bpm=numpy.average(self.beatmap)/self.samplerate
                return
            except OSError: pass

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
        elif lib=='split':
            self.beatmap= list(range(0, len(self.audio), len(self.audio)//split))


        if lib.split('.')[0]=='madmom':
            self.beatmap=numpy.absolute(self.beatmap-500)
            
        if caching is True: numpy.savetxt(cacheDir, self.beatmap.astype(int), fmt='%d')
        self.bpm=numpy.average(self.beatmap)/self.samplerate
        self.beatmap=self.beatmap.astype(int)

    def generate_hitmap(self, lib='madmom.RNNBeatProcessor', caching=True):
        print(f'analyzing hits using {lib}; ')
        self.hitlib=lib
        """among us big chungus"""
        if caching is True:
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

            if caching is True: numpy.savetxt(cacheDir, self.beat_probabilities)
    
    def osu(self):
        print(f'generating osu file')
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
        f"AudioFilename: {self.filename.split('/')[-1]}\n"
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
        if self.filename is not None: 
            shutil.copyfile(self.filename, 'BeatManipulator_TEMP/'+self.filename.split('/')[-1])
        else: song.write_audio(self,'BeatManipulator_TEMP/audio.mp3')
        shutil.make_archive('BeatManipulator_TEMP', 'zip', 'BeatManipulator_TEMP')
        os.rename('BeatManipulator_TEMP.zip', outputfilename('', self.filename, '_'+self.hitlib, 'osz'))
        shutil.rmtree('BeatManipulator_TEMP')



    def audio_autotrim(self):
        print(f'autotrimming; ')
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
        print(f'autoscaling; ')
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
        print(f'autoinserting; ')
        diff=(self.beatmap[1]-self.beatmap[0])
        a=0
        while diff<self.beatmap[0] and a<100:
            self.beatmap=numpy.insert(self.beatmap, 0, self.beatmap[0]-diff)
            a+=1

    def beatmap_shift(self, shift: float):
        if shift!=0: print(f'shift={shift}; ')
        #print(shift)
        length=len(self.beatmap)
        if shift>0:
            if shift%1==0:
                for i in range(length-int(shift)-1):
                    #print(self.beatmap[i], end=', ')
                    self.beatmap[i] = self.beatmap[i+int(shift)]
                    #print(self.beatmap[i])
            else:
                for i in range(length-int(shift)-1):
                    self.beatmap[i] = self.beatmap[i] + shift * (self.beatmap[i+1] - self.beatmap[i])
        elif shift<0:
            if shift%1==0:
                for i in reversed(range(length)):
                    #print(self.beatmap[i], i-shift, length, end=', ')
                    if i+shift<0: self.beatmap[i] = self.beatmap[i]+(shift-i)
                    else: self.beatmap[i] = self.beatmap[i+shift]
                    #print(self.beatmap[i])
            else:
                for i in reversed(range(length)):
                    #print(self.beatmap[i], end=', ')
                    if i+shift<0: self.beatmap[i] = self.beatmap[i]+(shift-i)
                    else: self.beatmap[i] = self.beatmap[i] + shift * (self.beatmap[i] - self.beatmap[i-1])
                    #print(self.beatmap[i])
                #self.beatmap = numpy.sort(self.beatmap)

    def beatmap_trim(self, start=0, end=None):
        if start!=0 or end is not None: print(f'start={start}; end={end}; ')
        start*=self.samplerate
        self.beatmap=self.beatmap[self.beatmap>=start].astype(int)
        if end is not None: self.beatmap=self.beatmap[self.beatmap<=end].astype(int)


    def beatswap(self, pattern: str, sep=',', smoothing=40, smoothing_mode='replace'):
        import math, numpy
        # get pattern size
        size=0    
        #cut processing??? not worth it, it is really fast anyways
        pattern=pattern.replace(' ', '').split(sep)
        print(f"beatswapping with {' '.join(pattern)}; ")
        for j in pattern:
            s=''
            if '?' not in j:
                for i in j:
                    if i.isdigit() or i=='.' or i=='-' or i=='/' or i=='+' or i=='%': s=str(s)+str(i)
                    elif i==':':
                        if s=='': s='0'
                        #print(s, eval(s))
                        size=max(math.ceil(float(eval(s))), size)
                        s=''
                    elif s!='': break
                if s=='': s='0'
            if s=='': s='0'
            size=max(math.ceil(float(eval(s))), size)

        if isinstance(self.audio,numpy.ndarray): self.audio=numpy.ndarray.tolist(self.audio)
        if self.beatmap.dtype!='int32': self.beatmap=self.beatmap.astype(int)

        #beat=[]
        #start=audio[:beatmap[0]]
        #end=audio[beatmap[-1]:audio[-1]]
        #for i in range(len(beatmap)-1):
        #    beat[i]=audio[beatmap[i]:beatmap[i+1]]

        # audio is a tuple with l and r channels
        #print(len(audio))

        self.audio=(self.audio[0], self.audio[1])
        #print(beatmap[0], audio[0][100])
        result=(self.audio[0][:self.beatmap[0]],self.audio[1][:self.beatmap[0]])
        beat=numpy.asarray([[],[]])

        # size, iterations are integers
        size=int(max(size//1, 1))
    

        # add beat to the end
        self.beatmap=numpy.abs(numpy.append(self.beatmap, len(self.audio[0])))

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
                            #print ('Beat start:',s,'=', eval(s),'=',int(eval(s)//1), '+',j,'*',size,'    =',int(eval(s)//1)+j*size, ',   mod=',eval(s)%1)
                            try: st=self.beatmap[int(eval(s)//1)+j*size ] + eval(s)%1* (self.beatmap[int(eval(s)//1)+j*size +1] - self.beatmap[int(eval(s)//1)+j*size])
                            except IndexError: break
                            s=''
                        
                        # create a beat
                        if s!='' and (n==len(i) or not(c.isdigit() or c=='.' or c=='-' or c=='/' or c=='+' or c=='%')):

                            # start already exists
                            if st is not None:
                                #print ('Beat end:  ',s,'=', eval(s),'=',int(eval(s)//1), '+',j,'*',size,'    =',int(eval(s)//1)+j*size, ',   mod=',eval(s)%1)
                                try:
                                    s=self.beatmap[int(eval(s)//1)+j*size ] + eval(s)%1* (self.beatmap[int(eval(s)//1)+j*size +1] - self.beatmap[int(eval(s)//1)+j*size])
                                    #print(s)
                                except IndexError: break
                            else:
                                # start doesn't exist
                                #print ('Beat start:',s,'=', eval(s),'=',int(eval(s)//1), '+',j,'*',size,'- 1 =',int(eval(s)//1)+j*size,   ',   mod=',eval(s)%1)
                                #print ('Beat end:  ',s,'=', eval(s),'=',int(eval(s)//1), '+',j,'*',size,'    =',int(eval(s)//1)+j*size+1, ',   mod=',eval(s)%1)
                                try:
                                    st=self.beatmap[int(eval(s)//1)+j*size-1 ] + eval(s)%1* (self.beatmap[int(eval(s)//1)+j*size +1] - self.beatmap[int(eval(s)//1)+j*size])
                                    s=self.beatmap[int(eval(s)//1)+j*size ] + eval(s)%1* (self.beatmap[int(eval(s)//1)+j*size +1] - self.beatmap[int(eval(s)//1)+j*size])
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
                                elif eval(z)==0:beat[0]*=0
                                else:beat[1]*=0

                            # volume
                            z=beatswap_getnum(i,'v')
                            if z is not None:
                                if z=='': z='0'
                                beat*=eval(z)

                            z=beatswap_getnum(i,'t')
                            if z is not None:
                                if z=='': z='2'
                                beat**=1/eval(z)

                            # speed
                            z=beatswap_getnum(i,'s')
                            if z is not None:
                                if z=='': z='2'
                                z=eval(z)
                                if z<1: 
                                    beat=numpy.asarray((numpy.repeat(beat[0],int(1//z)),numpy.repeat(beat[1],int(1//z))))
                                else:
                                    beat=numpy.asarray((beat[0,::int(z)],beat[1,::int(z)]))
                            
                            # bitcrush
                            z=beatswap_getnum(i,'b')
                            if z is not None:
                                if z=='': z='3'
                                z=1/eval(z)
                                if z<1: beat=beat*z
                                beat=numpy.around(beat, max(int(z), 1))
                                if z<1: beat=beat/z

                            # downsample
                            z=beatswap_getnum(i,'d')
                            if z is not None:
                                if z=='': z='3'
                                z=int(eval(z))
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
        #print(time.process_time() - benchmark)

        self.audio = result

    def beatsample(self, audio2, shift=0):
        print(f'beatsample; ')
        try: l=len(audio2[0])
        except (TypeError, IndexError): 
            l=len(audio2)
            audio2=numpy.vstack((audio2,audio2))
        for i in range(len(self.beatmap)):
            #print(self.beatmap[i])
            try: self.audio[:,int(self.beatmap[i]) + int(float(shift) * (int(self.beatmap[i+1])-int(self.beatmap[i]))) : int(self.beatmap[i])+int(float(shift) * (int(self.beatmap[i+1])-int(self.beatmap[i])))+int(l)]+=audio2
            except (IndexError, ValueError): pass

    def hitsample(self, audio2=None):
        print(f'hitsample; ')
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
        print(f'sidechain; ')
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
        print('___')
        if self.beatmap is None: song.analyze_beats(self,lib=lib)
        if autotrim is True: song.audio_autotrim(self)
        save=self.beatmap
        if autoscale is True: song.beatmap_autoscale(self)
        if shift!=0: song.beatmap_shift(self,shift)
        if scale!=1: song.beatmap_scale(self,scale)
        if autoinsert is True: song.beatmap_autoinsert(self)
        if start!=0 or end is not None: song.beatmap_trim(self,start, end)
        song.beatswap(self,pattern)

        if output is not None:
            if not (output.lower().endswith('.mp3') or output.lower().endswith('.wav') or output.lower().endswith('.flac') or output.lower().endswith('.ogg') or 
            output.lower().endswith('.aac') or output.lower().endswith('.ac3') or output.lower().endswith('.aiff')  or output.lower().endswith('.wma')):
                output=output+'.'.join(''.join(self.filename.split('/')[-1]).split('.')[:-1])+suffix+'.mp3'
            song.write_audio(self,output)

        self.beatmap=save


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
        print('___')
        if filename2 is None and audio2 is None:
            audio2=generate_sidechain()

        if audio2 is None:
            audio2, samplerate2=open_audio(filename2)

        if self.beatmap is None: song.analyze_beats(self,lib=lib)
        if autotrim is True: song.audio_autotrim(self)
        save=self.beatmap
        if autoscale is True: song.beatmap_autoscale(self)
        if shift!=0: song.beatmap_shift(self,shift)
        if scale!=1: song.beatmap_scale(self,scale)
        if autoinsert is True: song.beatmap_autoinsert(self)
        if start!=0 or end is not None: song.beatmap_trim(self,start, end)
        song.sidechain(self,audio2)

        if output is not None:
            if not (output.lower().endswith('.mp3') or output.lower().endswith('.wav') or output.lower().endswith('.flac') or output.lower().endswith('.ogg') or 
            output.lower().endswith('.aac') or output.lower().endswith('.ac3') or output.lower().endswith('.aiff')  or output.lower().endswith('.wma')):
                output=output+'.'.join(''.join(self.filename.split('/')[-1]).split('.')[:-1])+suffix+'.mp3'
            song.write_audio(self,output)
        
        self.beatmap=save

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
        print('___')
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
        if scale!=1: song.beatmap_scale(self,scale)
        if autoinsert is True: song.beatmap_autoinsert(self)
        if start!=0 or end is not None: song.beatmap_trim(self,start, end)
        song.beatsample(self,audio2)

        if output is not None:
            if not (output.lower().endswith('.mp3') or output.lower().endswith('.wav') or output.lower().endswith('.flac') or output.lower().endswith('.ogg') or 
            output.lower().endswith('.aac') or output.lower().endswith('.ac3') or output.lower().endswith('.aiff')  or output.lower().endswith('.wma')):
                output=output+'.'.join(''.join(self.filename.split('/')[-1]).split('.')[:-1])+suffix+'.mp3'
            song.write_audio(self,output)
        self.beatmap=save
        
    def audio_spectogram(self, hop_length:int=512):
        self.hop_length=hop_length
        import librosa
        self.spectogram=librosa.feature.melspectrogram(y=self.audio, sr=self.samplerate, hop_length=hop_length)

    def spectogram_audio(self):
        import librosa
        self.audio=librosa.feature.inverse.mel_to_audio(M=numpy.swapaxes(numpy.swapaxes(numpy.dstack(( self.spectogram[0,:,:],  self.spectogram[1,:,:])), 0, 2), 1,2), sr=self.samplerate, hop_length=self.hop_length)

    def write_image(self):
        """Turns song into an image based on beat positions. Currently semi-broken"""
        import cv2
        audio=self.audio[0].tolist()
        height=len(audio)/len(self.beatmap)
        width=len(self.beatmap)
        height*=3
        if height>width:
            increase_length=int(height/width)
            reduce_width=1
        else: 
            reduce_width=int(width/height)
            increase_length=1
        increase_length/=10
        reduce_width*=10
        image=[audio[0:self.beatmap[0]]]
        maximum=len(image)
        for i in range(len(self.beatmap)-1):
            image.append(audio[self.beatmap[i]:self.beatmap[i+1]])
            maximum=max(maximum,len(image[i]))
        for i in range(len(image)):
            image[i].extend((maximum-len(image[i]))*[0])
            image[i]=image[i][::reduce_width]

        audio=self.audio[1].tolist()
        image2=[audio[0:self.beatmap[0]]]
        for i in range(len(self.beatmap)-1):
            image2.append(audio[self.beatmap[i]:self.beatmap[i+1]])
        for i in range(len(image2)):
            image2[i].extend((maximum-len(image2[i]))*[0])
            image2[i]=image2[i][::reduce_width]
            print(len(image[i]), len(image2[i]))

        image=numpy.asarray(image)*255
        image2=numpy.asarray(image2)*255
        image3=numpy.add(image, image2)/2
        image,image2,image3=numpy.repeat(image,increase_length,axis=0),numpy.repeat(image2,increase_length,axis=0),numpy.repeat(image3,increase_length,axis=0)
        image=cv2.merge([image.T,image2.T, image3.T])

        #image=image.astype('uint8')
        #image=cv2.resize(image, (0,0), fx=len(image))
        cv2.imwrite('cv2_output.png', image)

def fix_beatmap(filename, lib='madmom.BeatDetectionProcessor', scale=1, shift=0):
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
    track=open_audio(filename)[0]
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
