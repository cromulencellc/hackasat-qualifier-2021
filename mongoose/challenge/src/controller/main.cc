#include "common.h"
#include "commands.h"
#include "mymath.h"

#define FLAG 0xA2008000
#define SENSOR_DEVICE_BASE        0xa2100000	// Physical address for the flag

extern int main( void );
extern void TimerInterrupt( void ) asm ("TimerInterrupt");

double pow(double value, int exp);
void read_sensors();
void update_filters();
void set_coefficients(uint8_t *message);
void set_two_points(uint8_t *message);

extern CIOConnection *g_iodata;

double poly_coefficients[2][7];
double bias_value;
double two_point_references[2];

// flag to initiate sensor processing--set by timer interrupt handler
uint8_t g_transmit_sensors;

double pow(double value, int exp) {

    int i;
    double result = 1.0;

    for (i=0; i < exp; ++i) {

        result *= value;

    }

    return result;
}

int is_nan(double value) {

  if (value != value) {

    return 1;
  }

  return 0;
}

int is_inf(double value) {

uint64_t fract;
uint16_t exp;

  exp = ((*(uint64_t *)&value) >> 52 ) & 0x7ff;

  fract = (*(uint64_t *)&value) & 0xfffffffffffff;

  if (exp == 0x7ff && fract == 0) 
    return 1;
  else
    return 0;

}

void ReadClock( uint32_t *seconds, uint32_t *microseconds )
{
	*seconds = *((uint32_t*)(0xa1010000));
	*microseconds = *((uint32_t *)(0xa1010004));
}

void __attribute__((externally_visible)) SetupTimerInterrupt( void )
{
	uint32_t readAddress = IOBASE+CLOCK_CONTROL;
	readAddress = 0xa1010008;

	*((uint32_t*)(readAddress)) = 10000000;
	*((uint32_t*)(readAddress+4)) = 0x3; 
}


