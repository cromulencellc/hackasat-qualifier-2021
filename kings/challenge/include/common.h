#pragma once

#include <stdint.h>

#define MEM_SIZE    0x1000

#define NUMCMDS     4
#define NUMBOX      4

// Up/Down Link
#define LINK_TARGET     0x0
// Cmds
#define LINK_DOWN       0x0

// Telemetry
#define TLM_TARGET  0x1
// Cmds
#define TLM_REQ     0x0
#define TLM_UPDATE  0x1
// Memory Manager
#define MEM_TARGET  0x2
// Cmds
#define MEM_READ    0x0
#define MEM_WRITE   0x1

// System 
#define SYS_TARGET (NUMBOX-1)
// Cmds
#define SHUTDOWN_CMD 0
#define LOGGER_CMD (NUMCMDS-1)
