#include <msg.h>
#include <mem.h>
#include <tlm.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>  
#include <string.h>

int running = 0;

#ifdef DEBUG
#include <stdio.h> 
#define LOG(str) {\
    routeMsg(createMessage(str, strlen(str), SYS_TARGET, LOGGER_CMD));\
}
static int LoggerFn(Msg m, int cmd) { 
    uint8_t *bytes; 
    int len = unpackMsg(m, &bytes);
    fprintf(stderr, "%s\n", (char*)bytes);    
    return 1;
}
#else 
#define LOG(...) while(0){};
static int LoggerFn(Msg m, int cmd) {
    return 1;   
}
#endif 

static int ShutdownFn(Msg m, int cmd) { 
    running = 0;
    return 1;   
}

void loadFlags(void){ 
    struct { 
        uint16_t address;
        uint16_t length;
        char buf[64]; 
    } body ;
    memset(&body.buf, 0, sizeof(body.buf));
    int fd = open("./flag1.txt", O_RDONLY);
    if (fd >= 0) {
        body.address = 0x0;
        body.length = read(fd, &body.buf, sizeof(body.buf));
        close(fd);
        routeMsg(createMessage(&body, 4 + body.length, MEM_TARGET, MEM_WRITE));
    }

    memset(&body.buf, 0, sizeof(body.buf));
    fd = open("./bank/flag2.txt", O_RDONLY);
    if (fd >= 0) {
        body.address = 0x20;
        body.length = read(fd, &body.buf, sizeof(body.buf));
        close(fd);
        routeMsg(createMessage(&body, 4 + body.length, MEM_TARGET, MEM_WRITE));
    }
}

velocity_t vel;

void loop() { 
    Msg m; 

    running = 1;
    while (running) {
        if ( recvMsg(&m) ) {
            routeMsg(m);
        } 
        vel.vx = 1.0;
        vel.vy = 2.0;
        vel.vz = 0.0;
        routeMsg(createMessage(&vel, sizeof(vel), TLM_TARGET, TLM_UPDATE));
    }
}

int main(int argc, char *argv[]) {
    init_msgs();
    init_mem();
    init_tlm();
    registerMsgBox(LoggerFn, SYS_TARGET, LOGGER_CMD);
    registerMsgBox(ShutdownFn, SYS_TARGET, SHUTDOWN_CMD);

    LOG("Start up Complete");
    LOG("Loading Flags...");
    
    loadFlags();

    loop();

    return 0;
}