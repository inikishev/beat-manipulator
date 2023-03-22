from . import io, main
import numpy as np
def generate(song, beatmap = None, mode='median', sr = None, log = True):
    if log is True: print(f'Generating an image from beats...', end = ' ')
    song = main.song(song, sr=sr)
    if song.beatmap is None: song.beatmap = beatmap
    if song.beatmap is None: song.beatmap_generate()
    if isinstance(song.audio, np.ndarray): song.audio = song.audio.tolist()
    # create the image
    image = [[],[]]
    for i in range(1, len(song.beatmap)):
        beat = song[i]
        image[0].append(beat[0])
        image[1].append(beat[1])

    # find image width
    lengths = [len(i) for i in image[0]]
    mode = mode.lower()
    if 'max' in mode:
        width = max(lengths)
    elif 'med' in mode:
        width = int(np.median(lengths))
    elif 'av' in mode:
        width = int(np.average(lengths))

    # fill or crop rows:
    for i in range(len(image[0])):
        difference = lengths[i] - width
        if difference<0:
            image[0][i].extend([np.nan]*(-difference))
            image[1][i].extend([np.nan]*(-difference))
        elif difference>0:
            image[0][i] = image[0][i][:-difference]
            image[1][i] = image[1][i][:-difference]

    song.audio = np.array(song.audio, copy=False)
    if log is True: print('Done!')
    return np.array(image, copy=False)

def bw_to_colored(image, channel = 2, fill = True):
    if fill is True:
        combined = image[0] * image[1]
        combined = (np.abs(combined)**0.5)*np.sign(combined)
    else: channel = np.zeros(shape = image[0].shape)
    image = image.tolist()
    if channel == 2: image.append(combined)
    else: image.insert(channel, combined)
    return np.rot90(np.array(image, copy=False).T)

def colored_to_bw(image, l=0, r=1):
    image = np.array(image, copy=False)
    return np.array([image[:,:,l],image[:,:,r]])

def write(image, output, mode = 'r', max_size = 4096, rotate = True, contrast=1):
    import cv2
    if max_size is not None:
        w = max_size
        h = min(len(image[0][0]), max_size)
    if mode == 'color':
        image = bw_to_colored(image)
    elif mode == 'r':
        image = image[0]
    elif mode == 'l':
        image = image[1]
    elif mode == 'combine':
        image = image[0] + image[1]
    image = image*(255*contrast)
    image = cv2.resize(src=image, dsize=(w, h), interpolation = cv2.INTER_NEAREST)
    if rotate is True: image = np.rot90(image)
    cv2.imwrite(output, image)
