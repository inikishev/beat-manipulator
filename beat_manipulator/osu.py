from . import main
import numpy as np

# L L L L L L L L L 
def generate(song, difficulties = [0.2, 0.1, 0.05, 0.025, 0.01, 0.0075, 0.005, 0.0025], lib='madmom.MultiModelSelectionProcessor', caching=True, log = True, output = '', add_peaks = True):
    # for i in difficulties:
    #     if i<0.005: print(f'Difficulties < 0.005 may result in broken beatmaps, found difficulty = {i}')
    if lib.lower == 'stunlocked': add_peaks = False

    if not isinstance(song, main.song): song = main.song(song)
    if log is True: print(f'Using {lib}; ', end='')
    
    filename = song.path.replace('\\', '/').split('/')[-1]
    if ' - ' in filename and len(filename.split(' - '))>1: 
        artist = filename.split(' - ')[0]
        title = ' - '.join(filename.split(' - ')[1:])
    else:
        artist = ''
        title = filename
    
    if caching is True:
        audio_id=hex(len(song.audio[0]))
        import os
        if not os.path.exists('beat_manipulator/beatmaps'):
            os.mkdir('beat_manipulator/beatmaps')
        cacheDir="beat_manipulator/beatmaps/" + filename + "_"+lib+"_"+audio_id+'.txt'
        try: 
            beatmap=np.loadtxt(cacheDir)
            if log is True: print('loaded cached beatmap.')
        except OSError: 
            if log is True:print("beatmap hasn't been generated yet. Generating...")
            beatmap = None

    if beatmap is None:
        if 'madmom' in lib.lower():
            from collections.abc import MutableMapping, MutableSequence
            import madmom
            assert len(song.audio[0])>song.sr*2, f'Audio file is too short, len={len(song.audio[0])} samples, or {len(song.audio[0])/song.sr} seconds. Minimum length is 2 seconds, audio below that breaks madmom processors.'
        if lib=='madmom.RNNBeatProcessor':
            proc = madmom.features.beats.RNNBeatProcessor()
            beatmap = proc(madmom.audio.signal.Signal(song.audio.T, song.sr))
        elif lib=='madmom.MultiModelSelectionProcessor':
            proc = madmom.features.beats.RNNBeatProcessor(post_processor=None)
            predictions = proc(madmom.audio.signal.Signal(song.audio.T, song.sr))
            mm_proc = madmom.features.beats.MultiModelSelectionProcessor(num_ref_predictions=None)
            beatmap= mm_proc(predictions)*song.sr
            beatmap/= np.max(beatmap)
        elif lib=='stunlocked':
            spikes = np.abs(np.gradient(np.clip(song.audio[0], -1, 1)))[:int(len(song.audio[0]) - (len(song.audio[0])%int(song.sr/100)))]
            spikes = spikes.reshape(-1, (int(song.sr/100)))
            spikes = np.asarray(list(np.max(i) for i in spikes))
            if len(beatmap) > len(spikes): beatmap = beatmap[:len(spikes)]
            elif len(spikes) > len(beatmap): spikes = spikes[:len(beatmap)]
            zeroing = 0
            for i in range(len(spikes)):
                if zeroing > 0:
                    if spikes[i] <= 0.1: zeroing -=1
                    spikes[i] = 0
                elif spikes[i] >= 0.1:
                    spikes[i] = 1
                    zeroing = 7
                if spikes[i] <= 0.1: spikes[i] = 0
            beatmap = spikes

        if caching is True: np.savetxt(cacheDir, beatmap)
        
    if add_peaks is True:
        spikes = np.abs(np.gradient(np.clip(song.audio[0], -1, 1)))[:int(len(song.audio[0]) - (len(song.audio[0])%int(song.sr/100)))]
        spikes = spikes.reshape(-1, (int(song.sr/100)))
        spikes = np.asarray(list(np.max(i) for i in spikes))
        if len(beatmap) > len(spikes): beatmap = beatmap[:len(spikes)]
        elif len(spikes) > len(beatmap): spikes = spikes[:len(beatmap)]
        zeroing = 0
        for i in range(len(spikes)):
            if zeroing > 0:
                if spikes[i] <= 0.1: zeroing -=1
                spikes[i] = 0
            elif spikes[i] >= 0.1:
                spikes[i] = 1
                zeroing = 7
            if spikes[i] <= 0.1: spikes[i] = 0
    else: spikes = None

    def _process(song: main.song, beatmap, spikes, threshold):
        '''ඞ'''
        if add_peaks is True: beatmap += spikes
        hitmap=[]
        actual_samplerate=int(song.sr/100)
        beat_middle=int(actual_samplerate/2)
        for i in range(len(beatmap)):
            if beatmap[i]>threshold: hitmap.append(i*actual_samplerate + beat_middle)
        hitmap=np.asarray(hitmap)
        clump=[]
        for i in range(len(hitmap)-1):
            #print(i, abs(song.beatmap[i]-song.beatmap[i+1]), clump)
            if abs(hitmap[i] - hitmap[i+1]) < song.sr/16 and i != len(hitmap)-2: clump.append(i)
            elif clump!=[]: 
                clump.append(i)
                actual_time=hitmap[clump[0]]
                hitmap[np.array(clump)]=0
                #print(song.beatmap)
                hitmap[clump[0]]=actual_time
                clump=[]
        
        hitmap=hitmap[hitmap!=0]
        return hitmap
    
    osufile=lambda title,artist,version: ("osu file format v14\n"
    "\n"
    "[General]\n"
    f"AudioFilename: {song.path.split('/')[-1]}\n"
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
    f'Creator:{lib} + BeatManipulator\n'
    f'Version:{version} {lib}\n'
    'Source:\n'
    'Tags:BeatManipulator\n'
    'BeatmapID:0\n'
    'BeatmapSetID:-1\n'
    '\n'
    '[Difficulty]\n'
    'HPDrainRate:4\n'
    'CircleSize:4\n'
    'OverallDifficulty:5\n'
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
    #print(self.beatmap)

    #print(self.beatmap)

    
    #print(len(osumap))
    #input('banana')
    import shutil, os
    if os.path.exists('beat_manipulator/temp'): shutil.rmtree('beat_manipulator/temp')
    os.mkdir('beat_manipulator/temp')
    hitmap=[]
    import random
    for difficulty in difficulties:
        for i in range(4):
            #print(i)
            this_difficulty=_process(song, beatmap, spikes, difficulty)
        hitmap.append(this_difficulty)

    for k in range(len(hitmap)):
        osumap=np.vstack((hitmap[k],np.zeros(len(hitmap[k])),np.zeros(len(hitmap[k])))).T
        difficulty= difficulties[k]
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

        file=osufile(artist, title, difficulty)
        for j in osumap:
            #print('285,70,'+str(int(int(i)*1000/self.samplerate))+',1,0')
            file+=f'{int(j[1])},{int(j[2])},{str(int(int(j[0])*1000/song.sr))},1,0\n'
        with open(f'beat_manipulator/temp/{artist} - {title} (BeatManipulator {difficulty} {lib}].osu', 'x', encoding="utf-8") as f:
            f.write(file)
    from . import io
    import shutil, os
    shutil.copyfile(song.path, 'beat_manipulator/temp/'+filename)
    shutil.make_archive('beat_manipulator_osz', 'zip', 'beat_manipulator/temp')
    outputname = io._outputfilename(path = output, filename = song.path, suffix = ' ('+lib + ')', ext = 'osz')
    if not os.path.exists(outputname):
        os.rename('beat_manipulator_osz.zip', outputname)
        if log is True: print(f'Created `{outputname}`')
    else: print(f'{outputname} already exists!')
    shutil.rmtree('beat_manipulator/temp')
    return outputname