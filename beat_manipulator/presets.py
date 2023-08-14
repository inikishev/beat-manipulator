from . import main, utils
BM_SAMPLES = {'cowbell' : 'beat_manipulator/samples/cowbell.flac',
              }

presets = {}

def presets_load(path, mode = 'add'):
    global presets
    import yaml
    with open(path, 'r') as f:
        yaml_presets = yaml.safe_load(f.read())
    
    # if mode.lower() == 'add':
    #     presets = presets | yaml_presets
    # elif mode.lower() == 'replace':
        presets = yaml_presets

presets_load('beat_manipulator/presets.yaml')

def _beatswap(song, pattern, pattern_name, scale = 1, shift = 0, output = '', modify = False):
    if isinstance(scale, str):
        if ',' in scale: scale = scale.replace(' ', '').split(',')
    elif not isinstance(scale, list): scale = [scale]
    if modify is False:
        for i in scale:
            main.beatswap(song, pattern = pattern, scale = i, shift = shift, output=output, suffix = f' ({pattern_name}{(" x"+str(round(utils._safer_eval(i), 4))) * (len(scale)>1)})', copy = True)
    else:
        assert isinstance(song, main.song), f"In order to modify a song, it needs to be of a main.song type, but it is {type(song)}"
        song.beatswap(pattern, scale = scale[0], shift = shift)
        return song

def get(preset):
    """returns (pattern, scale, shift)"""
    global presets
    assert preset in presets, f"{preset} not found in presets."
    preset = presets[preset]
    return preset['pattern'], preset['scale'] if 'scale' in preset else 1, preset['shift'] if 'shift' in preset else 0

def use(song, preset, output = '', scale = 1, shift = 0):
    global presets
    assert preset in presets, f"{preset} not found in presets."
    preset_name = preset
    preset = presets[preset]
    if not isinstance(song, main.song): song = main.song(song)
    if isinstance(list(preset.values())[0], dict):
        for i in preset.values():
            if 'sample' in i:
                pass
            elif 'sidechain' in i:
                pass
            else:
                song = _beatswap(song, pattern = i['pattern'], scale = scale*(i['scale'] if 'scale' in i else 1), shift = shift*(i['shift'] if 'shift' in i else 0), output = output, modify = True, pattern_name = preset_name)
        song.write(output, suffix = f' ({preset})')
    else:
        if 'sample' in preset:
            pass
        elif 'sidechain' in preset:
            pass
        else:
            _beatswap(song, pattern = preset['pattern'], scale = scale*(preset['scale'] if 'scale' in preset else 1), shift = shift*(preset['shift'] if 'shift' in preset else 0), output = output, modify = False, pattern_name = preset_name)

def use_all(song, output = ''):
    if not isinstance(song, main.song): song = main.song(song)
    for key in presets.keys():
        print(f'__ {key} __')
        use(song, key, output = output)
        print()

def test(song, scale = 1, shift = 0, adjust = 0, output = '', load_settings = False):
    song = main.song(song)
    song.beatmap_generate(load_settings = load_settings)
    song.beatswap('test', scale = scale, shift = shift, adjust = 500+adjust)
    song.write(output = output, suffix = ' (test)')

def save(song, scale = 1, shift = 0, adjust = 0):
    song = main.song(song)
    song.beatmap_save_settings(scale = scale, shift = shift, adjust = adjust)

def savetest(song, scale = 1, shift = 0, adjust = 0, output = '', load_settings = False):
    song = main.song(song)
    song.beatmap_generate(load_settings = load_settings)
    song.beatswap('test', scale = scale, shift = shift, adjust = 500+adjust)
    song.write(output = output, suffix = ' (test)')
    song.beatmap_save_settings(scale = scale, shift = shift, adjust = adjust)