
import numpy as np
from . import main

def open_audio(path:str = None, lib:str = 'auto', normalize = True) -> tuple:
    """Opens audio from path, returns (audio, samplerate) tuple.
    
    Audio is returned as an array with normal volume range between -1, 1.
    
    Example of returned audio: 
    
    [
        [0.35, -0.25, ... -0.15, -0.15], 
    
        [0.31, -0.21, ... -0.11, -0.07]
    ]"""

    if path is None:
        from tkinter.filedialog import askopenfilename
        path = askopenfilename(title='select song', filetypes=[("mp3", ".mp3"),("wav", ".wav"),("flac", ".flac"),("ogg", ".ogg"),("wma", ".wma")])
    
    path=path.replace('\\', '/')

    if lib=='pedalboard.io':
        import pedalboard.io
        with pedalboard.io.AudioFile(path) as f:
            audio = f.read(f.frames)
            sr = f.samplerate
    
    elif lib=='librosa':
        import librosa
        audio, sr = librosa.load(path, sr=None, mono=False)
    
    elif lib=='soundfile':
        import soundfile
        audio, sr = soundfile.read(path)
        audio=audio.T
    
    elif lib=='madmom':
        import madmom
        audio, sr = madmom.io.audio.load_audio_file(path, dtype=float)
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
                audio,sr=open_audio(path, i)
                break
            except Exception as e:
                print(f'open_audio with {i}: {e}')
    
    if len(audio)>16: audio=np.array([audio, audio], copy=False)
    if normalize is True: 
        audio = np.clip(audio, -1, 1)
        audio = audio*(1/np.max(np.abs(audio)))
    return audio.astype(np.float32),sr
    
def _sr(sr):
    try: return int(sr)
    except (ValueError, TypeError): assert False, f"Audio is an array, but `sr` argument is not valid. If audio is an array, you have to provide samplerate as an integer in the `sr` argument. Currently sr = {sr} of type {type(sr)}"

def write_audio(audio:np.ndarray, sr:int, output:str, lib:str='auto', libs=('pedalboard.io', 'soundfile'), log = True):
        """"writes audio to path specified by output. Path should end with file extension, for example `folder/audio.mp3`"""
        if log is True: print(f'Writing {output}...', end=' ')
        assert _iterable(audio), f"audio should be an array/iterable object, but it is {type(audio)}"
        sr = _sr(sr)
        if not isinstance(audio, np.ndarray): audio = np.array(audio, copy=False)
        if lib=='pedalboard.io':
            #print(audio)
            import pedalboard.io
            with pedalboard.io.AudioFile(output, 'w', sr, audio.shape[0]) as f:
                f.write(audio)
        elif lib=='soundfile':
            audio=audio.T
            import soundfile
            soundfile.write(output, audio, sr)
            del audio
        elif lib=='auto':
            for i in libs:
                try: 
                    write_audio(audio=audio, sr=sr, output=output, lib=i, log = False)
                    break
                except Exception as e:
                    print(e)
            else: assert False, 'Failed to write audio, chances are there is something wrong with it...'
        if log is True: print(f'Done!')

def _iterable(a):
    try:
        _ = iter(a)
        return True
    except TypeError: return False

def _load(audio, sr:int = None, lib:str = 'auto', channels:int = 2, transpose3D:bool = False) -> tuple:
    """Automatically converts audio from path or any format to [[...],[...]] array. Returns (audio, samplerate) tuple."""
    # path
    if isinstance(audio, str): return(open_audio(path=audio, lib=lib))
    # array
    if _iterable(audio):
        if isinstance(audio, main.song):
            if sr is None: sr = audio.sr
            audio = audio.audio
        # sr is provided in a tuple
        if sr is None and len(audio) == 2:
            if not _iterable(audio[0]):
                sr = audio[0]
                audio = audio[1]
            elif not _iterable(audio[1]):
                sr = audio[1]
                audio = audio[0]
        if not isinstance(audio, np.ndarray): audio = np.array(audio, copy=False)
        sr = _sr(sr)
        if _iterable(audio[0]):
            # image
            if _iterable(audio[0][0]):
                audio2 = []
                if transpose3D is True: audio = audio.T
                for i in audio:
                    audio2.extend(_load(audio=i, sr=sr, lib=lib, channels=channels, transpose3D=transpose3D)[0])
                return audio2, sr
            # transposed
            if len(audio) > 16:
                audio = audio.T
                return _load(audio=audio, sr=sr, lib=lib, channels=channels, transpose3D=transpose3D)
            # multi channel
            elif isinstance(channels, int):
                if len(audio) >= channels:
                    return audio[:channels], sr
                # masked mono
                else: return np.array([audio[0] for _ in range(channels)], copy=False), sr
            else: return audio, sr
        else: 
            # mono
            return (np.array([audio for _ in range(channels)], copy=False) if channels is not None else audio), sr
    # unknown
    else: assert False, f"Audio should be either a string with path, an array/iterable object, or a song object, but it is {type(audio)}"

def _tosong(audio, sr=None):
    if isinstance(audio, main.song): return audio
    else: 
        audio, sr = _load(audio = audio, sr = sr)
        return main.song(audio=audio, sr = sr)

def _outputfilename(path:str = None, filename:str = None, suffix:str = None, ext:str = None):
    """If path has file extension, returns `path + suffix + ext`. Else returns `path + filename + suffix + .ext`. If nothing is specified, returns `output.mp3`"""
    if ext is not None:
        if not ext.startswith('.'): ext = '.'+ext
    if path is None: path = 'output'
    if path.endswith('/') or path.endswith('\\'): path=path[:-1]
    if '.' in path:
        path = path.split('.')
        if path[-1].lower() in ['mp3', 'wav', 'flac', 'ogg', 'wma', 'aac', 'ac3', 'aiff']:
            if ext is not None:
                path[-1] = ext
            if suffix is not None: path[len(path)-2]+=suffix
            return ''.join(path)
        else: path = ''.join(path)
    if filename is not None:
        filename = filename.replace('\\','/').split('/')[-1]
        if '.' in filename:
            filename = filename.split('.')
            if filename[-1].lower() in ['mp3', 'wav', 'flac', 'ogg', 'wma', 'aac', 'ac3', 'aiff']:
                if ext is not None:
                    filename[-1] = ext
                if suffix is not None: filename.insert(len(filename)-1, suffix)
            else: filename += [ext]
            filename = ''.join(filename)
            return f'{path}/{filename}' if path != '' else filename
        return f'{(path + "/") * (path != "")}{filename}{suffix if suffix is not None else ""}.{ext if ext is not None else "mp3"}'
    else: return f'{path}/output.mp3'
