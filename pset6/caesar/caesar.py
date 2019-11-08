from cs50 import get_string
import sys

# check that 1 argument is provide
if len(sys.argv) != 2:
    print('Usage: python caesar.py k')
    sys.exit(1)

# preparing the key
k = int(sys.argv[1])%26
# get plain text
plain = get_string('plaintext: ')

# print ciphertext
print('ciphertext: ', end='')

# go via each character
for p in plain:
    if not p.isalpha():
        print(p, end='')
    else:
        if p.isupper():
            c = 65 + (ord(p) + k - 65) % 26
        else:
            c = 97 + (ord(p) + k - 97) % 26
        print(chr(c), end='')
print()