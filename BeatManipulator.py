# 0. import Big Ounce's audio effects
#   import BigOuncesAudioEffects as ba

# 1. Open an audio file
#   (audio, samplerate)=ba.r_pedalboard('path/to/audio')

# 2. audio variable is a numpy array. Leave it as is or convert to a spectogram. Note that converting back into audio is very slow. You can also use librosa.feature.melspectrogram(y=audio, sr=samplerate, hop_length=hop_length) directly, but you will need to separate l and r channels manually
#   ba.c_melspectrogram(audio, samplerate, hop_length=512) - hop_length: lower=higher quality
#   ba.c_mfcc(audio, samplerate, hop_length=512, sep=False) - sep: if set to true, left and right audio streams will be processed separately

# 3.1 Apply effects. Audio effects work better if you haven't converted to spectogram.
#   ba.a_bitcrush(audio, a=1)
#   ba.a_volume(audio,a=None) - if a isn't provided, it will be calculated automatically to normalize volume. a=1.5 means 150% volume.
#   ba.a_saturation(audio, a=2) - obtained by audio**(1/a). 
#   ba.a_saturation_smooth(audio, a=10) - obtained by sin(audio) a times.
#   ba.a_clip(audio, max=1, min=None) - clips the stream, where max=0.5 is 50% volume. If min is specified, max will clip the waveform at the top, and min at the bottom.
#   ba.a_distortion_abs(audio) - weird distortion. Use ba.a_vshift to autoshift the waveform after this
#   ba.a_distortion_cos(audio) - similar to abs distortion
#   ba.a_distortion_div(audio) - obnoxious distortion, recommended to clip or normalize volume after
#   ba.a_distortion_mod(audio) - a very weird distortion
#   ba.a_reverse(audio) - reverses the audio
#   ba.a_speed(audio, a: float) - make the stream faster/slower by factor of a. Note: faster stream means it is higher pitch.
#   ba.a_inverse(audio) - inverses the waveform. Has no impact on the sound
#   ba.a_vshift(audio, a=None) - vertically shifts the waveform. If a isn't specified, it is calculated automatically to normalize the waveform.
#   ba.a_auto(audio) - combines autoshift and autovolume
#   ba.a_cut(audio, samplerate, s=None, e=None) - cuts the audio. S is start in seconds, e is end in seconds.

# 3.2 Image effects work better on spectograms
#   ba.i_resize (audio, x=0, y=0, xmax=0, ymax=0, interpolation = None) - resizes the image. Or you can set xmax and ymax instead, which will only resize if image is bigger than them
#   ba.i_scale (audio, x=0, y=0, interpolation = None) - similar to a_speed, but you can also set y value and interpolation
#   ba.i_inverse(audio) - inverts the image

# 3.3. If you converted into spectogram, convert back into audio
#   ba.u_melspectrogram(audio, samplerate, hop_length=512)
#   ba.u_mfcc(audio, samplerate, hop_length=512)

# 4. Write a file
#   w_pedalboard(audio, samplerate, output='pedalboard_output.mp3') - output a sound file. Can be any format that pedalboard supports.
#   w_cv2image(audio, output='cv2_output.png', max=100000000) - output an image. To avoid the image being too big max=100000000 is pixel amount cap.

import numpy
#Import os
#if not os.path.exists('BigOuncesAudioEffects'):
    #os.mkdir('BigOuncesAudioEffects')
#Open the file
#Pedalboard
def r_pedalboard(file: str):
    from pedalboard.io import AudioFile
    with AudioFile(file) as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate
    return audio, samplerate

#Convert the file
def c_melspectrogram(audio, samplerate, hop_length=512):
    import librosa
    audio=librosa.feature.melspectrogram(y=audio, sr=samplerate, hop_length=hop_length)
    if audio.ndim >=3: return audio[0,:,:], audio[1,:,:]
    else: return audio

def c_mfcc(audio, samplerate, hop_length=512, sep=False):
    import librosa
    if sep==True: audio=numpy.dstack((librosa.feature.mfcc(y=audio[0:,:], sr=samplerate, hop_length=hop_length), librosa.feature.mfcc(y=audio[1:,:], sr=samplerate, hop_length=hop_length)))
    else: audio = librosa.feature.mfcc(y=audio, sr=samplerate)
    return audio

#effects
#bitcrush
def a_bitcrush(audio, a=1):
    if a<=0: return numpy.around(audio)
    else: a=1/a
    if a<1: audio=audio*a
    audio=numpy.around(audio, max(int(a), 1))
    if a<1: audio=audio/a
    return audio

