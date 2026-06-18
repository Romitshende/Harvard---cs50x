#include "helpers.h"
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Calculate the average of the RGB channels
            float average =
                (image[i][j].rgbtRed + image[i][j].rgbtGreen + image[i][j].rgbtBlue) / 3.0;
            int rounded_avg = round(average);

            // Assign the average back to all channels
            image[i][j].rgbtRed = rounded_avg;
            image[i][j].rgbtGreen = rounded_avg;
            image[i][j].rgbtBlue = rounded_avg;
        }
    }
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        // Only loop up to half the width to swap pixels
        for (int j = 0; j < width / 2; j++)
        {
            RGBTRIPLE temp = image[i][j];
            image[i][j] = image[i][width - 1 - j];
            image[i][width - 1 - j] = temp;
        }
    }
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    // Create a temporary copy of the image
    RGBTRIPLE copy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j] = image[i][j];
        }
    }

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int sumRed = 0, sumGreen = 0, sumBlue = 0;
            float counter = 0.0;

            // Check the 3x3 neighbor grid
            for (int r = -1; r <= 1; r++)
            {
                for (int c = -1; c <= 1; c++)
                {
                    int neighborI = i + r;
                    int neighborJ = j + c;

                    // Ensure neighboring pixel is within image boundaries
                    if (neighborI >= 0 && neighborI < height && neighborJ >= 0 && neighborJ < width)
                    {
                        sumRed += copy[neighborI][neighborJ].rgbtRed;
                        sumGreen += copy[neighborI][neighborJ].rgbtGreen;
                        sumBlue += copy[neighborI][neighborJ].rgbtBlue;
                        counter++;
                    }
                }
            }

            // Write rounded averages to the original image
            image[i][j].rgbtRed = round(sumRed / counter);
            image[i][j].rgbtGreen = round(sumGreen / counter);
            image[i][j].rgbtBlue = round(sumBlue / counter);
        }
    }
}

// Detect edges (Sobel Filter)
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    // Create a temporary copy of the image
    RGBTRIPLE copy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j] = image[i][j];
        }
    }

    // Sobel kernels
    int Gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};

    int Gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            float gx_red = 0, gx_green = 0, gx_blue = 0;
            float gy_red = 0, gy_green = 0, gy_blue = 0;

            // Check the 3x3 neighbor grid
            for (int r = -1; r <= 1; r++)
            {
                for (int c = -1; c <= 1; c++)
                {
                    int neighborI = i + r;
                    int neighborJ = j + c;

                    // Out of bounds pixels are treated as 0 (solid black), so we only calculate for
                    // valid pixels
                    if (neighborI >= 0 && neighborI < height && neighborJ >= 0 && neighborJ < width)
                    {
                        int weightX = Gx[r + 1][c + 1];
                        int weightY = Gy[r + 1][c + 1];

                        gx_red += copy[neighborI][neighborJ].rgbtRed * weightX;
                        gx_green += copy[neighborI][neighborJ].rgbtGreen * weightX;
                        gx_blue += copy[neighborI][neighborJ].rgbtBlue * weightX;

                        gy_red += copy[neighborI][neighborJ].rgbtRed * weightY;
                        gy_green += copy[neighborI][neighborJ].rgbtGreen * weightY;
                        gy_blue += copy[neighborI][neighborJ].rgbtBlue * weightY;
                    }
                }
            }

            // Calculate the Sobel magnitude square root formula
            int final_red = round(sqrt(gx_red * gx_red + gy_red * gy_red));
            int final_green = round(sqrt(gx_green * gx_green + gy_green * gy_green));
            int final_blue = round(sqrt(gx_blue * gx_blue + gy_blue * gy_blue));

            // Cap values at 255 if they overflow
            image[i][j].rgbtRed = (final_red > 255) ? 255 : final_red;
            image[i][j].rgbtGreen = (final_green > 255) ? 255 : final_green;
            image[i][j].rgbtBlue = (final_blue > 255) ? 255 : final_blue;
        }
    }
}
