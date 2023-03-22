from .utils import C_SLICE, C_JOIN, C_MISC, C_MATH
import numpy as np
from . import io, utils, main
def _getnum(pattern, cur, symbols = '+-*/'):
    number = ''
    while pattern[cur].isdecimal() or pattern[cur] in symbols:
        number+=pattern[cur]
        cur+=1
    return number, cur-1

def parse(pattern:str, samples:dict, pattern_length:int = None,
        c_slice:str = C_SLICE,
        c_join:str = C_JOIN, 
        c_misc:str = C_MISC,
        log = True,
        simple_mode = False):
    """Returns (beats, operators, pattern_length, c_slice, c_misc, c_join)"""
    if log is True: print(f'Beatswapping with `{pattern}`')
    
    #load samples:
    if isinstance(samples, str): samples = (samples,)
    if not isinstance(samples, dict):
        samples = {str(i+1):samples[i] for i in range(len(samples))}

    #preprocess pattern
    separator = c_join[0]
    #forgot separator
    if simple_mode is True:
        if c_join[0] not in pattern and c_join[1] not in pattern and c_join[2] not in pattern and c_join[3] not in pattern: pattern = pattern.replace(' ', separator)
    if ' ' not in c_join: pattern = pattern.replace(' ', '') # ignore spaces
    for i in c_join:
        while i+i in pattern: pattern = pattern.replace(i+i, i) #double separator
        while pattern.startswith(i): pattern = pattern[1:]
        while pattern.endswith(i): pattern = pattern[:-1]

    # Creates a list of beat strings so that I can later see if there is a `!` in the string
    separated = pattern
    for i in c_join:
        separated = separated.replace(i, c_join[0])
    separated = separated.split(c_join[0])
    pattern = pattern.replace(c_misc[6], '')
    
    # parsing
    length = 0
    num = ''
    cur = 0
    beats = []
    operators = [separator]
    shuffle_beats = []
    shuffle_groups = []
    current_beat = 0
    effect = None
    pattern += ' '
    sample_toadd = None

    # Loops over all characters
    while cur < len(pattern):
        char = pattern[cur]
        #print(f'char = {char}, cur = {cur}, num = {num}, current_beat = {current_beat}, effect = {effect}, len(beats) = {len(beats)}, length = {length}')
        if char == c_misc[3]: char = str(current_beat+1)  # Replaces `i` with current number

        # If character is `", ', `, or [`: searches for closing quote and gets the sample rate, 
        # moves cursor to the character after last quote/bracket, creates a sample_toadd variable with the sample.
        elif char in c_misc[0:3]+c_misc[10:12]:
            quote = char
            if quote == c_misc[10]: quote = c_misc[11] # `[` is replaced with `]`
            cur += 1
            sample = ''

            # Gets sample name between quote characters, moves cursor to the ending quote.
            while pattern[cur] != quote:
                sample += pattern[cur]
                cur += 1
            assert sample in samples, f"No sample named `{sample}` found in samples. Available samples: {samples.keys()}"
            
            # If sample is a song, it will be converted to a song if needed, and beatmap will be generated
            if quote == c_misc[11]: 
                if not isinstance(samples[sample], main.song): samples[sample] = main.song(samples[sample])
                if samples[sample].beatmap is None: 
                    samples[sample].beatmap_generate()
                    samples[sample].beatmap_adjust()

            # Else sample is a sound file
            elif not isinstance(samples[sample], np.ndarray): samples[sample] = io._load(samples[sample])[0] 

            sample_toadd = [samples[sample], [], quote, None] # Creates the sample_toadd variable
            cur += 1
            char = pattern[cur]

        # If character is a math character, a slice character, or `@_?!%` - random, not count, skip, create variable -
        # - it gets added to `num`, and the loop repeats.
        # _safer_eval only takes part of the expression to the left of special characters (@%#), so it won't affect length calculation
        if char.isdecimal() or char in (C_MATH + c_slice + c_misc[4:8] + c_misc[9]):
            num += char
            #print(f'char = {char}, added it to num: num = {num}')

            # If character is `%` and beat hasn't been created yet, it takes the next character as well
            if char == c_misc[7] and len(beats) == current_beat:
                cur += 1
                char = pattern[cur]
                num += char

        # If character is a shuffle character `#` + math expression, beat number gets added to `shuffle_beats`, 
        # beat shuffle group gets added to `shuffle_groups`, cursor is moved to the character after the math expression, and loop repeats.
        # That means operations after this will only execute once character is not a math character.
        elif char == c_misc[8]:
            cur+=1
            number, cur = _getnum(pattern, cur)
            char = pattern[cur]
            shuffle_beats.append(current_beat)
            shuffle_groups.append(number)

        # If character is not math/shuffle, that means math expression has ended. Now it tries to figure out where the expression belongs, 
        # and parses the further characters
        else:
            
            # If the beat has not been added, it adds the beat. Also figures out pattern length.
            if len(beats) == current_beat and len(num) > 0:
                # Checks all slice characters in the beat expression. If slice character is found, splits the slice and breaks.
                for c in c_slice:
                    if c in num:
                        num = num.split(c)[:2] + [c]
                        #print(f'slice: split num by `{c}`, num = {num}, whole beat is {separated[current_beat]}')
                        if pattern_length is None and c_misc[6] not in separated[current_beat]:
                            num0, num1 = utils._safer_eval(num[0]), utils._safer_eval(num[1])
                            if c == c_slice[0]: length = max(num0, num1, length)
                            if c == c_slice[1]: length = max(num0-1, num0+num1-1, length)
                            if c == c_slice[2]: length = max(num0-num1, num0, length)
                        break
                # If it didn't break, the expression is not a slice, so it pattern length is just compared with the beat number.
                else: 
                    #print(f'single beat: {num}. Whole beat is {separated[current_beat]}')
                    if c_misc[6] not in separated[current_beat]: length = max(utils._safer_eval(num), length)

                # If there no sample saved in `sample_toadd`, adds the beat to list of beats.
                if sample_toadd is None: beats.append([num, []])
                # If `sample_toadd` is not None, beat is a sample/song. Adds the beat and sets sample_toadd to None
                else: 
                    sample_toadd[3] = num
                    beats.append(sample_toadd)
                    sample_toadd = None
                #print(f'char = {char}, got num = {num}, appended beat {len(beats)}')

            # Sample might not have a `num` with a slice, this adds the sample without a slice
            elif len(beats) == current_beat and len(num) == 0 and sample_toadd is not None:
                beats.append(sample_toadd)
                sample_toadd = None

            # If beat has been added, it now parses beats.
            if len(beats) == current_beat+1:
                #print(f'char = {char}, parsing effects:')

                # If there is an effect and current character is not a math character, effect and value are added to current beat, and effect is set to None
                if effect is not None:
                    #print(f'char = {char}, adding effect: type = {effect}, value = {num}')
                    beats[current_beat][1].append([effect, num if num!='' else None])
                    effect = None

                # If current character is a letter, it sets that letter to `effect` variable. 
                # Since loop repeats after that, that while current character is a math character, it gets added to `num`.
                if char.isalpha() and effect is None:
                    #print(f'char = {char}, effect type is {effect}')
                    effect = char

            # If character is a beat separator, it starts parsing the next beat in the next loop. 
            if char in c_join and len(beats) == current_beat + 1:
                #print(f'char = {char}, parsing next beat')
                current_beat += 1
                effect = None
                operators.append(char)

            num = '' # `num` is set to empty string. btw `num` is only used in this loop so it needs to be here
        
        cur += 1 # cursor goes to the next character

    
    #for i in beats: print(i)
    import math
    if pattern_length is None: pattern_length = int(math.ceil(length))

    return beats, operators, pattern_length, shuffle_groups, shuffle_beats, c_slice, c_misc, c_join