#volume, autovolume
def a_volume(audio,a=None):
    if a==None: a=1-(max(numpy.max(audio), abs(numpy.min(audio))))
    return audio*a

#saturation
def a_saturation(audio, a=2):
    return audio**(1/a)

#sin saturation
def a_saturation_smooth(audio, a=10):
    for i in range(a): audio=numpy.sin(audio)
    return audio

#clip
def a_clip(audio, max=1, min=None):
    if min==None: min=-max
    return numpy.clip(audio, min, max)

#distortion
def a_distortion_abs(audio):
    return abs(audio)

def a_distortion_cos(audio):
    return numpy.cos(audio)

def a_distortion_div(audio):
    return 1/audio

def a_distortion_mod(audio):
    if type(audio) is tuple: return a_distortion_mod(audio[0]), a_distortion_mod(audio[1])
    else: return audio[:,:-1]%audio[:,1:]

#reverse
def a_reverse(audio):
    if type(audio) is tuple: return a_reverse(audio[0]), a_reverse(audio[1])
    else: return audio[:,::-1]

def a_cut(audio, samplerate, s=None, e=None):
    s*=samplerate
    e*=samplerate
    s=int(s)
    e=int(e)
    if s>len(audio[1,:]) or s<0: s=0
    if e>len(audio[1,:]) or (e<s and e>0): e=len(audio[1,:])
    if type(audio) is tuple: return a_cut(audio[0]), a_cut(audio[1])
    else: 
        if s==None: return audio[:,:e]
        elif e==None: return audio[:,s:]
        else: return audio[:,s:e]

#speed
def a_speed(audio, a: float):
    if type(audio) is tuple: return a_speed(audio[0], a), a_speed(audio[1], a)
    elif a>=1:
        if a%1==0:return audio[:,::a]
        else:
            import cv2
            return cv2.resize(audio, (0,0), fx=a, interpolation = cv2.INTER_NEAREST)
    elif (1/a)%1==0: return numpy.repeat(audio, a, axis=1)
    else: 
        import cv2
        return cv2.resize(audio, (0,0), fx=a, interpolation = cv2.INTER_NEAREST)

#inverse
def a_inverse(audio):
    return -audio
def i_inverse(audio):
    return -audio

#shift, autoshift
def a_vshift(audio, a=None):
    if a==None: a=(numpy.max(audio)+numpy.min(audio))/2
    return audio-a

#auto fit into -1, 1
def a_auto(audio):
    audio=audio-(numpy.min(audio)+numpy.max(audio))/2
    return audio*(1-(max(numpy.max(audio), abs(numpy.min(audio)))))

def i_resize (audio, x=0, y=0, xmax=0, ymax=0, interpolation = None):
    import cv2
    if interpolation==None: interpolation=cv2.INTER_LINEAR
    if type(audio) is tuple: return i_resize(audio[0], x, y,xmax,ymax, interpolation), i_resize(audio[1], x, y,xmax,ymax, interpolation)
    else: return cv2.resize(src=audio, dsize=(max(x,min(audio[0],xmax)),max(y,min(audio[1],ymax))), interpolation = interpolation)

def i_scale (audio, x=0, y=0, interpolation = None):
    import cv2
    if interpolation==None: interpolation=cv2.INTER_LINEAR
    if type(audio) is tuple: return i_scale(audio[0], x, y, interpolation), i_scale(audio[1], x, y,interpolation)
    else: 
        if x==0:return cv2.resize(audio, (0,0), fy=y, interpolation = interpolation)
        else:return cv2.resize(audio, (0,0), fx=x, interpolation = interpolation)


def u_melspectrogram(audio, samplerate, hop_length=512):
    import librosa
    if type(audio) is tuple: return librosa.feature.inverse.mel_to_audio(M=numpy.swapaxes(numpy.swapaxes(numpy.dstack((audio[0,:,:], audio[1,:,:])), 0, 2), 1,2), sr=samplerate, hop_length=hop_length)
    else: return librosa.feature.inverse.mel_to_audio(M=audio, sr=samplerate, hop_length=hop_length)

def u_mfcc(audio, samplerate, hop_length=512):
    import librosa
    if type(audio) is tuple: return librosa.feature.inverse.mfcc_to_audio(M=numpy.swapaxes(numpy.swapaxes(numpy.dstack((audio[0,:,:], audio[1,:,:])), 0, 2), 1,2), sr=samplerate, hop_length=hop_length)
    return librosa.feature.inverse.mfcc_to_audio(mfcc=audio, sr=samplerate, hop_length=hop_length)

