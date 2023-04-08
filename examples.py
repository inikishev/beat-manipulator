import beat_manipulator as bm, os, random

path = 'F:/Stuff/Music/Tracks/'
song = 'Phonetick - You.mp3'
song = path + song

#bm.presets.savetest(song, scale = 1, shift = 0)

bm.beatswap(song, 'random', scale = 1, shift = 0)

#bm.presets.use(song = song, preset = 'dotted snares fast 1', scale = 1)