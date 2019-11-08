from cs50 import get_float

# request input from user
while True:
    n = get_float('Change owed: ')
    if n > 0:
        break

c = round(n * 100)
# check 25c
n25 = c // 25
c25 = c % 25
# check 10c
n10 = c25 // 10
c10 = c25 % 10
# check 5c
n5 = c10 // 5
c5 = c10 % 5
# check 1c
n1 = c5

numb = n25 + n10 + n5 + n1
print(numb)