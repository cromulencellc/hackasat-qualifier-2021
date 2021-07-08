#pragma once
#include <common.h> 

void init_msgs(void);

typedef struct msg *Msg;
Msg createMessage(void * payload, uint32_t length, int id, int cmd);
int unpackMsg(Msg m, uint8_t **payload);
int unpackMsgInto(Msg m, uint8_t * payload);
int recvMsg(Msg *m);

typedef int (*MsgBoxFn)(Msg m, int cmd);
void registerMsgBox(MsgBoxFn fn, int id, int cmd);
int routeMsg(Msg m); 

#ifdef DEBUG
void printStream(uint8_t *m, int len);
#endif 