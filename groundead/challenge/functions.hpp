#include <stdio.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <fcntl.h> // for open
#include <unistd.h> // for close
#include <threads.h>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <queue>

char* flag = getenv("FLAG");

// Print out the value of a field. For example, the apid value is desired to be
// printed out, the call would be -> printDebug("apid", apid);
void printDebug(std::string thingToPrint, uint32_t thingValue)
{
  std::stringstream ssTmp;
  std::string strTmp;
  ssTmp.str(std::string());
  strTmp.clear();
  ssTmp << thingValue;
  strTmp = ssTmp.str();
  std::cout << thingToPrint.c_str() << ": " << std::hex << std::setw(8) << std::setfill('0') << (((uint32_t) thingValue ) & 0xffffffff) << std::endl;
}

void printIntroArt(void)
{
std::cout << "" << std::endl << std::endl << std::endl;
std::cout << "     .-.                                                         -----------" << std::endl;
std::cout << "   (;;;)                                                        /            '" << std::endl;
std::cout << "    |_|                                  ,-------,-|           |C>      )    |" << std::endl;
std::cout << "      ' _.--l--._                       '      ,','|          /    || ,'     |" << std::endl;
std::cout << "     .      |     `.                   '-----,','  |         (,    ||        ," << std::endl;
std::cout << "   .` `.    |    .` `.                 |     ||    |           -- ||||      |" << std::endl;
std::cout << " .`     `   |  .`     `.               |     ||    |           |||||||     _|" << std::endl;
std::cout << "' __      `.|.`      __ `              |     ||    |______      `````|____/ |" << std::endl;
std::cout << "|   ''--._  V  _.--''   |              |     ||    |     ,|         _/_____/ |" << std::endl;
std::cout << "|        _ ( ) _        |              |     ||  ,'    ,' |        /          |" << std::endl;
std::cout << "| __..--'   ^   '--..__ | _           '|     ||,'    ,'   |       |            |" << std::endl;
std::cout << "'         .`|`.         '-.)        ,  |_____|'    ,'     |       /           | |" << std::endl;
std::cout << " `.     .`  |  `.     .`           , _____________,'      ,',_____|      |    | |" << std::endl;
std::cout << "   `. .`    |    `. .`             |             |     ,','      |      |    | |" << std::endl;
std::cout << "     `._    |    _.`|       -------|             |   ,','    ____|_____/    /  |" << std::endl;
std::cout << "         `--l--`  | |     ;        |             | ,','  /  |              /   |" << std::endl;
std::cout << "                  | |    ;         |_____________|','    |   -------------/   |" << std::endl;
std::cout << "               ---| |-------.                      |===========,'" << std::endl;
std::cout << "             /    ..       / |                                   " << std::endl;          
std::cout << "            --------------   |" << std::endl;
std::cout << "           |              | /" << std::endl;
std::cout << "           |              |/" << std::endl;
std::cout << "            --------------" << std::endl;
}

void printIntroText(void)
{
    printf("\n");
    printf("\n");
    printf("Ground Station ONLINE\n\n");
    printf(">");

    fflush(stdout);
}

// This function implementes the timer used to limit the run of this challenge. 
void *startTimer(void *thr_id) 
{
    sleep(180);
    printf("Time is up. Goodbye.\n");
    fflush(stdout);

    thrd_exit(EXIT_SUCCESS);
}
