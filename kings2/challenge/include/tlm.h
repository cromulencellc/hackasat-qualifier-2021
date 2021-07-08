#pragma once
#include <common.h>

typedef struct { 
    float px;
    float py;
    float pz;
} position_t;

typedef struct { 
    float vx;
    float vy;
    float vz;
} velocity_t;

void init_tlm(void);