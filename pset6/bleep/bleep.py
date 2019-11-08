from cs50 import get_string
import sys


def main():

    # check that 1 argument is provide
    if len(sys.argv) != 2:
        print('Usage: python bleep.py dictionary')
        sys.exit(1)

    # open dictionary
    dic = sys.argv[1]
    words = set()

    file = open(dic, "r")
    for line in file:
        words.add(line.rstrip("\n"))
    file.close()

    # temp print
    #print(words)

    # ask for text
    print('What message would you like to censor?')
    txt = get_string('')

    # check words
    x = txt.split(" ")
    for i in x:
        if i.lower() in words:
            print('*'*len(i), end='')
            print(' ', end='')
        else:
            print(i, end='')
            print(' ', end='')

    print()

if __name__ == "__main__":
    main()
