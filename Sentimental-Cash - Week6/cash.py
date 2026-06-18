from cs50 import get_float


def main():
    # 1. Prompt the user for valid change owed
    while True:
        dollars = get_float("Change owed: ")
        if dollars >= 0:
            break

    # 2. Convert dollars to cents and round to avoid floating-point errors
    cents = round(dollars * 100)

    # 3. Initialize coin counter
    coins = 0

    # 4. Greedy algorithm: Use largest coins possible
    # Quarters (25¢)
    coins += cents // 25
    cents %= 25

    # Dimes (10¢)
    coins += cents // 10
    cents %= 10

    # Nickels (5¢)
    coins += cents // 5
    cents %= 5

    # Pennies (1¢)
    coins += cents // 1
    cents %= 1

    # 5. Print the total number of coins
    print(coins)


if __name__ == "__main__":
    main()
