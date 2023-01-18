import numpy

def import_BeatSaber(dat_info, dat_difficulty, threshold=0.3, declumping=50) ->str: 
    import json
    #with open(dat_info, "r") as f:
    bs_info=json.loads(dat_info)
    #with open(dat_info, "r") as f:
    bs_map=json.loads(dat_difficulty)
    hitmap=[]
    bpm=bs_info["_beatsPerMinute"]
    artist=bs_info["_songAuthorName"]
    title=bs_info["_songName"]
    songfilename=bs_info['_songFilename']
    if songfilename.lower().endswith('.egg'): songfilename=songfilename.replace('.egg', '.ogg')
    #print(bpm)
    offset_sec=bs_info["_songTimeOffset"]
    try:
        for i in bs_map["_notes"]:
            for j in i.items():
                if j[0] == "_time": hitmap.append([[float((float(j[1])*8)*1000*(float(60 / float(bpm) / 8)))],[0]])
    except AttributeError: pass
    bs_map.pop("_notes")
    #print(bs_map)
    for k in bs_map.values():
        try:
            #print(k)
            for i in k:
                #print(i)
                for j in i.items():
                    #print(j)
                    if j[0] =="_time": hitmap.append([[float((float(j[1])*8)*1000*(float(60 / float(bpm) / 8)))],[0]])
        except AttributeError: pass

    # for i in range(len(hitmap)):
    #     if hitmap[i][1][0]==1:
    #         print (hitmap[i][0][0], i)
    hitmap=sorted(hitmap, key=lambda row: row[0])
    hitmap=numpy.asarray(hitmap)

    times=hitmap[:,0]
    #print(len(hitmap), len(times))
    clump=[]
    for i in range(len(times)-1):
        #print(i, abs(self.hitmap[i]-self.hitmap[i+1]), clump)
        if abs(times[i] - times[i+1]) < declumping: clump.append(i)
        elif clump!=[]:
            clump.append(i)
            actual_time=times[clump[0]]
            times[numpy.array(clump)]=0
            #print(self.hitmap)
            times[clump[0]]=actual_time
            clump=[]
    hitmap[:,0]=times
    hitmap=sorted(hitmap, key=lambda row: row[0])
    hitmap=numpy.asarray(hitmap)
    # for i in range(len(hitmap)):
    #      if hitmap[i,1]==1: 
    #          print ('n', hitmap[i,0], i)
    #print('sadasdsadsadsad')
    #print(hitmap)
    #print(hitmap)
    #print(hitmap)
    # for i in range(len(hitmap)):
    #     if hitmap[i,1]==1: 
    #         print (hitmap[i,0], i)
    n=0
    #input()
    #print(hitmap)
    for i in hitmap:
        if i[0]==0: n+=1
    hitmap=hitmap[n:]
    slider = False
    double=False
    was_double=0
    prev_dist=100
    prev_x=0
    prev_y=0
    file=''
    import random
    for i in range(len(hitmap)-1): 
        #if i== 0: continue
        #print(i)
        difficulty = threshold
        dist=(hitmap[i,0]-hitmap[i-1,0])*(1-(difficulty**0.3))
        #print(dist)
        if dist ==0: continue
        if dist<10: dist=0.00
        elif dist<20: dist=0.0
        elif dist<30: dist=0.01
        elif dist<40: dist=0.05
        elif dist<60: dist=0.3
        elif dist<80: dist=0.6
        elif dist<100: dist=0.75
        elif dist<150: dist=0.9
        elif dist<200: dist=1
        if prev_dist==dist: is_reverse = 1
        else: is_reverse=0
        prev_dist=dist
        if slider is True and dist<0.2: 
            dist = 0.25
        if prev_x>0: prev_x=prev_x-dist*0.1
        elif prev_x<0: prev_x=prev_x+dist*0.1
        if prev_y>0: prev_y=prev_y-dist*0.1
        elif prev_y<0: prev_y=prev_y+dist*0.1
        dirx=random.uniform(-dist,dist)
        diry=dist-abs(dirx)*random.choice([-1, 1])
        if abs(prev_x+dirx)>1: dirx=-dirx
        if abs(prev_y+diry)>1: diry=-diry
        x=prev_x+dirx
        y=prev_y+diry
        #print(dirx,diry,x,y)
        #print(x>1, x<1, y>1, y<1)
        if x>1: x=0.8
        if x<-1: x=-0.8
        if y>1: y=0.8
        if y<-1: y=-0.8
        prev_x=x
        prev_y=y
        #print(dirx,diry,x,y)
        
        if hitmap[i][1]==0 and slider is False:    
            file+=f'{int((x+1)*300)},{int((y+1)*180)},{int(hitmap[i,0])},1,0\n'
        elif slider is False:
            slider=True
            file+=f"{int((x+1)*300)},{int((y+1)*180)},{int(hitmap[i,0])},2,0,{random.choice(['B','C','L','P'])}|"
        elif double is True:
            double=False
            was_double=1
            file+=f'{int((x+1)*300)}:{int((y+1)*180)}|'
        else: 
            file+=f'{int((x+1)*300)}:{int((y+1)*180)},{was_double*is_reverse},{35*1+was_double+is_reverse}\n'
            was_double=0
            slider=False
            double=True
    return file,artist,title,songfilename



