/* Definitions for stub floating-point coprocessor.
   Copyright 2004, 2009 Brian R. Gaeke.

This file is part of VMIPS.

VMIPS is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

VMIPS is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along
with VMIPS; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.  */

#ifndef _FPU_H_
#define _FPU_H_

#include "types.h"

typedef union fpreg {

                float f;
                int32 i;
        } fpregType;

class CPU;

class FPU
{
        CPU *cpu;
        uint32 reg[32];

        fpregType regs[32];
        uint8 cc;

public:
	FPU (CPU *m) : cpu (m) { }
        void cpone_emulate (uint32 instr, uint32 pc);
        void bc1f_emulate(uint32 instr, uint32 pc);
        void mtc1_emulate (uint32 instr, uint32 pc);
        void mfc1_emulate (uint32 instr, uint32 pc);
        void cvt_s_emulate (uint32 instr, uint32 pc);
        void cvt_d_emulate (uint32 instr, uint32 pc);
        void cvt_w_emulate (uint32 instr, uint32 pc);
        void div_emulate (uint32 instr, uint32 pc);
        void trunc_emulate (uint32 instr, uint32 pc);
        void add_emulate(uint32 instr, uint32 pc);
        void sub_emulate(uint32 instr, uint32 pc);
        void cfc1_emulate(uint32 instr, uint32 pc);
        void ctc1_emulate(uint32 instr, uint32 pc);
        void mul_emulate(uint32 instr, uint32 pc);
        void equal_emulate(uint32 instr, uint32 pc); 
        void lt_emulate(uint32 instr, uint32 pc);
        void le_emulate(uint32 instr, uint32 pc);
        uint32 read_reg (uint16 regno);
	void write_reg (uint16 regno, uint32 word);
        void mov_emulate(uint32 instr, uint32 pc);
        void neg_emulate(uint32 instr, uint32 pc);
        void movf_emulate(uint32 instr, uint32 pc); 
        void movz_emulate(uint32 instr, uint32 pc); 
        void movn_emulate(uint32 instr, uint32 pc);

        static uint16 ft(const uint32 i) { return (i >> 16) & 0x01f; }
	static uint16 fs(const uint32 i) { return (i >> 11) & 0x01f; }
	static uint16 fd(const uint32 i) { return (i >> 6) & 0x01f; }
        static uint8 ccbit(const uint32 i) { return (i >> 18) & 0x7; }
        static uint8 fmt(const uint32 i) { return (i >>21 ) & 0x1f;}
};

#endif /* _FPU_H_ */