def w_cv2image(audio, output='cv2_output.png', max=100000000): 
    import cv2
    if type(audio) is tuple:
        w_cv2image(audio[0], output+'_l', max)
        w_cv2image(audio[1], output+'_r', max)
    else:
        if audio.size>max: print ('Array has more than max=', max, 'items, resize it or set the max argument')
        else: cv2.imwrite(output, audio)

def w_pedalboard(audio, samplerate, output='pedalboard_output.mp3'):
    from pedalboard.io import AudioFile
    with AudioFile(output, 'w', samplerate, audio.shape[0]) as f:
        f.write(audio)

def beats_librosa_constant(audio, samplerate, r=1):
    import librosa
    return numpy.arange(0, len(audio[0,:]), (samplerate*60)/round(float(librosa.beat.tempo(y=audio, sr=samplerate)[1]), r) )
    

def beats_librosa_variable(audio, samplerate):
    import librosa
    bpm = (samplerate*60)/librosa.beat.tempo(y=audio, sr=samplerate, aggregate=None)
    if bpm.ndim>1: bpm=(bpm[0,:]+bpm[1,:])/2
    a=0
    length = len(audio[0,:])
    for i in bpm[:-1]: 
        if bpm[a+1]+bpm[a]<=length: 
            bpm[a+1]+=bpm[a]
            a+=1
    return bpm

def b_each(audio, audio2, beats, scale=1, shift=0):
    l=len(audio2[0,:])
    if scale!=1:
        import math
        a=0
        b=numpy.array
        while a <len( beats[:-math.ceil(scale)]):
            b=numpy.append(b, (1-(a%1))*beats[math.floor(a)]+(a%1)*beats[math.ceil(a)])
            a+=scale
        beats = b
        shift/=scale
    for i in range(len(beats)):
        try: audio[:,int(beats[i]) + int(float(shift) * (int(beats[i+1])-int(beats[i]))) : int(beats[i])+int(float(shift) * (int(beats[i+1])-int(beats[i])))+int(l)]+=audio2
        except: pass
    return audio

def b_shift(beats, shift):
    beats=beats+shift*(beats[1]-beats[0])
    return beats[beats>=0] 


def beats_madmom0(filename, interval=64):
    from collections.abc import MutableMapping, MutableSequence
    import madmom
    proc = madmom.features.beats.RNNBeatProcessor()
    return madmom.features.beats.detect_beats(proc(filename), interval)

def beats_madmom_variable(filename, samplerate):
    import hashlib
    with open(filename, "rb") as f:
        file_hash = hashlib.blake2b()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    try: 
        with open("SavedBeatmaps/v_"+file_hash.hexdigest(),"r") as f:
            return numpy.fromstring(f.read())
    except FileNotFoundError:
        from collections.abc import MutableMapping, MutableSequence
        import madmom
        proc = madmom.features.beats.BeatTrackingProcessor(fps=100)
        act = madmom.features.beats.RNNBeatProcessor()(filename)
        beats=proc(act)*samplerate
        with open("SavedBeatmaps/v_"+file_hash.hexdigest(),"a+") as f:
            f.write(numpy.array2string(beats).replace('.',','))
    return beats

def beats_madmom_constant(filename, samplerate):
    import hashlib
    with open(filename, "rb") as f:
        file_hash = hashlib.blake2b()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    try: return numpy.loadtxt("SavedBeatmaps/" + ''.join(filename.split('/')[-1]) + "c_"+file_hash.hexdigest()[:5]+'.txt')
    except OSError:
        from collections.abc import MutableMapping, MutableSequence
        import madmom
        proc = madmom.features.beats.BeatDetectionProcessor(fps=100)
        act = madmom.features.beats.RNNBeatProcessor()(filename)
        beats=proc(act)*samplerate
        numpy.savetxt("SavedBeatmaps/" + ''.join(filename.split('/')[-1]) + "c_"+file_hash.hexdigest()[:5]+'.txt', beats)
        #with open("BigOuncesAudioEffects/c_"+file_hash.hexdigest()+'.txt',"a+") as f:
            #f.write(numpy.array2string(beats, formatter={'all':lambda x: str(x)}, separator=',').replace('[',))
    return(beats)


def beats_madmom_constant_CRF(filename, samplerate):
    from collections.abc import MutableMapping, MutableSequence
    import madmom
    proc = madmom.features.beats.CRFBeatDetectionProcessor(fps=100)
    act = madmom.features.beats.RNNBeatProcessor()(filename)
    return proc(act)*samplerate

