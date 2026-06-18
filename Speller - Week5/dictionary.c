// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
} node;

// Increased buckets for better performance (26 * 26 for first two letters)
const unsigned int N = 676;

// Hash table
node *table[N];

// Global variable to keep track of the dictionary size
unsigned int word_count = 0;

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // Hash the word to find the correct bucket
    unsigned int bucket = hash(word);

    // Set a cursor to point to the start of the linked list at that bucket
    node *cursor = table[bucket];

    // Traverse the linked list
    while (cursor != NULL)
    {
        // Use strcasecmp for case-insensitive comparison
        if (strcasecmp(cursor->word, word) == 0)
        {
            return true;
        }
        cursor = cursor->next;
    }

    return false;
}

// Hashes word to a number
// Uses the first two letters of the word for fewer collisions
unsigned int hash(const char *word)
{
    unsigned int hash_value = 0;

    // Hash based on the first letter
    hash_value += (toupper(word[0]) - 'A') * 26;

    // If there's a second letter, factor it in
    if (word[1] != '\0' && word[1] != '\'')
    {
        hash_value += (toupper(word[1]) - 'A');
    }

    // Ensure we stay within bounds, just in case
    return hash_value % N;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // Open the dictionary file
    FILE *dict_file = fopen(dictionary, "r");
    if (dict_file == NULL)
    {
        return false;
    }

    // Buffer to store the current word (plus 1 for null terminator)
    char buffer[LENGTH + 1];

    // Read strings from file until EOF
    while (fscanf(dict_file, "%s", buffer) != EOF)
    {
        // Create a new node for each word
        node *new_node = malloc(sizeof(node));
        if (new_node == NULL)
        {
            fclose(dict_file);
            return false;
        }

        // Copy the word into the node
        strcpy(new_node->word, buffer);

        // Determine the hash value
        unsigned int hash_value = hash(buffer);

        // Insert node into the hash table (prepend to the linked list)
        new_node->next = table[hash_value];
        table[hash_value] = new_node;

        // Increment total word counter
        word_count++;
    }

    // Close the file
    fclose(dict_file);

    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    return word_count;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    // Iterate through every bucket in the hash table
    for (int i = 0; i < N; i++)
    {
        node *cursor = table[i];

        // Traverse and free the linked list in this bucket
        while (cursor != NULL)
        {
            // Keep a pointer to the next node before freeing the current one
            node *tmp = cursor;
            cursor = cursor->next;
            free(tmp);
        }
    }

    return true;
}
