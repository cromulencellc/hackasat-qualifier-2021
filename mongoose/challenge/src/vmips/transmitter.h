/* Declarations to support the VMIPS clock device.
   Copyright 2003 Paul Twohey.

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

#ifndef _TRANSMITTERDEV_H_
#define _TRANSMITTERDEV_H_

#define TRANSMITTER_BASE           0x03000020

#include "devicemap.h"
#include "deviceexc.h"
#include "devreg.h"
#include "task.h"
#include <new>

// class vmips;

// Instruction count clock device
class TransmitterDevice : public DeviceMap
{
public:
	/* Create a new clock device that uses CLOCK as its time source and
	   which reports interrupts on irq IRQ at the regular interval
	   FREQUENCY_NS nanoseconds. */
	TransmitterDevice();

	/* Destroy the clock device and cancel any tasks it may have
	   waiting to execute on CLOCK. */
	virtual ~TransmitterDevice();

	virtual uint32 fetch_word(uint32 offset, int mode, DeviceExc *client);
	virtual uint8 fetch_byte(uint32 offset, int mode, DeviceExc *client);
	virtual void store_word(uint32 offset, uint32 data, DeviceExc *client);
	virtual void store_byte(uint32 offset, uint8 data, DeviceExc *client);

	/* Return a description of this device. */
	virtual const char *descriptor_str() const;

	virtual void timer_tick( void );

protected:

	uint8 xmit_buffer[16];
	uint8 xmit_byte_count;
	uint32 tick_count;
	uint32 control_word;

};

#endif /*  */
