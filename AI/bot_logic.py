import random

def gen_pass(pass_length):
    elements = "+-/*!&$#?=@<>"
    password = ""
    for i in range(pass_length):
        password += random.choice(elements)
    return password

def coinflip():
    num = random.randint(1, 2)
    return "Heads" if num == 1 else "Tails"

def roll_dice():
    return random.randint(1, 6)
