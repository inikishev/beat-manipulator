# command line
# alright so basically
# py -m beatman -i "path/to/input" -o "path to output" -p "pattern"
# takes song from input path, beatswaps with the pattern, and writes to output
# if output not specified, it just goes to output folder
# if input is not specified it opens a file selector
# just "py -m beatman" will bring up a file selector and ask for pattern
import beat_manipulator as bm, sys
#args=['whatevr', '-i', r'F:\Stuff\Music\Tracks\e-veryday - e-verynight.mp3', '--pattern', '1,3,2,4']
args=[i.replace('--', '-') if i.startswith('-') else i for i in sys.argv]
def arg(a, args:list=args):
    if a in args and len(args)>args.index(a):return args[args.index(a)+1]

#input
inp = arg('-i')
if inp is None: inp = arg('-in')
if inp is None: inp = arg('-input')
if inp is None:
    from tkinter import filedialog
    inp=filedialog.askopenfilename(title='Open a song for beatswapping')

#output
output= arg('-o')
if output is None: output = arg('-out')
if output is None: output = arg('-output')
if output is None: output = 'output'
#pattern
pattern= arg('-p')
if pattern is None: pattern = arg('-pat')
if pattern is None: pattern = arg('-pattern')
if pattern is None: pattern = input('Write the beatswapping pattern: ')

scale= arg('-s')
if scale is None: scale = arg('-sc')
if scale is None: scale = arg('-scale')
if scale is None: scale = 1
shift= arg('-h')
if shift is None: shift = arg('-shift')
if shift is None: shift = 0

bm.beatswap(audio=inp, output=output, pattern=pattern, scale = scale, shift = shift)
