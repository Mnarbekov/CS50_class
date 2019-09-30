#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int shift(char c);

int main(int argc, string argv[])
{
    // Check number of arguments =2
    if (argc != 2)
    {
        printf("Usage: ./caesar keyword\n");
        return 1;
    }
    string word = argv[1];
    // Check all values of agrument are not numbers
    for (int i = 0, n = strlen(word); i < n; i++)
    {
        if (isdigit(word[i]))
        {
          printf("Usage: ./vigenere keyword\n");
          return 1;  
        }   
    }
 
    
    int key = 0;
    
    
    // Get plaintext
    string plaintext = get_string("plaintext: ");
  
    // Return ciphertext
    printf("ciphertext: ");
    // Shift each letter
    int j = 0;
    for (int i = 0, n = strlen(plaintext); i < n; i++)
    {
        // Counter for key word
        if (j >= strlen(word))
            {
                j = 0;
            }
        
        
        // call shift function - convert letter to number
        key = shift(argv[1][j]);
        
        
        char p = plaintext[i];
        if (p >= 97 & p <= 122)
        {
            char c = 97 + (p + key - 97) % 26;
            printf("%c", c);
            j = j + 1;
        }
        else
        {
        
            if (p >= 65 & p <= 117)
            {
                char c = 65 + (p + key - 65) % 26;
                printf("%c", c);
                j = j + 1;
            } 
            else 
            {
                printf("%c", p);
            }
        }
        
    }
    printf("\n");
    
    
    return 0;
}

int shift(char c)
{
    int k = (int)c;
    int l = 0;
    if (k >= 97 & k <= 122)
    {
        l = k - 97;
    }
    else 
    {
        if (k >= 65 & k <= 90)
        {
            l = k - 65;
        }
    }
    return l;
}
