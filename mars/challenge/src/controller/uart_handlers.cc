#include "common.h"
#include "synovauartreg.h"
#include <stdlib.h>

#define READ_BUFFER_MAX_SIZE 1024

// char readBuffer[READ_BUFFER_MAX_SIZE];

// uint16_t readBufferCount = 0;
// uint16_t readBufferPointer = 0;



// extern void CIO_ReadInterrupt( void ) asm ("CIO_ReadInterrupt");



// inline void CIO_TurnOnInterrupts( void )
// {
// 	*(WRITE_CONTROL_REG) |= 0x1;
// 	*(READ_CONTROL_REG) |= 0x1;
// }

// inline void CIO_EnableReadInterrupt( void )
// {
// 	__asm__
//         __volatile__
//         (
//         "mfc0 $a0, $12 \n"
//         "ori $a0, $a0, 0x1001 \n"              /* IM4 and IEc */
//         "mtc0 $a0, $12\n"
//         : : : "%a0"
//         );
// }

// inline void CIO_DisableReadInterrupt( void )
// {
// 	 __asm__
//         __volatile__
//         (
//         "mfc0 $a0, $12 \n"
// 	"lui $a1, 0xffff\n"
//         "ori $a1, 0xefff\n"
//         "and $a0, $a1 \n"              /* IM4 and IEc */
//         "mtc0 $a0, $12\n"
//         : : : "%a0", "%a1"
//         );
// }

// inline void CIO_EnableWriteInterrupt( void )
// {
//         __asm__
//         __volatile__
//         (
//         "mfc0 $a0, $12 \n"
//         "ori $a0, $a0, 0x2001 \n"              /* IM5 and IEc */
//         "mtc0 $a0, $12\n"
//         : : : "%a0"
//         );
// }

// inline void CIO_DisableWriteInterrupt( void )
// {
//          __asm__
//         __volatile__
//         (
//         "mfc0 $a0, $12 \n"
// 	"lui $a1, 0xffff\n"
//         "ori $a1, 0xdfff\n"
//         "and $a0, $a1 \n"              /* IM5 and IEc */
//         "mtc0 $a0, $12\n"
//         : : : "%a0", "%a1"
//         );
// }

// void CIO_ReadInterrupt( void )
// {


// volatile uint32_t *READ_DATA_REG = (uint32_t*)(SYNOVA_UART2_ADDR + UART_READ_DATA);


//         debug_log(LOG_PRIORITY_HIGH, "Read interrupt fired\n");

// 	uint8_t in_byte = (*READ_DATA_REG);	// Read clears interrupt

//         if ( readBufferCount >= READ_BUFFER_MAX_SIZE ) {

//                 return;
//         }

//         readBuffer[readBufferPointer++] = in_byte;
//         readBufferCount++;

//         if (readBufferPointer >= READ_BUFFER_MAX_SIZE) {
//                 readBufferPointer = 0;
//         }


// }


