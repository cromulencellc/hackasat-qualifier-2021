#include <msg.h>
#include <stdlib.h>
#include <unistd.h>

int sendData (void *data, int length) {
    int total = 0;
    ssize_t sent = 0;
    while (total < length) {
        sent = write(1, (char*)data + total, length - total);
        if (sent < 0) {
            exit(1);
        }
        total += sent;
    }
    return total ;
}

int recvData(void *data, int length) {
    int total = 0;
    ssize_t recvd = 0;
    while (total < length) {
        recvd = read(0, (char *)data + total, length - total);
        if (recvd < 0) {
            exit(1);
        }
        total += recvd;
    }
    return total; 
}