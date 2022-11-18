import BeatManipulator as bm

# dnb 1=khshkhsh, or khsh
# rest - khsh

dotted05='0:3, 4:4.5,7, 4:4.5,11, 4:4.5,7, 4:4.5,11, 8:8.5,7, 8:8.5,11, 8:8.5,7, 8:8.5,11, 16' #0.125 - 0.5

bm.wrapper_beatswap(filename=None, pattern=dotted05, scale=0.125, shift=0, start=0, end=None)