def beats_madmom_variable_DBN(filename, samplerate):
    from collections.abc import MutableMapping, MutableSequence
    import madmom
    proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=100)
    act = madmom.features.beats.RNNBeatProcessor()(filename)
    return proc(act)*samplerate

def beatswapworker(audio, beats, swap, smoothing):
    audio=(audio[0],audio[1])
    #print(len(audio))
    mode,n,audio2,sel,size,cutx='beat',0,([0],[0]),'',0,0
    # ready up!
    for i in swap:
        n+=1
        if i==',' and mode=='' or mode=='ignore': 
            mode='beat'
            sel=''
            continue
        if i=='*': mode='ignore'
        if i=='(' and mode != 'ignore': mode='cut'
        if i==')' and mode=='cut': mode=''
        if mode=='' or mode=='cut' or mode=='ignore': 
            continue
        if i.isdigit(): sel=str(sel)+str(i)
        #print(i, n, sel, len(swap), i.isdigit(), sel.isdigit(), ((not i.isdigit()) or len(swap)==n) and sel.isdigit(), sep=',    ')
        if ((not i.isdigit()) or len(swap)==n) and sel.isdigit() and mode=='beat' and i!='*': 
            size=max(int(sel), size)
            sel=''
            mode=''
            if i==',': mode='beat'
    #process!
    if beats==[]: 
        beats=numpy.linspace(0, len(audio[0]), size+1, dtype=int)[0:-1]
        cutx=1
        #print(beats, len(audio[0]), size)
    mode='beat'
    #print(swap, smoothing)
    beats=numpy.append(beats, len(audio[0]))
    #print('audio length: ', len(audio[0]), '    swap length:', len(swap), '  beats length:', len(beats), '   beats in swap:', size, '    iterations:', max(int(round((len(beats)/size)-0.5)),1))
    if cutx==0: 
        #print('beats loaded', end='')
        iterations=max(int(round((len(beats)/size)-0.5)),1)
        #print('_'*(int((iterations)/max((iterations/50), 1))-1)+'|', end='\r')
    else: iterations=1
    for j in range(iterations):
        #print(j, int(iterations), int(iterations/50), max(int(iterations/50), 1), j%max(int(iterations/50), 1))
        #if cutx==0 and j%max(int(iterations/50), 1)==0: print('█', end='')
        n=0
        for i in swap:
            n+=1
            #print('j=', j, ',   n=', n, ',   i=',i,',   sel=', sel, ',     mode: ', mode, sep='')
            if i=='-' or i==' ': continue
            if (i.isdigit()) and mode=='beat': 
                #print('adding', str(sel), '+', str(i))
                sel=str(sel)+str(i)
                #print('obtained:', sel)
                #print(i, sel, sep=' | ')
            elif i=='-' and mode=='beat' or mode=='effect': mode='stop'
            elif i=='c' and mode=='beat' or mode=='effect': 
                cut=0
                mode='cut'
                sel=int(sel)-1+j*size
            elif mode=='cut' and i!=')':
                cut+=1
            elif mode=='cut' and i==')':
                #print('cutting: ', sel, ',  n =',n,'  cut =',cut,'  mask:', swap[n-cut:n-1])
                #print('before:',len(audio[0,int(beats[int(sel)]):int(beats[int(sel)+1])]))
                try:
                    cut=beatswapworker(numpy.asarray(audio)[:,int(beats[int(sel)]):int(beats[int(sel)+1])], [], swap[n-cut:n-1], smoothing).tolist()
                    for a in range(len(audio2)):
                        audio2[a].extend(numpy.linspace(audio2[a][-1], cut[a][0], smoothing))
                        audio2[a].extend(cut[a])
                    #audio2=numpy.hstack((audio2,numpy.vstack((numpy.linspace(audio2[0,-1:], cut[0,0], smoothing).T, numpy.linspace(audio2[1,-1:], cut[1,0], smoothing).T)),cut))
                    mode='stop'
                except IndexError: print('cut: out of bounds:', sel)
                #print('done cutting')
            if ((not i.isdigit()) or len(swap)==n) and sel!=0 and mode=='beat':
                sel=int(sel)-1+j*size
                #print('adding beat:', sel)
                try: 
                    for a in range(len(audio2)):
                        audio2[a].extend(numpy.linspace(audio2[a][-1], audio[a][int(beats[sel])], smoothing))
                        audio2[a].extend(audio[a][int(beats[sel]):int(beats[sel+1])])
                        #audio2=numpy.hstack((audio2, numpy.vstack((numpy.linspace(audio2[0,-1:], audio[0,int(beats[sel])], smoothing).T, numpy.linspace(audio2[1,-1:], audio[1,int(beats[sel])], smoothing).T)), audio[:,int(beats[sel]):int(beats[sel+1])]))
                except IndexError: print('add: out of bounds:', sel)
                mode='effect'
            if i=='r' and mode=='effect': 
                try:
                    #print('reversing:', sel, ', length =', len(audio[0,int(beats[sel]):int(beats[sel+1])]))
                    #print(len(audio[0,:]), len(audio2[0,:]), len(audio2[0,0:-len(audio[0,int(beats[sel]):int(beats[sel+1])])]))
                    for a in range(len(audio2)):
                        audio2[a].extend(numpy.linspace(audio2[a][-len(audio[a][int(beats[sel]):int(beats[sel+1])])],audio2[a][-1],smoothing))
                        audio2[a][-len(audio[a][int(beats[sel]):int(beats[sel+1])]):] = reversed(audio2[a][-len(audio[a][int(beats[sel]):int(beats[sel+1])]):])
                        #audio2=numpy.hstack((audio2[:,:-len(audio[0,int(beats[sel]):int(beats[sel+1])])],numpy.vstack((numpy.linspace(audio2[0,-len(audio[0,int(beats[sel]):int(beats[sel+1])])],audio2[0,-1],smoothing).T,numpy.linspace(audio2[1,-len(audio[0,int(beats[sel]):int(beats[sel+1])])],audio2[1,-1],smoothing).T)),audio2[:,-len(audio[0,int(beats[sel]):int(beats[sel+1])]):][:,::-1]))
                except FileExistsError: print('rev: out of bounds:', sel)
                #mode='effect'
            if i=='m' and mode=='effect':
                try: 
                    audio2=numpy.asarray(audio2)
                    audio2[:,-len(audio[0][int(beats[sel]):int(beats[sel+1])]):]*=0
                    audio2=audio2.tolist()
                    #audio2=numpy.hstack((audio2[:,:-len(audio[0,int(beats[sel]):int(beats[sel+1])])],audio2[:,-len(audio[0,int(beats[sel]):int(beats[sel+1])]):]*0))
                except IndexError: pass
            if i=='l' and mode=='effect':
                try: 
                    audio2=numpy.asarray(audio2)
                    audio2[:,-len(audio[0,int(beats[sel]):int(beats[sel+1])]):]*=10
                    audio2=audio2.tolist()
                    #audio2=numpy.hstack((audio2[:,:-len(audio[0,int(beats[sel]):int(beats[sel+1])])],audio2[:,-len(audio[0,int(beats[sel]):int(beats[sel+1])]):]*10))
                except IndexError: pass
            if (i==',' or len(swap)==n) and mode!='cut': 
                sel=0
                mode='beat'
    #print(len(audio2[0]))
    #print(numpy.asarray(audio2).shape)
    #if cutx==0: print( numpy.asarray(audio2))
    return numpy.asarray(audio2, dtype=float)

