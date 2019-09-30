#include <cs50.h>
#include <stdio.h>
#include <math.h>

int main(void)
{
    float cash;
    do 
    { 
        cash = get_float("Cash: ");
    }
    while (cash <= 0.009);
    
    int cents = round(cash * 100);
 
    int c25 = cents / 25; 
    int c25r = cents % 25;
   
    int c10 = c25r / 10; 
    int c10r = c25r % 10;
    
    int c5 = c10r / 5; 
    int c5r = c10r % 5;
    
    int c1 = c5r / 1;
    
    printf("%i\n", (c25 + c10 + c5 + c1));
    
}
