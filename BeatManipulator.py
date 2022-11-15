def analyze_beats(filename=None, audio=None, samplerate=None, beatproc='madmom.BeatDetectionProcessor', split=4):
    if beatproc.split('.')[0]=='madmom':
        from collections.abc import MutableMapping, MutableSequence
        import madmom
        if audio is None: audio=filename
        else: 
            audio=madmom.audio.signal.Signal(audio.T, samplerate)
    else: 
        if audio is None:
            from pedalboard.io import AudioFile
            with AudioFile(filename) as f:
                audio = f.read(f.frames)
                if samplerate is None: samplerate = f.samplerate

    if beatproc=='madmom.BeatTrackingProcessor':
        proc = madmom.features.beats.BeatTrackingProcessor(fps=100)
        act = madmom.features.beats.RNNBeatProcessor()(audio)
        return proc(act)*samplerate
    elif beatproc=='madmom.BeatDetectionProcessor':
        proc = madmom.features.beats.BeatDetectionProcessor(fps=100)
        act = madmom.features.beats.RNNBeatProcessor()(audio)
        return proc(act)*samplerate
    elif beatproc=='madmom.CRFBeatDetectionProcessor':
        proc = madmom.features.beats.CRFBeatDetectionProcessor(fps=100)
        act = madmom.features.beats.RNNBeatProcessor()(audio)
        return proc(act)*samplerate
    elif beatproc=='madmom.DBNBeatTrackingProcessor':
        proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=100)
        act = madmom.features.beats.RNNBeatProcessor()(audio)
        return proc(act)*samplerate
    elif beatproc=='Split':
        return list(range(0, len(audio), len(audio)//split))
    
        
def beatswap(output='./', filename=None, audio= None, samplerate=None, beatmap=None, beatproc='madmom.BeatDetectionProcessor', caching=True, pattern=None, scale=1.0, shift=0, autoscale=True, autoinsert=True, start=0, end=None, sep=',', smoothing=40, smoothing_mode='add'):
    import math, numpy
    if filename is None and audio is None:
        from tkinter.filedialog import askopenfilename
        filename = askopenfilename(title='select song', filetypes=[("mp3", ".mp3"),("wav", ".wav"),("flac", ".flac"),("ogg", ".ogg"),("wma", ".wma")])

    if not filename is None: filename=filename.replace('\\', '/')
    if audio is None:
        from pedalboard.io import AudioFile
        with AudioFile(filename) as f:
            audio = f.read(f.frames)
            if samplerate is None: samplerate = f.samplerate

    if beatmap is None:
        import hashlib
        with open(filename, "rb") as f:
            file_hash = hashlib.blake2b()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        if caching is True:
            import os
            if not os.path.exists('SavedBeatmaps'):
                os.mkdir('SavedBeatmaps')
            savedbeatmaps="SavedBeatmaps/" + ''.join(filename.split('/')[-1]) + "c_"+file_hash.hexdigest()[:5]+'.txt'
            try: beatmap=numpy.loadtxt(savedbeatmaps, dtype=int)
            except OSError:
                beatmap=analyze_beats(filename, audio, samplerate, beatproc)
                numpy.savetxt(savedbeatmaps, beatmap.astype(int))
        else: beatmap=analyze_beats(filename, audio, samplerate, beatproc)

    diff=(beatmap[1]-beatmap[0])
    if autoscale is True:
        if diff>=160000: scale/=8
        elif (diff)>=80000: scale/=4
        elif (diff)>=40000: scale/=2
        elif (diff)<=20000: scale*=2
        elif (diff)<=10000: scale*=4
        elif (diff)<=5000: scale*=8


    size=0    
    #cut processing???
    pattern=pattern.split(sep)
    for j in pattern:
        s=''
        if '*' not in j:
            for i in j:
                if i.isdigit() or i=='.' or i=='-' or i=='/' or i=='+' or i=='%': s=str(s)+str(i)
                elif i==':':
                    if s=='': s='0'
                    size=max(math.ceil(float(eval(s))), size)
                    s=''
                elif s!='': break
            if s=='': s='0'
        if s=='': s='0'
        size=max(size, eval(s))

    if scale!=1:
        a=0
        b=numpy.array([])
        while a <len( beatmap[:-math.ceil(scale)]):
            b=numpy.append(b, (1-(a%1))*beatmap[math.floor(a)]+(a%1)*beatmap[math.ceil(a)])
            a+=scale
        beatmap = b
    
    if autoinsert is True:
        while diff<beatmap[0]:
            beatmap=numpy.insert(beatmap, 0, beatmap[0]-diff)

    if shift>0 and shift%1==0:
        for i in range(shift): beatmap=numpy.insert(beatmap, 0, i)
    elif shift!=0:
        for i in range(int(16-float(shift))): beatmap=numpy.insert(beatmap, 0, i)


    start*=samplerate
    beatmap=beatmap[beatmap>=start]
    if end!=None: beatmap=beatmap[beatmap<=end]

    if isinstance(audio,numpy.ndarray): audio=numpy.ndarray.tolist(audio)

    #beat=[]
    #start=audio[:beatmap[0]]
    #end=audio[beatmap[-1]:audio[-1]]
    #for i in range(len(beatmap)-1):
    #    beat[i]=audio[beatmap[i]:beatmap[i+1]]
    if len(audio)>1: 
        audio=(audio[0], audio[1])
        result=([0],[0])
    else: 
        audio=(audio)
        result=([0])

    size=int(max(size//1, 1))
    iterations=int(len(beatmap)//size)

    #print(size, iterations)
    for j in range(iterations):
        for i in pattern:
            s=''
            st = None
            if '*' not in i:
                n=0
                for c in i:
                    n+=1
                    #print(c, i, j, size, iterations)
                    if c.isdigit() or c=='.' or c=='-' or c=='/' or c=='+' or c=='%': 
                        s=str(s)+str(c)
                    elif s!='' and c==':':
                        try: st=beatmap[int(eval(s)//1)+j*size ] + eval(s)%1* (beatmap[int(eval(s)//1)+j*size +1] - beatmap[int(eval(s)//1)+j*size])
                        except IndexError: break
                        s=''
                    if s!='' and (n==len(i) or not(c.isdigit() or c=='.' or c=='-' or c=='/' or c=='+' or c=='%')):
                        if st is not None:
                            try:s=beatmap[int(eval(s)//1)+j*size ] + eval(s)%1* (beatmap[int(eval(s)//1)+j*size +1] - beatmap[int(eval(s)//1)+j*size])
                            except IndexError: break
                        else:
                            try:
                                st=beatmap[int(eval(s)//1)+j*size ] + eval(s)%1* (beatmap[int(eval(s)//1)+j*size +1] - beatmap[int(eval(s)//1)+j*size])
                                s=beatmap[int(eval(s)//1)+j*size+1 ] + eval(s)%1* (beatmap[int(eval(s)//1)+j*size +1] - beatmap[int(eval(s)//1)+j*size])
                            except IndexError: break
                        if smoothing_mode=='add':
                            for a in range(len(audio)): 
                                #print(a, s, st, sep=',  ')
                                if smoothing>0: result[a].extend(numpy.linspace(result[a][-1],audio[a][int(st)],smoothing))
                                if smoothing_mode=='add': result[a].extend(audio[a][int(st):int(s)])
                                else:result[a].extend(audio[a][int(st):int(s)-smoothing])
                                #print(len(result[0]))

    
    if output is not None: 
        result=numpy.asarray(result)
        from pedalboard.io import AudioFile
        with AudioFile(''.join(''.join(filename.split('/')[-1]).split('.')[:-1])+'_bm.mp3', 'w', samplerate, result.shape[0]) as f:
            f.write(result)
    else: return result