def beatswap(audio, beats, swap:str,  scale=1, shift=0, smoothing=50):
    #print(scale)
    if (beats[1] - beats[0])>=160000: scale/=8
    elif (beats[1] - beats[0])>=80000: scale/=4
    elif (beats[1] - beats[0])>=40000: scale/=2
    elif (beats[1] - beats[0])<=20000: scale*=2
    elif (beats[1] - beats[0])<=10000: scale*=4
    elif (beats[1] - beats[0])<=5000: scale*=8
    #print(scale)
    if scale!=1:
        import math
        a=0
        b=numpy.array([])
        while a <len( beats[:-math.ceil(scale)]):
            b=numpy.append(b, (1-(a%1))*beats[math.floor(a)]+(a%1)*beats[math.ceil(a)])
            a+=scale
        beats = b
    i=0
    #print(beats[0], beats[1])
    diff=(beats[1]-beats[0])
    while diff<beats[0]:
        beats=numpy.insert(beats, 0, beats[0]-diff)
        i+=1
    #print (beats[1] - beats[0])
    #print(beats[0], beats[1])
    if shift>0 and shift%1==0:
        for i in range(shift): beats=numpy.insert(beats, 0, i)
    elif shift!=0:
        for i in range(int(16-float(shift))): beats=numpy.insert(beats, 0, i)
    beats=beats[beats>=0]
    return(beatswapworker(numpy.around(audio, 3).astype(float), beats.astype(int), swap, smoothing))
