# This is a default preset that colors every second letter of the username

def main(USERNAME):
    k = len(USERNAME)
    colored = range(0, k, 2)
    uncolored = range(1, k, 2)

    return colored, uncolored