# I can't be bothered to annotate this one. It just works, okay?
def _random(beat:str, length:int, rchar = C_MISC[4], schar = C_MISC[5]) -> str:
    """Takes a string and replaces stuff like `@1_4_0.5` with randomly generated number where 1 - start, 4 - stop, 0.5 - step. Returns string."""
    import random
    beat+=' '
    while rchar in beat:
        rand_index = beat.find(rchar)+1
        char = beat[rand_index]
        number = ''
        while char.isdecimal() or char in '.+-*/':
            number += char
            rand_index+=1
            char = beat[rand_index]
        if number != '': start = utils._safer_eval(number)
        else: start = 0
        if char == schar:
            rand_index+=1
            char = beat[rand_index]
            number = ''
            while char.isdecimal() or char in '.+-*/':
                number += char
                rand_index+=1
                char = beat[rand_index]
            if number != '': stop = utils._safer_eval(number)
            else: stop = length
            if char == schar:
                rand_index+=1
                char = beat[rand_index]
                number = ''
                while char.isdecimal() or char in '.+-*/':
                    number += char
                    rand_index+=1
                    char = beat[rand_index]
                if number != '': step = utils._safer_eval(number)
                else: step = length
        choices = []
        while start <= stop:
            choices.append(start)
            start+=step
        beat = list(beat)
        beat[beat.index(rchar):rand_index] = list(str(random.choice(choices)))
        beat = ''.join(beat)
    return beat

def _shuffle(pattern: list, shuffle_beats: list, shuffle_groups: list) -> list:
    """Shuffles pattern according to shuffle_beats and shuffle_groups"""
    import random
    done = []
    result = pattern.copy()
    for group in shuffle_groups:
        if group not in done:
            shuffled = [i for n, i in enumerate(shuffle_beats) if shuffle_groups[n] == group]
            unshuffled = shuffled.copy()
            random.shuffle(shuffled)
            for i in range(len(shuffled)):
                result[unshuffled[i]] = pattern[shuffled[i]]
            done.append(group)
    return result

def _metric_get(v, beat, metrics, c_misc7 = C_MISC[7]):
    assert v[v.find(c_misc7)+1] in metrics, f'`%{v[v.find(c_misc7)+1]}`: No metric called `{v[v.find(c_misc7)+1]}` found in metrics. Available metrics: {metrics.keys()}'
    metric = metrics[v[v.find(c_misc7)+1]](beat)
    return metric


def _metric_replace(v, metric, c_misc7 = C_MISC[7]):
    for _ in range(v.count(c_misc7)):
        v= v[:v.find(c_misc7)] + str(metric) + v[v.find(c_misc7)+2:]
    return v