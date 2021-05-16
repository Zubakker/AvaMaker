# This is a default preset that colors every capitalized letter of the username

def main(USERNAME):
    colored = list()
    uncolored = list()
    for i in range(len(USERNAME)):
        if USERNAME[i].isupper():
            colored.append(i)
        else:
            uncolored.append(i)
    return colored, uncolored

