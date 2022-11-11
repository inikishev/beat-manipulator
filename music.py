import BigOuncesAudioEffects as ba
from tkinter.filedialog import askopenfilename
filename = askopenfilename(title='select beat saber map .zip', filetypes=[
                    ("beat saber map", ".mp3"),
                ])
#Open a file
(audio, samplerate)=ba.r_pedalboard(filename)
print(samplerate)
#apply effects
(kaudio, ksamplerate)=ba.r_pedalboard('kick.wav')
(saudio, ssamplerate)=ba.r_pedalboard('clap.wav')
(haudio, hsamplerate)=ba.r_pedalboard('hh.wav')

#analyze beats
#beats = ba.beats_librosa_constant(audio, samplerate, 10)
beats = ba.beats_madmom_constant(filename, samplerate)
audio=ba.b_each(audio, haudio, beats, scale=1/15, shift=0)
audio=ba.b_each(audio, kaudio, beats, scale=2, shift=0)
audio=ba.b_each(audio, saudio, beats, scale=4, shift=2)

#print(beats)
#print(len(beats))
#audio=ba.a_cut(audio, samplerate, 438354/44100, 511413/44100)
#write it back
ba.w_pedalboard(audio, samplerate, output='pedalboard_output.mp3')
#ba.w_cv2image(audio, output='cv2_output.png', max=1000000)