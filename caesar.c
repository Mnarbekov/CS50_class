#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>


int main(int argc, string argv[])
{
    // Check number of arguments =2
    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    string key = argv[1];
    // Check all values of agrument are numbers
    for (int i = 0, n = strlen(key); i < n; i++)
    {
        if (!isdigit(key[i]))
        {
          printf("Usage: ./caesar key\n");
          return 1;  
        }   
    }
    
    int k = atoi(argv[1]);
    // Get plaintext
    string plaintext = get_string("plaintext: ");
  
    // Return ciphertext
    printf("ciphertext: ");
    // Shift each letter
    for (int i = 0, n = strlen(plaintext); i < n; i++)
    {
        char p = plaintext[i];
        if (p >= 97 & p <= 122)
        {
            char c = 97 + (p + k - 97) % 26;
            printf("%c", c);
        }
        else
        {
            if (p >= 65 & p <= 90)
            {
                char c = 65 + (p + k - 65) % 26;
                printf("%c", c);
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

