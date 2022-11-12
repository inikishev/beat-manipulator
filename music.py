import BigOuncesAudioEffects as ba
from tkinter.filedialog import askopenfilename
filename = askopenfilename(title='select beat saber map .zip', filetypes=[
                    ("beat saber map", ".mp3"),
                ])
#Open a file
(audio, samplerate)=ba.r_pedalboard(filename)
#print(samplerate)
#apply effects
(kaudio, ksamplerate)=ba.r_pedalboard('kick.wav')
(saudio, ssamplerate)=ba.r_pedalboard('clap.wav')
(haudio, hsamplerate)=ba.r_pedalboard('hh.wav')

#analyze beats
#beats = ba.beats_librosa_constant(audio, samplerate, 10)
beats = ba.beats_madmom_constant(filename, samplerate)
#import numpy
# beats=numpy.array([   2205,   23373,   44982,   66150,   88641,  110691,  130977,  152145,
#   172872,  195363,  216090,  236817,  259308,  280035,  300762,  322371,
#   343539,  366030,  388080,  408807,  430857,  452466,  474075,  495243,
#   515529,  537579,  559188,  579474,  601524,  623133,  644301,  665469,
#   685314,  707364,  728973,  749259,  771309,  792918,  813645,  834372,
#   855540,  878031,  899640,  919926,  941976,  963144,  983430, 1004598,
#  1025766, 1048257, 1069866, 1090593, 1112643, 1134252, 1154538, 1175706,
#  1196874, 1219365, 1240974, 1261260, 1283751, 1304919, 1325205, 1346373,
#  1368423,])
#audio=ba.b_each(audio, kaudio, be5ats, scale=1/4, shift=0, include=range(11,20))
#audio=ba.b_each(audio, saudio, beats, scale=1/4, shift=2, exclude=[30,31,32,33])
#print(audio)
audio = ba.beatswap(audio, beats, '1,2,3,5, 6,7,9,10, 11,13,14,15, 4,8,12,16', scale=1, smoothing=50)
#print(audio)
#print(beats)
#print(len(beats))
#audio=ba.a_cut(audio, samplerate, 438354/44100, 511413/44100)
#write it back
print(filename)
ba.w_pedalboard(audio, samplerate, output=''.join(filename.split('/')[-1]))
#ba.w_cv2image(audio, output='cv2_output.png', max=1000000)