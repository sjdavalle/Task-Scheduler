#include<stdio.h>   
#include <unistd.h>

int main(void) 
{ 
   printf("dummy process.\n"); 
   while(1)
   {
       sleep(10); 
   }
   return 0; 
}