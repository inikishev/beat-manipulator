import BeatManipulator as bm
import bm_wrapper as bmw
audio=list(i/100 for i in range(-100,100,1))
beatmap=list(range(0,100,10))+list(range(100,201,20))

def printb(text):
    print(f'\033[1m{text}\033[0m')
def printe(text):
    print(f'\x1b[0;31;40m{text}\x1b[0m')

# audio:
# [-1.0, -0.99, -0.98, -0.97, -0.96, -0.95, -0.94, -0.93, -0.92, -0.91, -0.9, -0.89, -0.88, -0.87, -0.86, -0.85, -0.84, -0.83, -0.82, -0.81, -0.8, -0.79, -0.78, -0.77, -0.76, -0.75, -0.74, -0.73, -0.72, -0.71, -0.7, -0.69, -0.68, -0.67, -0.66, -0.65, -0.64, -0.63, -0.62, -0.61, -0.6, -0.59, -0.58, -0.57, -0.56, -0.55, -0.54, -0.53, -0.52, -0.51, -0.5, -0.49, -0.48, -0.47, -0.46, -0.45, -0.44, -0.43, -0.42, -0.41, -0.4, -0.39, -0.38, -0.37, -0.36, -0.35, -0.34, -0.33, -0.32, -0.31, -0.3, -0.29, -0.28, -0.27, -0.26, -0.25, -0.24, -0.23, -0.22, -0.21, -0.2, -0.19, -0.18, -0.17, -0.16, -0.15, -0.14, -0.13, -0.12, -0.11, -0.1, -0.09, -0.08, -0.07, -0.06, -0.05, -0.04, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.4, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.5, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.6, 0.61, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68, 0.69, 0.7, 0.71, 0.72, 0.73, 0.74, 0.75, 0.76, 0.77, 0.78, 0.79, 0.8, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99] 
# audio at beatmap:
# [-1.0, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

test=bm.song(audio=audio, samplerate=2, beatmap=beatmap, filename='test.mp3', log=False)
if list(test.beatmap) == beatmap: printb('beatmap assignment passed')
else: printe(f'''beatmap assignment error.
{beatmap}
{test.beatmap}''')

test.beatmap_shift(2)
if list(test.beatmap) == beatmap[2:]: printb('beatmap_shift(2) passed')
else: printe(f'''beatmap_shift(2) error, 1st line is the expected result:
{[0, 1, 2] + beatmap[1:]}
{test.beatmap}''')

test.beatmap = beatmap.copy()
test.beatmap_shift(-2)
if list(test.beatmap) == list([0, 1, 2] + beatmap[1:]): printb ('beatmap_shift(-2) passed')
else:printe(f'''beatmap_shift(-2) error, 1st line is the expected result:
{beatmap[2:]}
{test.beatmap}''')

test.beatmap = beatmap.copy()
should=[5, 15, 25, 35, 45, 55, 65, 75, 85, 95, 110, 130, 150, 170, 190, 200]
test.beatmap_shift(0.5)
if list(test.beatmap) == should: printb('beatmap_shift(0.5) passed')
else:printe(f'''beatmap_shift(0.5) error, 1st line is the expected result:
{should}
{test.beatmap}''')

test.beatmap = beatmap.copy()
should=[0, 5, 15, 25, 35, 45, 55, 65, 75, 85, 95, 110, 130, 150, 170, 190]
test.beatmap_shift(-0.5)
if list(test.beatmap) == should: printb('beatmap_shift(-0.5) passed')
else:printe(f'''beatmap_shift(-0.5) error, 1st line is the expected result:
{should}
{test.beatmap}''')

test.beatmap = beatmap.copy()
should=[25, 35, 45, 55, 65, 75, 85, 95, 110, 130, 150, 170, 190, 200]
test.beatmap_shift(2.5)
if list(test.beatmap) == should: printb('beatmap_shift(2.5) passed')
else:printe(f'''beatmap_shift(2.5) error, 1st line is the expected result:
{should}
{list(test.beatmap)}''')

test.beatmap = beatmap.copy()
should=[1, 2, 3, 5, 15, 25, 35, 45, 55, 65, 75, 85, 95, 110, 130, 150, 170, 190]
test.beatmap_shift(-2.5)
if list(test.beatmap) == should: printb('beatmap_shift(-2.5) passed')
else:printe(f'''beatmap_shift(-2.5) error, 1st line is the expected result:
{should}
{list(test.beatmap)}''')

test.beatmap = beatmap.copy()
should=[0, 20, 40, 60, 80, 100, 140, 180]
test.beatmap_scale(2)
if list(test.beatmap) == should: printb('beatmap_scale(2) passed')
else:printe(f'''beatmap_scale(2) error, 1st line is the expected result:
{should}
{list(test.beatmap)}''')

test.beatmap = beatmap.copy()
should=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190]
test.beatmap_scale(0.5)
if list(test.beatmap) == should: printb('beatmap_scale(2) passed')
else:printe(f'''beatmap_scale(2) error, 1st line is the expected result:
{should}
{list(test.beatmap)}''')

