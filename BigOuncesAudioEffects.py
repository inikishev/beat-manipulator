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

def beats_madmom0(filename, interval=64):
    from collections.abc import MutableMapping, MutableSequence
    import madmom
    proc = madmom.features.beats.RNNBeatProcessor()
    return madmom.features.beats.detect_beats(proc(filename), interval)

def beats_madmom_variable(filename, samplerate):
    from collections.abc import MutableMapping, MutableSequence
    import madmom
    proc = madmom.features.beats.BeatTrackingProcessor(fps=100)
    act = madmom.features.beats.RNNBeatProcessor()(filename)
    return proc(act)*samplerate

def beats_madmom_constant(filename, samplerate):
    from collections.abc import MutableMapping, MutableSequence
    import madmom
    proc = madmom.features.beats.BeatDetectionProcessor(fps=100)
    act = madmom.features.beats.RNNBeatProcessor()(filename)
    return proc(act)*samplerate

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