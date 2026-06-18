from cs50 import get_string


def main():
    # 1. Get input text from the user
    text = get_string("Text: ")

    # 2. Count letters, words, and sentences
    letters = 0
    words = 0
    sentences = 0

    # We can track word boundaries by checking if a character is a space
    # Initialize words to 1 assuming the text has at least one word
    if len(text) > 0:
        words = 1

    for char in text:
        # Count letters (A-Z, a-z)
        if char.isalpha():
            letters += 1
        # Count words (by spaces)
        elif char.isspace():
            words += 1
        # Count sentences (. ! ?)
        elif char in ['.', '!', '?']:
            sentences += 1

    # 3. Calculate Coleman-Liau index
    # L = average number of letters per 100 words
    # S = average number of sentences per 100 words
    L = (letters / words) * 100
    S = (sentences / words) * 100

    index = round(0.0588 * L - 0.296 * S - 15.8)

    # 4. Output the grade level
    if index >= 16:
        print("Grade 16+")
    elif index < 1:
        print("Before Grade 1")
    else:
        print(f"Grade {index}")


if __name__ == "__main__":
    main()
