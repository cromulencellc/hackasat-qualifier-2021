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

#include "transmitter.h"
#include "devreg.h"
#include "vmips.h"
#include "mapper.h"

#include <cassert>
#include <cstddef>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

TransmitterDevice::TransmitterDevice( )
	: DeviceMap(20)
{
	control_word = 0;
	xmit_byte_count = 0;
	tick_count = 0;
}

TransmitterDevice::~TransmitterDevice()
{

}

void TransmitterDevice::timer_tick()
{

	if (control_word != 0 ) {

		++tick_count;

		if ( tick_count > 1000 ) {

			write(1, xmit_buffer+xmit_byte_count, 1);

			xmit_byte_count++;

			if (xmit_byte_count >= 16) {

				control_word = 0;
				xmit_byte_count = 0;
				tick_count = 0;
			}
		}



	}
}

uint32 TransmitterDevice::fetch_word( uint32 offset, int mode, DeviceExc *client )
{

	// printf("read word at offset = %d\n", offset);

	if (offset > 3) {

		return *(uint32 *)(xmit_buffer+offset-4);

	}
	else {

		return control_word;
	}

}

uint8 TransmitterDevice::fetch_byte( uint32 offset, int mode, DeviceExc *client )
{

	// printf("read byte at offset = %d\n", offset);

	if (offset > 3) {

		return xmit_buffer[offset - 4];
	}
	else {

		return control_word & 0xff;
	}

	
}

void TransmitterDevice::store_word( uint32 offset, uint32 data, DeviceExc *client )
{

	// fprintf(stderr, "write offset = %d\n", offset);

	if (offset > 3) {

		*(uint32 *)(xmit_buffer+offset-4) = data;

	}
	else {

		control_word = 1;
		// write(1, xmit_buffer, 16);

	}

}

void TransmitterDevice::store_byte( uint32 offset, uint8 data, DeviceExc *client )
{

	// fprintf(stderr, "write byte at offset = %d\n", offset);

	if (offset > 3) {

		xmit_buffer[offset-4] = data;

	}
	else {

		// fprintf(stderr, "time to transmit\n");

		control_word = 1;
		// write(1, xmit_buffer, 16);
	}

}

const char *TransmitterDevice::descriptor_str() const
{
	return "Transmitter device";
}
