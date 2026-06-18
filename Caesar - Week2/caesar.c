#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, string argv[])
{
    // 1. Make sure the user provided exactly one command-line argument
    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    // 2. Make sure every character in the key string is a digit
    for (int i = 0, n = strlen(argv[1]); i < n; i++)
    {
        if (!isdigit(argv[1][i]))
        {
            printf("Usage: ./caesar key\n");
            return 1;
        }
    }

    // 3. Convert the key string into an actual integer
    int key = atoi(argv[1]);

    // 4. Prompt the user for the plaintext
    string plaintext = get_string("plaintext:  ");

    // 5. Start printing the ciphertext
    printf("ciphertext: ");

    // 6. Iterate through each character of the plaintext
    for (int i = 0, n = strlen(plaintext); i < n; i++)
    {
        // Check if the character is uppercase
        if (isupper(plaintext[i]))
        {
            // Shift ASCII to alphabetical index (0-25), apply key, wrap around, shift back
            char c = ((plaintext[i] - 'A' + key) % 26) + 'A';
            printf("%c", c);
        }
        // Check if the character is lowercase
        else if (islower(plaintext[i]))
        {
            // Shift ASCII to alphabetical index (0-25), apply key, wrap around, shift back
            char c = ((plaintext[i] - 'a' + key) % 26) + 'a';
            printf("%c", c);
        }
        // If it's not a letter, print it exactly as it is
        else
        {
            printf("%c", plaintext[i]);
        }
    }

    // 7. Print a final newline and exit cleanly
    printf("\n");
    return 0;
}
