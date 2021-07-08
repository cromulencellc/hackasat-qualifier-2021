/* Stubs for floating-point coprocessor.
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

#include "fpu.h"
#include "cpu.h"
#include "vmips.h"
#include "excnames.h"
#include "stub-dis.h"
#include <cstdio>
#include <string.h>
#include <math.h>

void FPU::cpone_emulate (uint32 instr, uint32 pc)
{

        // machine->disasm->disassemble (pc, instr);

    	uint16 rs = CPU::rs (instr);

	if (rs > 15) {
		switch (CPU::funct (instr)) {
            case 0: add_emulate(instr, pc); break;
            case 1: sub_emulate(instr, pc); break;
            case 2: mul_emulate(instr, pc); break;    
            case 3: div_emulate(instr, pc); break;
            case 6: mov_emulate(instr, pc); break;
            case 7: neg_emulate(instr, pc); break;
            case 13: trunc_emulate(instr, pc); break;
            case 17: movf_emulate(instr, pc); break;
            case 18: movz_emulate(instr, pc); break;
            case 19: movn_emulate(instr, pc); break;
            case 32: cvt_s_emulate(instr, pc); break;
            case 33: cvt_d_emulate(instr, pc); break;
            case 36: cvt_w_emulate(instr, pc); break;
            // case 49: unequal_emulate(instr, pc); break;
            case 50: equal_emulate(instr, pc); break;
            case 60: lt_emulate(instr, pc); break;
            case 62: le_emulate(instr, pc); break;

		default: 
            fprintf (stderr, "FPU instruction %x not implemented at pc=0x%x:\n",
            instr, pc);
            machine->disasm->disassemble (pc, instr);
            cpu->exception (RI, ANY, 0); 
            break;
		}
	} else {
		switch (rs) {
		case 0: mfc1_emulate(instr, pc); break;
        case 2: cfc1_emulate(instr, pc); break;
		case 4: mtc1_emulate(instr, pc); break;
        case 6: ctc1_emulate(instr, pc); break;
        case 8: bc1f_emulate(instr, pc); break;
		default: 
        
            fprintf (stderr, "FPU instruction %x not implemented at pc=0x%x:\n",
            instr, pc);
            machine->disasm->disassemble (pc, instr);
            cpu->exception (CpU, ANY, 0); 
            break;
		}
	}

}

void FPU::mov_emulate(uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);    
    uint16_t fd = FPU::fd(instr);


    uint8_t fmt = FPU::fmt(instr);

    // regs[fd].f = regs[fs].f * regs[ft].f;

    double value;

    if (fmt == 0x10 ) {

        reg[fd] = reg[fs];

    }
    else if (fmt == 0x11) {

        reg[fd+1] = reg[fs+1];

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }

}

void FPU::neg_emulate(uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);    
    uint16_t fd = FPU::fd(instr);
    uint8_t fmt = FPU::fmt(instr);

    // regs[fd].f = regs[fs].f * regs[ft].f;

    double value;

    if (fmt == 0x10 ) {

        regs[fd].f = - regs[fs].f;

    }
    else if (fmt == 0x11) {

        value = - *(double *)&regs[fs].i;
        *(double *)&regs[fd].i = value;
        // fprintf(stderr, "value = %lf\n", value);

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }
}

void FPU::movf_emulate(uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);    
    uint16_t fd = FPU::fd(instr);
    uint8_t ccbit = FPU::ccbit(instr);

    uint8_t ccvalue = (instr >> 16) & 0x1;

    uint8_t flag = (cc >> ccbit) & 0x01;

    if ( flag == ccvalue) {

        reg[fd] = reg[fs];
    }
}

void FPU::movz_emulate(uint32 instr, uint32 pc) {

        fprintf (stderr, "FPU instruction %u not implemented for format %u:\n",
        instr, pc);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

}
    
void FPU::movn_emulate(uint32 instr, uint32 pc) {

        fprintf (stderr, "FPU instruction %u not implemented for format %u:\n",
        instr, pc);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

}


void FPU::bc1f_emulate(uint32 instr, uint32 pc) {


    // fprintf(stderr, "%X\n", instr);

    uint8_t ccbit = (instr >> 18) & 0x7;
    uint8_t ccvalue = (instr >> 16) & 0x1;

    uint8_t flag = (cc >> ccbit) & 0x01;

    // fprintf(stderr, "ccbit = %x and flag = %x\n", ccbit, flag);

    if ( flag == ccvalue )

        cpu->branch(instr, pc);


}

void FPU::lt_emulate(uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);    
    uint16 ft = FPU::ft(instr);
    uint8_t fmt = FPU::fmt(instr);
    uint8_t fd = FPU::fd(instr);

    uint8_t ccbit = fd >> 2;
    uint8_t mask = ~(uint8_t)pow(2, ccbit);

    uint8_t result = 0;

    if (fmt == 0x10 ) {

            if ( regs[fs].f < regs[ft].f) {
                result = 1;
            }
    }
    else if (fmt == 0x11) {

        if ( *(double *)&regs[fs].i < *(double *)&regs[ft].i) {

            result = 1;
        }

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }

    FPU::cc &= mask;
    FPU::cc |= result << ccbit;

    // fprintf(stderr, "CC = %x\n", FPU::cc);

}


void FPU::le_emulate(uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16 ft = FPU::ft(instr);
    uint8_t fmt = FPU::fmt(instr);
    uint8_t fd = FPU::fd(instr);

    uint8_t ccbit = fd >> 2;
    uint8_t mask = ~(uint8_t)pow(2, ccbit);

    uint8_t result = 0;

    if (fmt == 0x10 ) {

            if ( regs[fs].f <= regs[ft].f) {
                result = 1;
            }
    }
    else if (fmt == 0x11) {

        if ( *(double *)&regs[fs].i <= *(double *)&regs[ft].i) {

            result = 1;
        }

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }

    FPU::cc &= mask;
    FPU::cc |= result << ccbit;

    // fprintf(stderr, "CC = %x\n", FPU::cc);

}

void FPU::equal_emulate(uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16 ft = FPU::ft(instr);
    uint8_t fmt = FPU::fmt(instr);
    uint8_t fd = FPU::fd(instr);

    uint8_t ccbit = fd >> 2;
    uint8_t mask = ~(uint8_t)pow(2, ccbit);

    uint8_t result = 0;

    if (fmt == 0x10 ) {

            if ( regs[fs].f == regs[ft].f) {
                result = 1;
            }
    }
    else if (fmt == 0x11) {

        if ( *(double *)&regs[fs].i == *(double *)&regs[ft].i) {

            result = 1;
        }

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }

    FPU::cc &= mask;
    FPU::cc |= result << ccbit;

    // fprintf(stderr, "CC = %x\n", FPU::cc);

}



void FPU::mul_emulate(uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16 ft = FPU::ft(instr);
    uint16_t fd = FPU::fd(instr);
    uint8_t fmt = FPU::fmt(instr);

    // regs[fd].f = regs[fs].f * regs[ft].f;

    double value;

    if (fmt == 0x10 ) {

        regs[fd].f = regs[fs].f * regs[ft].f;

    }
    else if (fmt == 0x11) {

        value = *(double *)&regs[fs].i * *(double *)&regs[ft].i;

        // fprintf(stderr, "value = %lf\n", value);
        *(double *)&regs[fd].i = value;

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }

}


void FPU::cfc1_emulate(uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16_t rt = CPU::rt(instr);

    cpu->put_reg(rt, regs[fs].i);

    // fprintf(stderr, "copying from %d and to %d\n", rt, fs);

}

void FPU::ctc1_emulate(uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16_t rt = CPU::rt(instr);

    FPU::write_reg (fs, cpu->get_reg (CPU::rt (instr)));

}
void FPU::div_emulate( uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16 ft = FPU::ft(instr);
    uint16_t fd = FPU::fd(instr);
    uint8_t fmt = FPU::fmt(instr);

    // regs[fd].f = regs[fs].f / regs[ft].f;

    double value;

    if (fmt == 0x10 ) {

        regs[fd].f = regs[fs].f / regs[ft].f;

    }
    else if (fmt == 0x11) {

        value = *(double *)&regs[fs].i / *(double *)&regs[ft].i;

        // fprintf(stderr, "value = %lf\n", value);
        *(double *)&regs[fd].i = value;

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }
};

void FPU::add_emulate(uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16_t fd = FPU::fd(instr);
    uint16_t ft = FPU::ft(instr);

    uint8_t fmt = FPU::fmt(instr);

    double value;

    if (fmt == 0x10 ) {

        regs[fd].f = regs[fs].f + regs[ft].f;

    }
    else if (fmt == 0x11) {

        value = *(double *)&regs[fs].i + *(double *)&regs[ft].i;

        // fprintf(stderr, "value = %lf\n", value);
        *(double *)&regs[fd].i = value;

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }
}

void FPU::sub_emulate(uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16_t fd = FPU::fd(instr);
    uint16_t ft = FPU::ft(instr);
    uint8_t fmt = FPU::fmt(instr);

    // regs[fd].f = regs[fs].f - regs[ft].f;

    double value;

    if (fmt == 0x10 ) {

        regs[fd].f = regs[fs].f - regs[ft].f;

    }
    else if (fmt == 0x11) {

        value = *(double *)&regs[fs].i - *(double *)&regs[ft].i;

        // fprintf(stderr, "value = %lf\n", value);
        *(double *)&regs[fd].i = value;

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }

}

void FPU::trunc_emulate( uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16_t fd = FPU::fd(instr);

    regs[fd].i = (uint32_t)regs[fs].f;

};

void FPU::mfc1_emulate( uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16_t ft = FPU::ft(instr);

    cpu->put_reg(ft, regs[fs].i);

};

void FPU::mtc1_emulate( uint32 instr, uint32 pc) {

	FPU::write_reg (CPU::rd (instr), cpu->get_reg (CPU::rt (instr)));

   //  fprintf(stderr, "regs = %f\n", regs[FPU::fd(instr)].f);

};

void FPU::cvt_s_emulate( uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16_t fd = FPU::fd(instr);
   
    uint8_t fmt = FPU::fmt(instr);

   //  fprintf(stderr, "fmt = %x\n", fmt);

    if (fmt == 0x14) {

        regs[fd].f = (float)regs[fs].i;

    }
    else if ( fmt == 0x11) {

        regs[fd].f = (float)*(double *)&regs[fs].i;

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }
      //   fprintf(stderr, "regs = %f\n", regs[fd].f);


}

void FPU::cvt_d_emulate( uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16_t fd = FPU::fd(instr);
    uint8_t fmt = FPU::fmt(instr);

    // fprintf(stderr, "fmt = %x\n", fmt);

    if (fmt == 0x14 ) {

        double value = (double)(regs[fs].i);
        memcpy(&regs[fd].i, &value, 8);

    }
    else if ( fmt == 0x10 ) {

        double value = (double)(regs[fs].f);
        // memcpy(&regs[fd].i, &value, 8);

        *(double *)&regs[fd].i = value;

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }
    // fprintf(stderr, "reg = %lf\n", *(double *)&regs[fd]);

}

void FPU::cvt_w_emulate( uint32 instr, uint32 pc) {

    uint16_t fs = FPU::fs(instr);
    uint16_t fd = FPU::fd(instr);
    uint8_t fmt = FPU::fmt(instr);


    if (fmt == 0x10 ) {

        regs[fd].i = (int32_t)regs[fs].f;

    }
    else if (fmt == 0x11 ) {


        regs[fd].i = (int32_t)*(double *)&regs[fs].i;

    }
    else {

        fprintf (stderr, "FPU instruction %x not implemented for format %x:\n",
        instr, fmt);
        machine->disasm->disassemble (pc, instr);
        cpu->exception (CpU, ANY, 0); 

    }

    // fprintf(stderr, "reg.f = %f   reg.i = %u\n", regs[fd].f, regs[fd].i);


}

uint32 FPU::read_reg (uint16 regno)
{

    // fprintf(stderr, "ReadReg: value read = %d from regno = %d\n", regs[regno].i, regno);
    return regs[regno].i;

}

void FPU::write_reg (uint16 regno, uint32 word)
{

    // reg[regno] = word;

    regs[regno].i = word;

    // fprintf(stderr, "WriteReg: value written = %d to regno = %d\n", word, regno);
    // fprintf(stderr, "reg.f = %f   reg.i = %u\n", regs[regno].f, regs[regno].i);

}
