from cs50 import get_int

# request input from user
while True:
    n = get_int('Height: ')
    if n > 0 and n <= 8:
        break

# print the results
for i in range(n):
    print(' '*(n-i-1), end="")
    print('#'*(i+1))
