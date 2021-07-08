
#include <stdio.h>

main(void) {


union reg {

   float f;
   double f2;
   unsigned int d;
}; 

union reg reg1;

reg1.d = 33;

//reg1.f = (float)reg1.d;

printf("size of = %d\n", sizeof(union reg));
printf("%f\n", reg1.f);

printf("%d\n", reg1.d);

}

