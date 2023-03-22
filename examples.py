import beat_manipulator as bm, os, random

path = 'F:/Stuff/Music/Tracks/'
song = 'Flawed Mangoes - parasite.mp3'
song = path + song

# bm.presets.savetest(song, scale = 2, shift = 0)

bm.beatswap(song, '1,3,2,4', scale = 0.001, shift = 0)

# bm.presets.use(song = song, preset = 'Rhythm Era')