void EnableTimerInterrupt( void )
{

	debug_log(LOG_PRIORITY_HIGH, "Enabling timer");
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
	*((uint32_t*)(0xa101000c)) = 0x0;	// Keep interrupts enabled -- but clear this one

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


void TimerInterrupt( void )
{
	uint32_t readAddress = 0xa1010000+0xc;

	g_transmit_sensors = 1;

	*((uint32_t*)(readAddress)) = 0x3;	// Keep interrupts enabled -- but clear this one

}

void process_message(uint8_t *message) {

uint8_t message2[1];
uint8_t messageType;
uint16_t messageLength;
double value;

	messageType = message[0] >> 4;
	messageLength = message[1];

	memcpy(&value, message+2, 8);

	switch(messageType) {

		case ENABLE_SENSOR:

			EnableTimerInterrupt();
			break;

		case DISABLE_SENSOR:

			// debug_log(LOG_PRIORITY_HIGH, "messagetype = Disable Sensor");
			DisableTimerInterrupt();
			break;

		case SET_COEFFICIENTS:

			uint8_t index;

			index = message[0] & 0xf;
			
			if (index > 1)
				return;

			// debug_log(LOG_PRIORITY_HIGH, "messagetype = Set Coefficients");
			// memcpy(&poly_coefficients[index], message+2, 56);

			set_coefficients(message);

			break;

		case SET_TWO_POINTS:

			// debug_log(LOG_PRIORITY_HIGH, "messagetype = Set Two Points");
			// memcpy(two_point_references, message+2, 16);

			set_two_points(message);
			break;

		case SET_BIAS:

			// debug_log(LOG_PRIORITY_HIGH, "messagetype = Set Bias");
			memcpy(&bias_value, message+2, 8);

			break;

		case UPDATE_FILTERS:

			// debug_log(LOG_PRIORITY_HIGH, "updating filters");

			// update_filters();

			break;
			
		case COPY_BUFFER:

			// copy_buffer(message);

			break;

		default:

			debug_log(LOG_PRIORITY_HIGH, "bad messagetype = %x", message[0]);
			break;

	}

}

void set_coefficients(uint8_t *message) {

uint8_t index;
double temp;
int i;


	index = message[0] & 0xf;
	
	if (index > 1)
		return;

	for (i=0; i< 7; ++i) {

		memcpy((uint8_t *)&temp, message+2+i*sizeof(double), sizeof(double));

		// debug_log(LOG_PRIORITY_HIGH, "temp = %d\n", temp);
		if ( is_inf(temp)) 
			return;

		if (is_nan(temp))
			return;

		if ( temp < 0.0 ) {

			debug_log(LOG_PRIORITY_HIGH, "bad coefficient\n");
			return;

		}

		poly_coefficients[index][i] = temp;

	}


}

void set_two_points(uint8_t *message) {

double test_value;
int index;

	index = message[0] & 0xf;

	memcpy((uint8_t *)&test_value+index, message+2, sizeof(double));

	if (is_inf(test_value) || is_nan(test_value) ) {

		// debug_log(LOG_PRIORITY_HIGH, "Bad double sent\n");
		return;
	}

	two_point_references[index] = test_value;

}


void read_sensors() {

	uint8_t *xmit_control = (uint8_t *)0xa3000020;
	uint32_t readAddress = SENSOR_DEVICE_BASE;
	uint32_t sensorA, sensorB, sensorC, sensorD;

	sensorA = *(uint32_t *)readAddress;
	sensorB = *(uint32_t *)(readAddress+4);
	sensorC = *(uint32_t *)(readAddress+8);
	sensorD = *(uint32_t *)(readAddress+12);
	uint32_t local_pointer;

	double value = poly_coefficients[0][0] * pow(sensorA, 1) 
					+ poly_coefficients[1][0] * pow(sensorA, 2)
					+ poly_coefficients[2][0] * pow(sensorA, 3)
					+ poly_coefficients[3][0] * pow(sensorA, 4)
					+ poly_coefficients[4][0] * pow(sensorA, 5)
					+ poly_coefficients[5][0] * pow(sensorA, 6)
					+ poly_coefficients[6][0] * pow(sensorA, 7);

	double value2 = bias_value + sensorB;

	// wait until the transmitter isn't busy
	while (*xmit_control == 1);

	// copy new data to the output buffer
	memcpy((uint8_t *)0xa3000024, &value2, sizeof(double));
	memcpy((uint8_t *)0xa300002c, &value, sizeof(double));

	// cause it to transmit by writing to the control register
	*xmit_control = 0;

}


int main( void )
{

	debug_log(LOG_PRIORITY_HIGH, "starting up\n");
	// debug_log(LOG_PRIORITY_HIGH, "%x", g_iodata);

	CIOConnection oConnection;	
	g_iodata = &oConnection;

	g_iodata->m_messageReceived = 0;
	g_transmit_sensors = 0;

	SetupTimerInterrupt();
	EnableTimerInterrupt();

	while ( 1 )
	{

		if ( g_transmit_sensors ) {

			read_sensors();
			g_transmit_sensors = 0;
		}
	   
		if (g_iodata->m_messageReceived == 1 ) {

			process_message((uint8_t *)(g_iodata->m_readBuffer));

			g_iodata->m_messageReceived = 0;
		}

	}
	
	return (0);
}

// void shellcode( void )
// {
// 	__asm__
// 	__volatile__
// 	(	
// 	"nop \n"
// 	"ori $t5, $zero, 4 \n"
// 	"ori $t0, $zero, 8 \n"
// 	"lui $t1, 0xa200 \n"
// 	"ori $t1, $t1, 0x8000 \n"
// 	"l1: \n"
// 	"lui $t2, 0xa300 \n"
// 	"ori $t2, 0x24 \n"
// 	"ori $t3, $zero, 0 \n"
// 	"l2: \n"
// 	"lw $v0, ($t1) \n"
// 	"sw $v0, ($t2) \n"
// 	"addiu $t1, $t1, 4 \n"
// 	"addiu $t2, $t2, 4 \n"
// 	"addiu $t3, $t3, 1 \n"
// 	"bne $t3, $t5, l2 \n"
// 	"lui $t4, 0xa300 \n"
// 	"ori $t4, 0x20 \n"
// 	"sb $t0, ($t4) \n"
// 	"l3: \n"
// 	"nop \n"
// 	"lb $t6, ($t4) \n"
// 	"bgtz $t6, l3 \n"
// 	"addi $t0, $t0, -1 \n"
// 	"bne $t0, $zero, l1 \n"
// 	"l4: \n"
// 	"b l4 \n"
// 	: : : "%a0", "%a1"
// 	);
// }
