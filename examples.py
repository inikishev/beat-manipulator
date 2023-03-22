import beat_manipulator as bm, os, random

path = 'F:/Stuff/Music/Tracks/'
song = 'Flawed Mangoes - parasite.mp3'
song = path + song

# bm.presets.savetest(song, scale = 1, shift = 0)

#bm.beatswap(song, 'test', scale = 1, shift = 0)

bm.presets.use(song = song, preset = '3 bars mix')