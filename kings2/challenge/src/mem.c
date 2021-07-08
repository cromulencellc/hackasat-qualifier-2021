#include <msg.h>
#include <mem.h> 
#include <link.h>
#include <stdio.h> 
#include <stdlib.h>
#include <string.h> 
#include <sys/mman.h>

static uint8_t *Memory;

static int ReadMemFn(Msg m, int cmd) {
    MemCmd req;
    unpackMsg(m, (uint8_t**)&req);
    if (req->length > 64) { 
        req->length = 64;
    }
    if (req->address + req->length > MEM_SIZE) {
        return -1;
    }
    uint8_t *buf = (uint8_t *)malloc(req->length); 
    memcpy(buf, &Memory[req->address], req->length);
    
    m = createMessage(buf, req->length, LINK_TARGET, LINK_DOWN);
    routeMsg(m);

#ifdef DEBUG  
    m = createMessage(buf, req->length, SYS_TARGET, LOGGER_CMD);
    routeMsg(m);
#endif

    return 1;
}

static int WriteMemFn(Msg m, int cmd) {
    MemCmd req; 
    if (unpackMsg(m, (uint8_t**)&req) < 0) {
        return -1;
    }
    if (req->length > 64) { 
        req->length = 64;
    }
    if (req->address + req->length > MEM_SIZE) {   
        return -1;
    }
    memcpy(&Memory[req->address], &req->data, req->length);
    return 1;
}

void init_mem(void) {
    registerMsgBox(ReadMemFn,   MEM_TARGET, MEM_READ);
    registerMsgBox(WriteMemFn,  MEM_TARGET, MEM_WRITE);

    Memory = mmap((void*)0x12800000, MEM_SIZE, 
        PROT_READ|PROT_WRITE|PROT_EXEC, 
        MAP_ANONYMOUS | MAP_PRIVATE, 
        0, 0);
    
    memset(Memory, 0, MEM_SIZE);
}