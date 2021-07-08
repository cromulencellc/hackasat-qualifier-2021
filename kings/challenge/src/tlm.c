#include <tlm.h>
#include <msg.h>

static position_t pos; 

static int handleReq(Msg m, int cmd) {
    (void)cmd;
    routeMsg( createMessage(&pos, sizeof(pos), LINK_TARGET, LINK_TARGET) );
    return 1;
}

static int updateFn(Msg m, int cmd) { 
    (void)cmd;
    velocity_t vel;
    unpackMsgInto(m, (uint8_t *)&vel);
    pos.px += vel.vx * 0.01;
    pos.py += vel.vy * 0.01;
    pos.pz += vel.vz * 0.01;
    return 1;
}

void init_tlm(void) { 
    pos.px = 0.0;
    pos.py = 0.0;
    pos.pz = 0.0;
    registerMsgBox(handleReq, TLM_TARGET, TLM_REQ);
    registerMsgBox(updateFn, TLM_TARGET, TLM_UPDATE);
}