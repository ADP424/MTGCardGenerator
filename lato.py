import itertools
import re


input = """
    "w/u/b": Symbol(WHITE_BLUE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/r/w": Symbol(BLUE_RED_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/w/u": Symbol(GREEN_WHITE_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/w/b": Symbol(RED_WHITE_BLACK_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/b/g": Symbol(WHITE_BLACK_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/g/w": Symbol(RED_GREEN_WHITE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/b/r": Symbol(BLUE_BLACK_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/g/u": Symbol(BLACK_GREEN_BLUE_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/u/r": Symbol(GREEN_BLUE_RED_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/r/g": Symbol(BLACK_RED_GREEN_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/u/c": Symbol(WHITE_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "w/b/c": Symbol(WHITE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/b/c": Symbol(BLUE_BLACK_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "u/r/c": Symbol(BLUE_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/r/c": Symbol(BLACK_RED_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "b/g/c": Symbol(BLACK_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/g/c": Symbol(RED_GREEN_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "r/w/c": Symbol(RED_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/w/c": Symbol(GREEN_WHITE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
    "g/u/c": Symbol(GREEN_BLUE_COLORLESS_MANA, HYBRID_MANA_SYMBOL_SIZE_MULT),
"""

output = ""
for line in input.split("\n"):
    if len(line.strip()) == 0:
        continue
    mana = list(re.findall(r"\"(.*)/(.*)/(.*)\"", line)[0])
    for perm in itertools.permutations(mana):
        f, s, t = perm
        output += re.sub(r"\".*/.*/.*\"", f'"{f}/{s}/{t}"', line) + "\n"
print(output)