osufile=lambda title,artist,version,filename: ("osu file format v14\n"
        "\n"
        "[General]\n"
        f"AudioFilename: {filename}\n"
        "AudioLeadIn: 0\n"
        "PreviewTime: -1\n"
        "Countdown: 0\n"
        "SampleSet: Normal\n"
        "StackLeniency: 0.5\n"
        "Mode: 0\n"
        "LetterboxInBreaks: 0\n"
        "WidescreenStoryboard: 0\n"
        "\n"
        "[Editor]\n"
        "DistanceSpacing: 1.1\n"
        "BeatDivisor: 4\n"
        "GridSize: 8\n"
        "TimelineZoom: 1.6\n"
        "\n"
        "[Metadata]\n"
        f"Title:{title}\n"
        f"TitleUnicode:{title}\n"
        f"Artist:{artist}\n"
        f"ArtistUnicode:{artist}\n"
        f'Creator:Saber2Osu\n'
        f'Version:{version}\n'
        'Source:\n'
        'Tags:BeatManipulator\n'
        'BeatmapID:0\n'
        'BeatmapSetID:-1\n'
        '\n'
        '[Difficulty]\n'
        'HPDrainRate:4\n'
        'CircleSize:4\n'
        'OverallDifficulty:5\n'
        'ApproachRate:10\n'
        'SliderMultiplier:3.3\n'
        'SliderTickRate:1\n'
        '\n'
        '[Events]\n'
        '//Background and Video events\n'
        '//Break Periods\n'
        '//Storyboard Layer 0 (Background)\n'
        '//Storyboard Layer 1 (Fail)\n'
        '//Storyboard Layer 2 (Pass)\n'
        '//Storyboard Layer 3 (Foreground)\n'
        '//Storyboard Layer 4 (Overlay)\n'
        '//Storyboard Sound Samples\n'
        '\n'
        '[TimingPoints]\n'
        '0,120.0,4,1,0,100,1,0\n'
        '\n'
        '\n'
        '[HitObjects]\n')


class osu_map:
    def __init__(self, filename:str=None, audio:numpy.array=None, samplerate:int=None, beatmap:list=None, threshold=0.3, declumping=50):
        if filename is None:
            from tkinter.filedialog import askopenfilename
            self.filename = askopenfilename(title='select song')
            #self.audio, self.samplerate=open_audio(self.filename)
        else: 
            self.filename=filename

        if self.filename.lower().endswith('.zip'): 
            import shutil,os
            if os.path.exists('Saber2Osu_TEMP'): shutil.rmtree('Saber2Osu_TEMP')
            os.mkdir('Saber2Osu_TEMP')
            shutil.unpack_archive(self.filename, 'Saber2Osu_TEMP')
            bs_difficulty=[]
            self.difficulties=[]
            diflist=[]
            for root,dirs,files in os.walk('Saber2Osu_TEMP'):
                for fname in files:
                    #print(fname)
                    if fname.lower().endswith('egg'): os.rename(root.replace('\\','/')+'/'+fname, root.replace('\\','/')+'/'+fname.replace('.egg','.ogg'))
                    if fname.lower().endswith('.mp3') or fname.lower().endswith('.wav') or fname.lower().endswith('.ogg') or fname.lower().endswith('.flac'):
                        self.filename=root.replace('\\','/')+'/'+fname
                        #self.audio, self.samplerate=open_audio(root.replace('\\','/')+'/'+fname)
                    elif fname.lower()=="info.dat":
                        with open (root.replace('\\','/')+'/'+fname, 'r') as f:
                            bs_info=f.read()
                    elif fname.lower().endswith('.dat'):
                        with open (root.replace('\\','/')+'/'+fname, 'r') as f:
                            bs_difficulty.append(f.read())
                            diflist.append(fname)
            for i in bs_difficulty: 
                beats,self.artist,self.title,self.songfilename=import_BeatSaber(bs_info, i, threshold=threshold, declumping=declumping)
                self.difficulties.append(beats)

            for i in range(len(self.difficulties)):
                with open(f'Saber2Osu_TEMP/{self.artist} - {self.title} [Saber2Osu {diflist[i]}].osu', 'x') as f:
                    f.write(osufile(self.title, self.artist, diflist[i], self.songfilename) + self.difficulties[i])
            shutil.make_archive('Saber2Osu_TEMP', 'zip', 'Saber2Osu_TEMP')
            os.rename('Saber2Osu_TEMP.zip', f'[Saber2Osu] {self.artist} - {self.title}.osz')
            shutil.rmtree('Saber2Osu_TEMP')

            

        
