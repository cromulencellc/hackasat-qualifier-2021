#include "common.h"
#include "pidcontroller.h"

extern int main( void );
extern void TimerInterrupt( void ) asm ("TimerInterrupt");

extern CIOConnection *g_iodata;

void ReadClock( uint32_t *seconds, uint32_t *microseconds )
{
	// uint32_t readAddress = IOBASE+CLOCK_CONTROL;
	// readAddress = 0xa1010000;
	*seconds = *((uint32_t*)(0xa1010000));
	*microseconds = *((uint32_t *)(0xa1010004));
}

void __attribute__((externally_visible)) SetupTimerInterrupt( void )
{
	uint32_t readAddress = IOBASE+CLOCK_CONTROL;
	readAddress = 0xa1010000+8;

	*((uint32_t*)(readAddress)) = 1000000;
	*((uint32_t*)(readAddress+4)) = 0x3; 
}


void EnableTimerInterrupt( void )
{
	__asm__
	__volatile__
	(	
	"mfc0 $a0, $12 \n"
        "ori $a0, $a0, 0x8001 \n"              /* IM7 and IEc */
        "mtc0 $a0, $12\n"
	: : : "%a0"
	);
}

void DisableTimerInterrupt( void )
{
	__asm__
	__volatile__
	(	
	"mfc0 $a0, $12 \n"
	"lui $a1, 0xffff\n"
	"ori $a1, 0x7fff\n"
        "and $a0, $a1 \n"              /* IM7 and IEc */
        "mtc0 $a0, $12\n"
	: : : "%a0", "%a1"
	);
}

volatile int waitFlag;


void TimerInterrupt( void )
{
	uint32_t readAddress = 0xa1010000+0xc;

	uint32_t value;
	//printf( ">\n" );
	//putc('>');
	// value = TestReadClock();
	// debug_log(LOG_PRIORITY_HIGH, "Timer fired: %u\n", value);
	// g_iodata->WriteData((uint8_t *)"Hell", 4);

	// if (waitFlag == 1) {

	// 	// debug_log(LOG_PRIORITY_HIGH, "wait flag is set\n");
	// 	waitFlag = 0;

	// }
	// waitFlag = 0;
	*((uint32_t*)(readAddress)) = 0x3;	// Keep interrupts enabled -- but clear this one

}



int main( void )
{

	// CTimeFrame timeframe;
	CIOConnection oConnection;
		
	g_iodata = &oConnection;
	int bytes_read;
	unsigned char tempBuffer[1024];
	uint32_t value;
	uint32_t last_time = 0;
	uint32_t current_time = 0;
	uint32_t time_delta_ms;

	// controller inputs and state history
	uint8_t leg1, leg2, leg3;
	uint8_t leg1_last = 0;
	uint8_t leg2_last = 0;
	uint8_t leg3_last = 0;
	uint8_t leg_touchdown;
	uint8_t leg_touchdown_enable;
	uint8_t radar_acquired;
	uint16_t radar_altitude;
	int16_t imu_velocity;

	// controller outputs
	uint8_t parachute_enable = 0;
	volatile uint8_t backshell_eject = 0;
	uint8_t deploy_legs = 0;
	uint8_t engine_cutoff = 1;
	uint16_t engine_thrust = 0;

	// controller inputs converting to floating point values
	float altitude;
	float velocity;

	// state variables

	uint8_t powered_descent_state = 0;
	uint8_t constant_velocity_state = 0;
	uint8_t touchdown_state = 0;

	PID *controller = 0;


	debug_log(LOG_PRIORITY_HIGH, "starting up\n");

	uint8_t buffer[3];

	uint8_t controller_state = 0;

	while ( 1 )
	{

		uint32_t x = 0;

		while (g_iodata->m_messageReceived == 0) {

			x = x + 1;
		}
		   
		if (g_iodata->m_messageReceived == 1 ) {

			// debug_log(LOG_PRIORITY_HIGH, "A whole message was received\n");

			imu_velocity = g_iodata->m_readBuffer[1] | g_iodata->m_readBuffer[0] << 8;
			radar_altitude = g_iodata->m_readBuffer[3] | g_iodata->m_readBuffer[2] << 8;

			// time_delta_ms = g_iodata->m_readBuffer[7] | g_iodata->m_readBuffer[6] << 8;
			// debug_log(LOG_PRIORITY_HIGH, "time_delta = %d\n", (int)time_delta_ms);

			leg1_last = leg1;
			leg2_last = leg2;
			leg3_last = leg3;

			leg1 = g_iodata->m_readBuffer[5] & 0x01;
			leg2 = (g_iodata->m_readBuffer[5] >> 1) & 0x01;
			leg3 = (g_iodata->m_readBuffer[5] >> 2) & 0x01;
			leg_touchdown_enable = (g_iodata->m_readBuffer[5] >> 3) & 0x01;
			radar_acquired = (g_iodata->m_readBuffer[5] >>4 ) & 0x01;

			velocity = (float) imu_velocity;
			altitude = (float) radar_altitude;

			// debug_log(LOG_PRIORITY_HIGH, "vel = %d\n", (int)velocity);

			// debug_log(LOG_PRIORITY_HIGH, "leg1=%d, leg2=%d, leg3=%d\n", leg1, leg2, leg3);
			
			// last_time = current_time;
			// current_time = ReadClock();

			// if ( last_time > 0 ) {

			// 	time_delta_ms = (current_time - last_time) / 10000;
			// 	// debug_log(LOG_PRIORITY_HIGH, "Time delta = %u ms\n", time_delta_ms);

			// }
			g_iodata->m_frameSync1Found = 0;
			g_iodata->m_frameSync2Found = 0;
			g_iodata->m_messageReceived = 0;

		}

		// update controller outputs based on the new inputs received
		if (controller_state == 0) {

				if (abs(velocity) < 81.0){

					controller_state = 1;
				}
		}
		else if (controller_state == 1) {

				backshell_eject = 1;
				deploy_legs = 1;
				engine_thrust = 80;
				engine_cutoff = 0;

				if (radar_acquired) {

					controller_state = 2;
				}
		}
		else if (controller_state == 2) {

				// PID mycontroller = PID(.004, .0001, .00000, velocity, -8.0, altitude, 40.0 );
				PID mycontroller = PID(.6, 0.005, 0.1, velocity, -8.0, altitude, 40.0 );

				controller = &mycontroller;

				controller_state = 3;
		}
		else if (controller_state == 3) {

				if (altitude <= 40.0 ) {

					controller_state = 4;
				
				}
				controller->update(altitude);

				value = (int)(controller->pid_output)+35;

				if (value < 0.0) 
					engine_thrust = 0;
				else
					engine_thrust = value;

				if (engine_thrust > 100 )
					engine_thrust = 100;

		}
		else if (controller_state == 4) {

			if ( velocity < -2.4)
				engine_thrust = 100;
			else
				engine_thrust = 40;

		}

		// enable this LOC to fix the bug in the PID controller
		// leg_touchdown = 0;

		if ( leg1 && leg1_last ) {

			leg_touchdown = 1;
		}

		if ( leg2 && leg2_last ) {

			leg_touchdown = 1;
		}

		if ( leg3 && leg3_last ) {

			leg_touchdown = 1;
		}

		if ( leg_touchdown_enable && leg_touchdown ) {

			engine_cutoff = 1;
		}

		buffer[0] = 0x5a;
		buffer[1] = ( backshell_eject | deploy_legs << 1 | engine_cutoff <<2 )  & 0xff;
		buffer[2] =  engine_thrust & 0xff;

		g_iodata->WriteData(buffer, 3);

	}
	
	return (0);
}
