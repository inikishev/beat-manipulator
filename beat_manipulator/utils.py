C_SLICE = ":><"  # 0 - range, 1 - first, 2 - last
C_JOIN = ",;~&^$}" # 0 - append, 1 - first length, 2 - cut, 3 - maximum, 4 - sidechain
C_MISC = "'\"`i@_?%#![]"
# 0 ',1 " - sample, 2 ` - sample uncut, 3 i - current, 4 @ - random, 
# # 5 _ - random sep, 6 ? - not count, 7 % - create variable, 8 # - shuffle, 9 ! skip
# 10, 11 [] - song
C_MATH = '+-*/.'
C_MATH_STRICT = '.+-*/'

def _safer_eval(string:str) -> float:
    if isinstance(string, str): 
        try:
            for i in (C_MISC[4], C_MISC[7], C_MISC[8]):
                if i in string: string = string[:string.find(i)]
            string = string.replace('{', '<').replace('}', '>')
            string = eval(''.join([i for i in string if i.isdecimal() or i in C_MATH]))
        except (NameError, SyntaxError): string = 1
    return string

def _safer_eval_strict(string:str) -> float:
    if isinstance(string, str): 
        for n, v in enumerate(string):
            assert v in C_MATH_STRICT or v == ' ' or v.isdecimal, f"_safer_eval_strict error: {string}[{n}] = {v}, which isn't a decimal, isn't in {C_MATH_STRICT} and isn't a space"
        string = eval(''.join([i for i in string if i.isdecimal() or i in C_MATH_STRICT]))
    return string
