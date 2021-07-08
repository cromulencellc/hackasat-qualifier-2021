
#include "stdint.h"

int is_nan(double value) {

  if (value != value) {

    return 1;
  }

  return 0;
}

int is_inf(double value) {

uint64_t fract;
uint16_t exp;

  exp = ((*(uint64_t *)&value) >> 52 ) & 0x7ff;

  fract = (*(uint64_t *)&value) & 0xfffffffffffff;

  if (exp == 0x7ff && fract == 0) 
    return 1;
  else
    return 0;

}

