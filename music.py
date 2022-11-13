import BigOuncesAudioEffects as ba
from tkinter.filedialog import askopenfilename
import numpy
filename = askopenfilename(title='select beat saber map .zip', filetypes=[("beat saber map", ".mp3"),])
#filename = 'F:/Stuff/Music/Tracks/Misanthrop - Triumph.mp3'
(audio, samplerate)=ba.r_pedalboard(filename)

(kaudio, ksamplerate)=ba.r_pedalboard('kick.wav')
#(saudio, ssamplerate)=ba.r_pedalboard('clap.wav')
#(haudio, hsamplerate)=ba.r_pedalboard('hh.wav')

beats = ba.beats_madmom_constant(filename, samplerate)

#audio*=0.1
#audio=ba.b_each(audio, haudio, beats, shift=0.5, scale=2)
#audio=ba.b_each(audio, saudio, beats, shift=1, scale=2)
#audio=ba.b_each(audio, haudio/8, beats, shift=1.5, scale=2)

#audio=ba.beatswap(audio,beats,shift=1, swap='1c(1l,2m,3,4),2,3,4', scale=1)


#dotted = '1,2,3, 5,6,7, 9,10,11, 5,6,7, 13,14,15,16' #0.5
dotted= '1,2c(1,2-),3,4c(1,2-),5,6c(1,2-),3,4c(1,2-),7,8' #1
dotted05='1,2,3, 5c(1,2-),7, 5c(1,2-),11, 5c(1,2-),7, 5c(1,2-),11, 9c(1,2-),7, 9c(1,2-),11, 9c(1,2-),7, 9c(1,2-),11, 16' #0.5
t47 = '1, 2, 3, 4c(1,2-)' #1
t411 = '1, 2, 3, 1, 2, 5, 7, 4, 6, 7, 8' #1
faster2='1c(1,2-)'
faster3='1c(1,2,3-)'
faster4='1c(1,2,3,4-)'
slower1='1c(1,2,2)'

print (beats[1] - beats[0])

audio2 = ba.beatswap(audio, beats, shift=0, scale=0.5, swap=dotted)
print(' exporting', ''.join(filename.split('/')[-1]))
ba.w_pedalboard(audio2, samplerate, output=''.join(filename.split('/')[-1]))

#test
def test():
    audio=ba.beatswap(audio,beats,shift=0, swap='1c(1l,2m),2,3,4,5m,6,7,8', scale=0.5)
    print('exporting test')
    ba.w_pedalboard(audio, samplerate, output='test.mp3')
#test()