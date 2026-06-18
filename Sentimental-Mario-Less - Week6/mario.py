from cs50 import get_int

while True:
    height = get_int("Height : ")
    if 1 <= height <= 8:
        break

for rows in range(height):
    for columns in range(height - rows - 1):
        print(" ", end="")

    for brick in range(rows + 1):
        print("#", end="")

    print()
