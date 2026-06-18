import csv
import sys


def main():

    # TODO: Check for command-line usage
    if len(sys.argv) != 3:
        print("Usage: python dna.py data.csv sequence.txt")
        sys.exit(1)

    # TODO: Read database file into a variable
    database = []
    with open(sys.argv[1], "r") as csvfile:
        reader = csv.DictReader(csvfile)
        # Store the STR headers (everything except the 'name' column)
        strs = reader.fieldnames[1:]
        for row in reader:
            database.append(row)

    # TODO: Read DNA sequence file into a variable
    with open(sys.argv[2], "r") as txtfile:
        dna_sequence = txtfile.read()

    # TODO: Find longest match of each STR in DNA sequence
    run_counts = {}
    for STR in strs:
        run_counts[STR] = longest_match(dna_sequence, STR)

    # TODO: Check database for matching profiles
    for person in database:
        match = True
        for STR in strs:
            # Note: DictReader stores values as strings, so convert to int to compare
            if int(person[STR]) != run_counts[STR]:
                match = False
                break

        # If all STR counts match for a person, print their name and terminate
        if match:
            print(person["name"])
            return

    # If the loop finishes without returning, no match was found
    print("No match")

    return


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):

        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:

            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in sequence, return longest run found
    return longest_run


main()
