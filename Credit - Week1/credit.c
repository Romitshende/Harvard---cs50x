#include <cs50.h>
#include <stdio.h>

int main(void)
{
    long number = get_long("Number: ");

    long temp = number;
    int sum = 0;
    int position = 0;
    int length = 0;

    int first_two = 0;
    int first_one = 0;

    // Luhn's algorithm
    while (temp > 0)
    {
        int digit = temp % 10;

        if (position % 2 == 1)
        {
            int product = digit * 2;

            if (product > 9)
            {
                sum += (product / 10) + (product % 10);
            }
            else
            {
                sum += product;
            }
        }
        else
        {
            sum += digit;
        }

        temp /= 10;
        position++;
        length++;
    }

    // Find starting digits
    temp = number;

    while (temp >= 100)
    {
        temp /= 10;
    }

    first_two = temp;
    first_one = temp / 10;

    // Check validity
    if (sum % 10 != 0)
    {
        printf("INVALID\n");
    }
    else if (length == 15 && (first_two == 34 || first_two == 37))
    {
        printf("AMEX\n");
    }
    else if (length == 16 && (first_two >= 51 && first_two <= 55))
    {
        printf("MASTERCARD\n");
    }
    else if ((length == 13 || length == 16) && first_one == 4)
    {
        printf("VISA\n");
    }
    else
    {
        printf("INVALID\n");
    }
}