test.beatmap = beatmap.copy()
test.beatswap("1, 3, 2, 4", smoothing=0)
should=[[-1.0, -0.99, -0.98, -0.97, -0.96, -0.95, -0.94, -0.93, -0.92, -0.91, -0.8, -0.79, -0.78, -0.77, -0.76, -0.75, -0.74, -0.73, -0.72, -0.71, -0.9, -0.89, -0.88, -0.87, -0.86, -0.85, -0.84, -0.83, -0.82, -0.81, -0.7, -0.69, -0.68, -0.67, -0.66, -0.65, -0.64, -0.63, -0.62, -0.61, -0.6, -0.59, -0.58, -0.57, -0.56, -0.55, -0.54, -0.53, -0.52, -0.51, -0.4, -0.39, -0.38, -0.37, -0.36, -0.35, -0.34, -0.33, -0.32, -0.31, -0.5, -0.49, -0.48, -0.47, -0.46, -0.45, -0.44, -0.43, -0.42, -0.41, -0.3, -0.29, -0.28, -0.27, -0.26, -0.25, -0.24, -0.23, -0.22, -0.21, -0.2, -0.19, -0.18, -0.17, -0.16, -0.15, -0.14, -0.13, -0.12, -0.11, 0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, -0.1, -0.09, -0.08, -0.07, -0.06, -0.05, -0.04, -0.03, -0.02, -0.01, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.4, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.5, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.8, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 0.6, 0.61, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68, 0.69, 0.7, 0.71, 0.72, 0.73, 0.74, 0.75, 0.76, 0.77, 0.78, 0.79], [-1.0, -0.99, -0.98, -0.97, -0.96, -0.95, -0.94, -0.93, -0.92, -0.91, -0.8, -0.79, -0.78, -0.77, -0.76, -0.75, -0.74, -0.73, -0.72, -0.71, -0.9, -0.89, -0.88, -0.87, -0.86, -0.85, -0.84, -0.83, -0.82, -0.81, -0.7, -0.69, -0.68, -0.67, -0.66, -0.65, -0.64, -0.63, -0.62, -0.61, -0.6, -0.59, -0.58, -0.57, -0.56, -0.55, -0.54, -0.53, -0.52, -0.51, -0.4, -0.39, -0.38, -0.37, -0.36, -0.35, -0.34, -0.33, -0.32, -0.31, -0.5, -0.49, -0.48, -0.47, -0.46, -0.45, -0.44, -0.43, -0.42, -0.41, -0.3, -0.29, -0.28, -0.27, -0.26, -0.25, -0.24, -0.23, -0.22, -0.21, -0.2, -0.19, -0.18, -0.17, -0.16, -0.15, -0.14, -0.13, -0.12, -0.11, 0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, -0.1, -0.09, -0.08, -0.07, -0.06, -0.05, -0.04, -0.03, -0.02, -0.01, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.4, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.5, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.8, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99, 0.6, 0.61, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68, 0.69, 0.7, 0.71, 0.72, 0.73, 0.74, 0.75, 0.76, 0.77, 0.78, 0.79]]
if list(test.audio) == should: printb('beatswap("1, 3, 2, 4") passed')
else:printe(f'''beatswap("1, 3, 2, 4") error, 1st line is the expected result:
{should}
{list(test.audio)}''')

# [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200]

def import_test():
    audio2=list(i/100000 for i in range(-100000,100000,1))
    beatmap2=list(range(0,100000,10))+list(range(100,200001,20))
    test2=bm.song(audio=audio2, samplerate=2, beatmap=beatmap2, filename='test2.mp3', log=False)

def shift_test(number, shift):
    audio2=list(i/number for i in range(-number,number,1))
    beatmap2=list(range(0,number,10))+list(range(100,number*2+1,20))
    test2=bm.song(audio=audio2, samplerate=2, beatmap=beatmap2, filename='test2.mp3', log=False)
    test2.beatmap_shift(shift)

def scale_test(number, scale):
    audio2=list(i/number for i in range(-number,number,1))
    beatmap2=list(range(0,number,10))+list(range(100,number*2+1,20))
    test2=bm.song(audio=audio2, samplerate=2, beatmap=beatmap2, filename='test2.mp3',log=False)
    test2.beatmap_scale(0.5)

def beatswap_test(number, pattern):
    audio2=list((i/number)*100 for i in range(-number,number,1))
    beatmap2=list(range(0,number*100,1000))+list(range(10000,number*200+1,2000))
    test2=bm.song(audio=audio2, samplerate=2, beatmap=beatmap2, filename='test2.mp3',log=False)
    test2.beatswap(pattern)

input('run time tests?')
import timeit
printb(f'beatmap_shift(-2.5) for 1000 beats takes {timeit.timeit(lambda: shift_test(1000,shift=-2.5), number=1)}') #0.0028216999489814043
printb(f'beatmap_shift(-2.5) for 20000 beats takes {timeit.timeit(lambda: shift_test(20000,shift=-2.5), number=1)}') #0.6304191001690924
printb(f'beatmap_scale(0.5) for 20000 beats takes {timeit.timeit(lambda: scale_test(20000,scale=0.5), number=1)}') #0.10623739985749125
printb(f'test2.beatswap("1,3,2,4") for 20000 beats takes {timeit.timeit(lambda: beatswap_test(20000,pattern="1,3,2,4"), number=1)}') #0.406920799985528
printb(f'test2.beatswap("1v2, 0:0.5b5, 1:1.5r, 3c, 4:3") for 20000 beats takes {timeit.timeit(lambda: beatswap_test(20000,pattern="1v2, 0:0.5b5, 1:1.5r, 3c, 4:3"), number=1)}') #0.5667359000071883