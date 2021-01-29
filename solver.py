#!/usr/bin/python3
from z3 import Int, Solver, unsat, Or, And, Xor, Distinct, sat
import random, itertools

COLORS =  {0:"red", 1:"blue", 2:"violet", 3:"green", 4:"yellow", 5:"orange", 6:"white", 7:"black"}
MAP_SIZE = 4

def verif(real, guess):
    rate = {"red":0, "white":0}
    for i in range(MAP_SIZE):
        if real[i] == guess[i]:
            rate["red"] += 1
        elif guess[i] in real:
            rate["white"] += 1
    return rate

def init_solver(cols):
    s = Solver()
    for col in cols:
        cond = And(col >= 0, col < len(COLORS)) #possible values for each column
        s.add(cond)
    cond_unicity = Distinct(cols) #each column is different
    s.add(cond_unicity)
    return s

def add_conds(rate, s, cols, guess):
    cond = Xor(False, False)
    if rate["red"] != 0 and rate["white"] != 0:
        for combi in itertools.combinations(cols, rate["red"]):
            mid_cond = And()
            not_combi = [col for col in cols if col not in combi]
            red_cond = And()
            for part in combi:
                x = cols.index(part)
                red_cond = And(red_cond, (part == guess[x]))
            for part in not_combi:
                x = cols.index(part)
                red_cond = And(red_cond, (part != guess[x]))

            mid_cond = And(mid_cond, red_cond)

            white_cond = Xor(False, False)
            for combi2 in itertools.combinations(not_combi, rate["white"]):
                not_combi2 = [col for col in cols if (col not in combi and col not in combi2)]
                tmp_white_cond = And()
                for part in combi2:
                    x = cols.index(part)
                    tmp_white_cond = And(tmp_white_cond, (part != guess[x]))
                    tmp_white_cond_tmp = Xor(False, False)
                    for col in cols:
                        if col is not part and col not in combi:
                            tmp_white_cond_tmp = Xor(tmp_white_cond_tmp, (col == guess[x]))
                    tmp_white_cond = And(tmp_white_cond, tmp_white_cond_tmp)
                    for col in not_combi2:
                        x = cols.index(col)
                        for col2 in cols:
                            tmp_white_cond = And(tmp_white_cond, (col2 != guess[x]))                                 
                white_cond = Xor(white_cond, tmp_white_cond)

            mid_cond = And(mid_cond, white_cond)   

            cond = Xor(cond, mid_cond)

    elif rate["red"] != 0:
        for combi in itertools.combinations(cols, rate["red"]):
            mid_cond = And()
            not_combi = [col for col in cols if col not in combi]
            red_cond = And()
            for part in combi: 
                x = cols.index(part)
                red_cond = And(red_cond, (part == guess[x]))
            for part in not_combi:
                x = cols.index(part)
                for col2 in cols:
                    red_cond = And(red_cond, (col2 != guess[x])) 

            mid_cond = And(mid_cond, red_cond)           
            cond = Xor(cond, mid_cond)

    elif rate["white"] != 0:
        mid_cond = And()
        white_cond = Xor(False, False)
        for combi2 in itertools.combinations(cols, rate["white"]):
            not_combi2 = [col for col in cols if (col not in combi2)]
            tmp_white_cond = And()
            for part in combi2:
                x = cols.index(part)
                tmp_white_cond = And(tmp_white_cond, (part != guess[x]))
                tmp_white_cond_tmp = Xor(False, False)
                for col in cols:
                    if col is not part:
                        tmp_white_cond_tmp = Xor(tmp_white_cond_tmp, (col == guess[x]))
                tmp_white_cond = And(tmp_white_cond, tmp_white_cond_tmp)
                for col in not_combi2:
                    x = cols.index(col)
                    for col2 in cols:
                        tmp_white_cond = And(tmp_white_cond, (col2 != guess[x]))                                 
            white_cond = Xor(white_cond, tmp_white_cond)

        mid_cond = And(mid_cond, white_cond)   

        cond = Xor(cond, mid_cond)

    else:
        cond = And()
        for x,col in enumerate(cols):
            for col2 in cols:
                cond = And(cond, (col2 != guess[x]))

    s.add(cond)

if __name__ == '__main__':
    choosen_combi = random.sample(list(COLORS.keys()), k=MAP_SIZE)
    print("Base : ", choosen_combi)
    guess_ctr = 0
    cols = [Int("col_%d" % i) for i in range(MAP_SIZE)]
    s = init_solver(cols)

    while True:
        guess_ctr += 1
        if s.check() == unsat:
            print("Error :(")
            exit(1)
        else:
            m = s.model()
            guess = [m[col].as_long() for col in cols]
            print("Guess %d : " % guess_ctr, guess)
        rate = verif(choosen_combi, guess)
        print(rate)
        if rate["red"] == MAP_SIZE:
            break
        else:
            add_conds(rate, s, cols, guess)
    print("Guessed in %d try" % guess_ctr)