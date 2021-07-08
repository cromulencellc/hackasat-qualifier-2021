#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <msg.h>
#include <link.h> 

#ifdef DEBUG 
#include <stdio.h>
#endif 

#define HEADER1 0x55
#define HEADER2 0xAA

struct __attribute__((__packed__)) msgHeader {
    uint8_t  startCode[2];
    uint16_t length;
    uint16_t crc; 
    uint8_t  target;
    uint8_t  cmd; 
} ;

typedef struct msg msg_t; 
struct __attribute__((__packed__)) msg {
    struct msgHeader header;
    uint8_t payload;
}; 
struct {
    MsgBoxFn cmds[NUMCMDS];
} MsgBox[NUMBOX];


#define INITIAL_CRC_CC3         0x1D0F
#define CRC_ARINC_POLY			0xA02B 	

static uint16_t calcCRC(uint8_t *ptr, int count) {
    uint16_t crc;
    uint8_t i;

    crc = INITIAL_CRC_CC3;
    while( --count >= 0 ){
        crc = crc ^ ((uint16_t) (*ptr++ << 8));
        for (i = 0; i < 8; i++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ CRC_ARINC_POLY;
            } else {
                crc = crc << 1;
            }
        }
    }

    return crc;
}

static int defaultBoxFn(Msg m, int cmd) {
    (void)m, cmd;
    return -1;
}

static int downlinkFn(Msg m, int cmd) { 
    (void)cmd;
    int length = sizeof(struct msgHeader) + m->header.length;
    int ret = !!sendData(m, length);
    free(m);
    return ret;
}

void init_msgs(void) {
    for (int id = 0; id < NUMCMDS; id++) {
        for (int cmd = 0; cmd < NUMBOX; cmd++) {
            MsgBox[id].cmds[cmd] = defaultBoxFn;
        }
    }
    MsgBox[LINK_TARGET].cmds[LINK_DOWN] = downlinkFn;
}

Msg createMessage(void * payload, uint32_t length, int id, int cmd) {
    Msg m = malloc(length + sizeof(struct msgHeader));
    if (!m) {
        exit(1);
    }
    m->header.startCode[0] = HEADER1;
    m->header.startCode[1] = HEADER2;
    m->header.length = length;
    m->header.crc    = calcCRC(payload, length);    
    m->header.target = id;
    m->header.cmd    = cmd;
    memcpy(&m->payload, payload, length);

    return m;
}


int unpackMsgInto(Msg m, uint8_t *payload) {
    int length = m->header.length;
    if (m->header.startCode[0] != HEADER1 || m->header.startCode[1] != HEADER2) {
        return -1;
    }
    if (m->header.crc != calcCRC(&m->payload, length)) {
        return -1;
    }
    memcpy(payload, &m->payload, length);
    free(m);
    return length;
} 

int unpackMsg(Msg m, uint8_t **payload) {
    int length = m->header.length;
    *payload = malloc(length);
    length = unpackMsgInto(m, *payload);
    if (length < 0) {
        free(*payload);
        *payload = NULL;
    }
    return length;
} 

int recvMsg(Msg *m) { 
    struct msgHeader head;
    recvData(&head, sizeof(struct msgHeader));
    
    *m = malloc(sizeof(struct msgHeader) + head.length);
    memcpy(*m, &head, sizeof(struct msgHeader));
    if (head.length == 0) {
        return 1;
    }
    return !!recvData(&(*m)->payload, head.length); 
}

void registerMsgBox(MsgBoxFn fn, int id, int cmd) {
    if (id < 0 || id > NUMBOX || cmd < 0 || cmd > NUMCMDS) {
        return;
    }
    MsgBox[id].cmds[cmd] = fn;
}

int routeMsg(Msg m) {
    if ( m->header.target >= NUMBOX || m->header.cmd >= NUMCMDS) {
        return -1;
    }
    int cmd = m->header.cmd; 
    return MsgBox[m->header.target].cmds[cmd](m, cmd);
}


#ifdef DEBUG
void printStream(uint8_t *m, int len) {
    printf("[");
    for (int ii = 0; ii < len; ii++) { 
        printf("%02x ", (m)[ii]);
    }
    printf("]");
}
#endif 