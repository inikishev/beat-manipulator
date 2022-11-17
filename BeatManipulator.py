def open_audio(filename=None, lib='pedalboard.io'):
    if filename is None:
        from tkinter.filedialog import askopenfilename
        filename = askopenfilename(title='select song', filetypes=[("mp3", ".mp3"),("wav", ".wav"),("flac", ".flac"),("ogg", ".ogg"),("wma", ".wma")])
    filename=filename.replace('\\', '/')
    if lib=='pedalboard.io':
        from pedalboard.io import AudioFile
        with AudioFile(filename) as f:
            audio = f.read(f.frames)
            samplerate = f.samplerate
    return audio,samplerate


def analyze_beats(filename=None, audio=None, samplerate=44100, lib='madmom.BeatDetectionProcessor', caching=True, split=None):
    if audio is None and filename is None: (audio, samplerate) = open_audio()

    if caching is True and filename is not None:
        import hashlib
        with open(filename, "rb") as f:
            file_hash = hashlib.blake2b()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        import os
        if not os.path.exists('SavedBeatmaps'):
            os.mkdir('SavedBeatmaps')
        import numpy
        cacheDir="SavedBeatmaps/" + ''.join(filename.split('/')[-1]) + lib+"_"+file_hash.hexdigest()[:5]+'.txt'
        try: return numpy.loadtxt(cacheDir, dtype=int)
        except OSError: pass
        
    if lib.split('.')[0]=='madmom':
        from collections.abc import MutableMapping, MutableSequence
        import madmom
        if audio is None: audio=filename
        else: 
            audio=madmom.audio.signal.Signal(audio.T, samplerate)

    if lib=='madmom.BeatTrackingProcessor':
        proc = madmom.features.beats.BeatTrackingProcessor(fps=100)
        act = madmom.features.beats.RNNBeatProcessor()(audio)
        beatmap= proc(act)*samplerate
    elif lib=='madmom.BeatTrackingProcessor.constant':
        proc = madmom.features.beats.BeatTrackingProcessor(fps=100, look_aside=0)
        act = madmom.features.beats.RNNBeatProcessor()(audio)
        beatmap= proc(act)*samplerate
    elif lib=='madmom.BeatDetectionProcessor':
        proc = madmom.features.beats.BeatDetectionProcessor(fps=100)
        act = madmom.features.beats.RNNBeatProcessor()(audio)
        beatmap= proc(act)*samplerate
    elif lib=='madmom.CRFBeatDetectionProcessor':
        proc = madmom.features.beats.CRFBeatDetectionProcessor(fps=100)
        act = madmom.features.beats.RNNBeatProcessor()(audio)
        beatmap= proc(act)*samplerate
    elif lib=='madmom.DBNBeatTrackingProcessor':
        proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=100)
        act = madmom.features.beats.RNNBeatProcessor()(audio)
        beatmap= proc(act)*samplerate
    elif lib=='Split':
        beatmap= list(range(0, len(audio), len(audio)//split))
        
    if caching is True: numpy.savetxt(cacheDir, beatmap.astype(int))
    return beatmap
    
def write_audio(audio, output='BeatManipulator.mp3', samplerate=44100, lib='pedalboard.io'):
    if lib=='pedalboard.io':
        import numpy
        if not isinstance(audio,numpy.ndarray): audio=numpy.asarray(audio)
        from pedalboard.io import AudioFile
        with AudioFile(output, 'w', samplerate, audio.shape[0]) as f:
            f.write(audio)
    

# ''.join(filename.split('/')[-1]).split('.')[:-1])+'_bm.mp3'
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

def beatswap(filename=None, pattern=None, output='', scale=1.0, shift=0, start=0, end=None, autoscale=False, autoinsert=True, trim=True, sep=',', smoothing=40, smoothing_mode='replace', audio= None, samplerate=None, beatmap=None, libBeat='madmom.BeatDetectionProcessor', caching=True):
    import math, numpy

    # ask for a file
    if audio is None and filename is None:
        from tkinter.filedialog import askopenfilename
        filename = askopenfilename(title='select song', filetypes=[("mp3", ".mp3"),("wav", ".wav"),("flac", ".flac"),("ogg", ".ogg"),("wma", ".wma")])
    
    # open the file
    if filename is not None: 
        filename=filename.replace('\\', '/')
        if audio is None or samplerate is None:
            (audio, samplerate) = open_audio(filename)

    # analyze beats
    if beatmap is None:
        beatmap=analyze_beats(filename=filename, samplerate=samplerate, lib=libBeat, caching=caching)

    #trim silence
    if trim is True:
        n=0
        for i in audio[0]:
            if i>=0.0001:break
            n+=1
        audio = numpy.asarray([audio[0,n:], audio[1,n:]])
        #print(beatmap)
        beatmap=numpy.absolute(beatmap-n)
        #print(beatmap)


    #import time
    #benchmark = time.process_time()
    if not isinstance(beatmap,numpy.ndarray): beatmap=numpy.asarray(beatmap)

    #normalize BPM
    diff=(beatmap[1]-beatmap[0])
    bpm=(beatmap[-1]-beatmap[0])/(len(beatmap)-1)
    #print('BPM =', (bpm/samplerate) * 240, bpm)
    if autoscale is True:
        if bpm>=160000: scale/=8
        elif (bpm)>=80000: scale/=4
        elif (bpm)>=40000: scale/=2
        elif (bpm)<=20000: scale*=2
        elif (bpm)<=10000: scale*=4
        elif (bpm)<=5000: scale*=8

    # add beat to the end
    beatmap=numpy.append(beatmap, len(audio[0]))

    # get pattern size
    size=0    
    #cut processing??? not worth it, it is really fast anyways
    pattern=pattern.replace(' ', '').split(sep)
    for j in pattern:
        s=''
        if '?' not in j:
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

    # scale beatmap
    if scale!=1:
        a=0
        b=numpy.array([])
        while a <len( beatmap[:-math.ceil(scale)]):
            b=numpy.append(b, (1-(a%1))*beatmap[math.floor(a)]+(a%1)*beatmap[math.ceil(a)])
            a+=scale
        beatmap = b
    
    # autoinsert beats to the beginning
    if autoinsert is True:
        while diff<beatmap[0]:
            beatmap=numpy.insert(beatmap, 0, beatmap[0]-diff)

    # shift (doesn't really work)
    if shift>0 and shift%1==0:
        for i in range(shift): beatmap=numpy.insert(beatmap, 0, i+2)
    elif shift!=0:
        for i in range(int(16-float(shift))): beatmap=numpy.insert(beatmap, 0, i+2)
    #beatmap=numpy.insert(beatmap,0,0)

    # apply start and end time
    start*=samplerate
    beatmap=beatmap[beatmap>=start].astype(int)
    if end!=None: beatmap=beatmap[beatmap<=end].astype(int)

    if isinstance(audio,numpy.ndarray): audio=numpy.ndarray.tolist(audio)

    #beat=[]
    #start=audio[:beatmap[0]]
    #end=audio[beatmap[-1]:audio[-1]]
    #for i in range(len(beatmap)-1):
    #    beat[i]=audio[beatmap[i]:beatmap[i+1]]

    # audio is a tuple with l and r channels
    #print(len(audio))
    if len(audio)>1: 
        audio=(audio[0], audio[1])
        #print(beatmap[0], audio[0][100])
        result=(audio[0][:beatmap[0]],audio[1][:beatmap[0]])
        beat=numpy.asarray([[],[]])
    else: 
        audio=(audio[0])
        result=(audio[0][:beatmap[0]])
        beat=numpy.asarray[[]]

    # size, iterations are integers
    size=int(max(size//1, 1))
    iterations=int(len(beatmap)//size)

    #print(size, iterations)
    # processing
    for j in range(iterations):
        for i in pattern:
            if '!' not in i:
                n,s,st,reverse,z=0,'',None,False,None
                for c in i:
                    n+=1
                    #print('s =', s, ',  st =', st, ',   c =', c, ',   n =,',n)

                    # Get the character
                    if c.isdigit() or c=='.' or c=='-' or c=='/' or c=='+' or c=='%': 
                        s=str(s)+str(c)
                    
                    # If character is : - get start
                    elif s!='' and c==':':
                        #print ('Beat start:',s,'=', eval(s),'=',int(eval(s)//1), '+',j,'*',size,'    =',int(eval(s)//1)+j*size, ',   mod=',eval(s)%1)
                        try: st=beatmap[int(eval(s)//1)+j*size ] + eval(s)%1* (beatmap[int(eval(s)//1)+j*size +1] - beatmap[int(eval(s)//1)+j*size])
                        except IndexError: break
                        s=''
                    
                    # create a beat
                    if s!='' and (n==len(i) or not(c.isdigit() or c=='.' or c=='-' or c=='/' or c=='+' or c=='%')):

                        # start already exists
                        if st is not None:
                            #print ('Beat end:  ',s,'=', eval(s),'=',int(eval(s)//1), '+',j,'*',size,'    =',int(eval(s)//1)+j*size, ',   mod=',eval(s)%1)
                            try:
                                s=beatmap[int(eval(s)//1)+j*size ] + eval(s)%1* (beatmap[int(eval(s)//1)+j*size +1] - beatmap[int(eval(s)//1)+j*size])
                                #print(s)
                            except IndexError: break
                        else:
                            # start doesn't exist
                            #print ('Beat start:',s,'=', eval(s),'=',int(eval(s)//1), '+',j,'*',size,'- 1 =',int(eval(s)//1)+j*size,   ',   mod=',eval(s)%1)
                            #print ('Beat end:  ',s,'=', eval(s),'=',int(eval(s)//1), '+',j,'*',size,'    =',int(eval(s)//1)+j*size+1, ',   mod=',eval(s)%1)
                            try:
                                st=beatmap[int(eval(s)//1)+j*size-1 ] + eval(s)%1* (beatmap[int(eval(s)//1)+j*size +1] - beatmap[int(eval(s)//1)+j*size])
                                s=beatmap[int(eval(s)//1)+j*size ] + eval(s)%1* (beatmap[int(eval(s)//1)+j*size +1] - beatmap[int(eval(s)//1)+j*size])
                            except IndexError: break
                        
                        if st>s: 
                            s, st=st, s
                            reverse=True

                        # create the beat
                        if len(audio)>1: 
                            if smoothing_mode=='add': beat=numpy.asarray([audio[0][int(st):int(s)],audio[1][int(st):int(s)]])
                            else: beat=numpy.asarray([audio[0][int(st):int(s)-smoothing],audio[1][int(st):int(s)-smoothing]])
                        else:
                            if smoothing_mode=='add': beat=numpy.asarray([audio[0][int(st):int(s)]])
                            else: beat=numpy.asarray([audio[0][int(st):int(s)-smoothing]])

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
                                if len(beat) >1:
                                    beat=numpy.asarray((numpy.repeat(beat[0],int(1//z)),numpy.repeat(beat[1],int(1//z))))
                                else: beat=numpy.asarray((numpy.repeat(beat, int(1//z))))
                            else:
                                if len(beat) >1:
                                    beat=numpy.asarray((beat[0,::int(z)],beat[1,::int(z)]))
                                else: beat=numpy.asarray(beat[0,::int(z)])
                        
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
                            if len(beat) >1:
                                beat=numpy.asarray((numpy.repeat(beat[0,::z],z),numpy.repeat(beat[1,::z],z)))
                            else: beat=numpy.asarray((numpy.repeat(beat[::z], z)))

                        # convert to list
                        beat=beat.tolist()

                        # effects with list
                        # reverse
                        if ('r' in i and reverse is False) or (reverse is True and 'r' not in i):
                            if len(beat) >1:
                                beat=(beat[0][::-1],beat[1][::-1] )
                            else:beat=(beat[::-1])

                        # add beat to the result
                        for a in range(len(audio)): 
                            #print('Adding beat... a, s, st:', a, s, st, sep=',  ')
                            #print(result[a][-1])
                            #print(beat[a][0])
                            if smoothing>0: result[a].extend(numpy.linspace(result[a][-1],beat[a][0],smoothing))
                            result[a].extend(beat[a])
                            #print(len(result[0]))

                        #   
                        break
    #print(time.process_time() - benchmark)
    
    # create output
    if output is not None:
        if (not output.lower().endswith('.mp3') or output.lower().endswith('.wav') or output.lower().endswith('.flac') or output.lower().endswith('.ogg')) and filename is not None: output=output+''.join(''.join(filename.split('/')[-1]).split('.')[:-1])+'_bm.mp3'
        elif (not output.lower().endswith('.mp3') or output.lower().endswith('.wav') or output.lower().endswith('.flac') or output.lower().endswith('.ogg')) =='': output=output+'BeatManipulator_output.mp3'

    if output is not None: write_audio(result, output, samplerate)
    else: return result