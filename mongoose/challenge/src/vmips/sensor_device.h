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

#ifndef _SENSORDEV_H_
#define _SENSORDEV_H_

#include "devicemap.h"
#include "devreg.h"
#include "task.h"
#include <new>

class vmips;

#define SENSOR_DEVICE_BASE        0x02100000	// Physical address for the flag

// Instruction count clock device
class SensorDevice : public DeviceMap
{
public:
	/* Create a new clock device that uses CLOCK as its time source and
	   which reports interrupts on irq IRQ at the regular interval
	   FREQUENCY_NS nanoseconds. */
	SensorDevice();

	/* Destroy the clock device and cancel any tasks it may have
	   waiting to execute on CLOCK. */
	virtual ~SensorDevice();

	virtual uint32 fetch_word(uint32 offset, int mode, DeviceExc *client);
	virtual void store_word(uint32 offset, uint32 data, DeviceExc *client);

	/* Return a description of this device. */
	virtual const char *descriptor_str() const;

	virtual void step( void );

protected:

	uint32 sensorA;
	uint32 sensorB;
	uint32 sensorC;
	uint32 sensorD;

	double sensor_reading;
};

#endif /*  */
