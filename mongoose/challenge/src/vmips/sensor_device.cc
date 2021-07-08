/* Implementation of VMIPS clock device.
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

#include "sensor_device.h"
#include "devreg.h"
#include "vmips.h"

#include <cassert>
#include <cstddef>
#include <stdio.h>
#include <stdlib.h>


SensorDevice::SensorDevice( )
	: DeviceMap(16)
	 
{

	sensorA = 0;
	sensorB = 1;
	sensorC = 3;
	sensorD = 4;
}

SensorDevice::~SensorDevice()
{

}

void SensorDevice::step()
{

	++sensorA;
	sensorB += 2;
	sensorC += 4;
	sensorD += 10;

}

uint32 SensorDevice::fetch_word( uint32 offset, int mode, DeviceExc *client )
{

	switch( offset / 4 ) {
	case 0:	
		// fprintf(stderr, "SensorA being read\n");

		return sensorA;
		break;
	case 1:		
		// fprintf(stderr, "SensorB being read\n");

		return sensorB;
		break;
	case 2:
		// fprintf(stderr, "SensorC being read\n");

		return sensorC;
		break;
	case 3:	
		// fprintf(stderr, "SensorD being read\n");

		return sensorD;
	default:
		assert( ! "reached" );
		return 0;
	}
}

void SensorDevice::store_word( uint32 offset, uint32 data, DeviceExc *client )
{

	switch( offset / 4 ) {
	case 0:	// timer_hi
		// timer_hi = data;
		break;
	case 1: // timer_lo
		// timer_lo = data;
		break;
	case 2: // counter
		// timer_set_counter = data;
		// timer_counter = timer_set_counter;
		break;
	case 3:		// control word
		// interrupt_enabled = data & 0x1;
		// if ( interrupt_set && data & 0x2 )
		// {
			// interrupt_set = false;
			// deassertInt( irq );
		// }

		// timer_divider = (data >> 2) & 0x3;

		return;
	default:
		assert( ! "reached" );
	}
}

const char *SensorDevice::descriptor_str() const
{
	return "Sensor device";
}
