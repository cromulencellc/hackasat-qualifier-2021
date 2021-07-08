#pragma once
#include <common.h> 


struct __attribute__((__packed__)) mem_cmd_t  {
    uint16_t address;
    uint16_t length;
    uint8_t  data; 
} ;
typedef struct mem_cmd_t *MemCmd; 

void init_mem(void);
