CC=mipsel-linux-gnu-gcc
AS=mipsel-linux-gnu-gcc
CXX=mipsel-linux-gnu-gcc
STR=mipsel-linux-gnu-strip

LINKER_SCRIPT=ld.script

TARGET ?= a.out

BUILD_DIR ?= ./build
SRC_DIRS ?= ./

SRCS :=  \
	common.cc \
	lib_cpp/cpp.cc \
	lib/prng.c \
	lib/new_printf.c \
	lib/malloc.c \
	lib/memcmp.c \
	lib/stdlib.c \
	cioconnection.cc \
	main.cc

OBJS := $(SRCS:%=%.o)
DEPS := $(OBJS:.o=.d)

INC_DIRS := $(shell find $(SRC_DIRS) -type d)
LIB_INC_DIR := lib/ lib_cpp/
LIB_INC_FLAGS := $(addprefix -L ,$(LIB_INC_DIR))
INC_FLAGS := $(addprefix -I,$(INC_DIRS)) $(addprefix -isystem , $(LIB_INC_DIR))

ASFLAGS ?= $(INC_FLAGS) -EL -march=r3000 -mfp32 -mhard-float -fno-exceptions -fno-pic -mno-abicalls -ffreestanding -nostdinc 
CPPFLAGS ?= $(INC_FLAGS) -EL -march=r3000 -mfp32 -mhard-float -fno-exceptions -fno-pic -mno-abicalls -ffreestanding -nostdinc -MMD -MP 
CXXFLAGS ?= $(INC_FLAGS) -EL -march=r3000 -mfp32 -mhard-float -fno-exceptions -fno-pic -mno-abicalls -ffreestanding -nostdinc 
LDFLAGS ?= -EL -march=r3000 -mfp32 -mhard-float -fno-exceptions -fno-pic -mno-abicalls -ffreestanding -nostdinc -nostdlib 

$(TARGET): $(OBJS) setup.S.o
	$(CC) -T $(LINKER_SCRIPT) $(LIB_INC_FLAGS) -l mylibc -l mylibc++  setup.S.o $(OBJS) -o $@ $(LDFLAGS) 

# assembly
%.S.o: %.S
	$(MKDIR_P) $(dir $@)
	$(AS) $(ASFLAGS) -c $< -o $@

# c source
%.c.o: %.c
	$(MKDIR_P) $(dir $@)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

# c++ source
%.cc.o: %.cc
	$(MKDIR_P) $(dir $@)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@


.PHONY: clean

clean:
	$(RM) *.o *.d $(TARGET)

.PHONY: rom
rom:
	mipsel-linux-gnu-objcopy -O binary $(TARGET) $(TARGET).rom

-include $(DEPS)

MKDIR_P ?= mkdir -p


#all:
#mips-linux-gnu-gcc -EL -march=r3000 -mfp32 -fno-pic -mno-abicalls -ffreestanding -T ld.script setup.S echo.c -o echo
#	mips-linux-gnu-gcc -EL -march=r3000 -mfp32 -fno-pic -mno-abicalls -ffreestanding -nostartfiles -nostdlib -fno-builtin -T ld.script setup.S echo.c -o echo
#	mips-linux-gnu-objcopy -O binary echo

