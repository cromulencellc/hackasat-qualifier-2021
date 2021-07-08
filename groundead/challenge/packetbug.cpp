#include "Queue.hpp"
#include "functions.hpp"
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

#define PORT 12345
#define SA struct sockaddr

// #define NUM_THREADS 2
#define NUM_THREADS 3

#define QUEUE_SIZE 2048

uint32_t pktPrimHdrBitDefn(uint32_t start, uint32_t end)
{
  return ((start << 16) | (end - start + 1));
}

uint32_t PVN = pktPrimHdrBitDefn((uint32_t)13,(uint32_t)15);
uint32_t PKT_TYPE = pktPrimHdrBitDefn((uint32_t)12,(uint32_t)12);
uint32_t SEC_HDR_FLAG = pktPrimHdrBitDefn((uint32_t)11,(uint32_t)11);
uint32_t APID = pktPrimHdrBitDefn((uint32_t)0,(uint32_t)10);
uint32_t SEQ_FLAGS = pktPrimHdrBitDefn((uint32_t)14,(uint32_t)15);
uint32_t PKT_SEQ_CNT_OR_PKT_NAME = pktPrimHdrBitDefn((uint32_t)0,(uint32_t)13);

uint32_t readPktPrimHdrBitField(uint32_t bitField, uint32_t val)
{
  const uint32_t width = bitField & 0xffff;
  const uint32_t bitNum = bitField >> 16;
  val >>= bitNum;
  val &= ((1 << width) - 1);
  return val;
}

char char2int(char input)
{
    if (input >= '0' && input <= '9')
        return input - '0';
    if (input >= 'A' && input <= 'F')
        return input - 'A' + 10;
    if (input >= 'a' && input <= 'f')
        return input - 'a' + 10;

    throw std::runtime_error("Incorrect symbol in hex string");
};

std::string hex2str(std::string hex)
{
    std::string out;
    out.resize(hex.size() / 2 + hex.size() % 2);

    std::string::iterator it = hex.begin();
    std::string::iterator out_it = out.begin();
    if (hex.size() % 2 != 0) 
    {
        *out_it++ = char(char2int(*it++));
    }

    for (; it < hex.end() - 1; it++) {
        *out_it++ = char2int(*it++) << 4 | char2int(*it);
    };

    return out;
}

// Declare an instance of the Queue class. 
Queue q;

// This function simulates the sending of CCSDS packets from the ground station to the 
// satellite. Bytes are read in and assembled and if they the form a test telemetry
// command packet, they are added to the Queue class to be sent to the satellite. 
void *getSatellitePacketBytes(void *thr_id) 
{
    uint8_t val = 0;

    char buffer[256];
    bzero(buffer, sizeof(buffer));

    std::stringstream ssTmp;
    std::string strTmp;
    ssTmp.str(std::string());
    strTmp.clear();

    std::string dlpreamble = "1acffc1d";

    std::stringstream ssTotalPacket;
    ssTotalPacket.str(std::string());

    while(true)
    {   
        int n = 0;

        while (n <= 1)
        {
            n = read(0, buffer, 256);
        }

        for (int i = 0; i < n; i++)
        {
          ssTmp << std::hex << std::setw(2) << std::setfill('0') << (((uint8_t) buffer[i] ) & 0xff);
        }

        std::string var;
        uint32_t telemType = 0;
        std::string telemTypeStr;

        try
        {    
            var = hex2str(ssTmp.str().c_str());
            telemType = strtoul(var.c_str(), NULL, 16);              
            telemTypeStr = var.substr(12,2);
        }
        catch (...)
        {
        }

        telemType = strtoul(telemTypeStr.c_str(), NULL, 16);

        if (telemType == 7)
        {
          ssTotalPacket << dlpreamble << var;

          ssTotalPacket.seekg(0, std::ios::end);
          int size = ssTotalPacket.tellg();

          ssTotalPacket.seekg(0, std::ios::beg);

          // for (int i = 0; i < 2*(n + dlpreambleSize); i = i + 2)
          for (int i = 0; i < size; i = i + 2)
          {
            std::string tmpStr = ssTotalPacket.str().substr(i,2);
            val = strtoul(tmpStr.c_str(), NULL, 16);

            q.enQueue(val);
            // printDebug("val", val);
          }
        }
        else
        {
          std::cout << std::endl << std::endl;
          std::cout << "That sequence of hex characters did not work. Try again." << std::endl << std::endl;
        }

        ssTotalPacket.str(std::string());
        ssTmp.str(std::string());
        bzero(buffer, sizeof(buffer));
        n = 0;

        usleep(500000);
    }

    thrd_exit(EXIT_SUCCESS);
}

// This function simulates the reception and processing of CCSDS packets sent from the
// satellite. Bytes are read from the Queue class, which can be thought of as having just
// arrived from the satellite. These bytes are then assembled, parsed, and processed according
// to what kind of CCSDS packet they are interpreted to be. 
void *processSatellitePacketBytes(void *thr_id) 
{
  std::queue<uint8_t> runningBytes;
  std::queue<uint8_t> tmp_queue;
  uint8_t primaryPacketHeaderByteIndex = 0;
  std::stringstream primHdrSs;
  primHdrSs.str(std::string());
  std::stringstream packetDataFieldSs;
  packetDataFieldSs.str(std::string());
  bool foundDownlinkPreamble = false;
  bool justFoundDownlinkPreamble = false;
  bool packetPrimaryHeaderParsed = false;
  bool telemetryTypeError = false;
  uint32_t apid = 0;
  uint32_t pvn = 0;              
  uint32_t pkt_type = 0;
  uint32_t sec_hdr_flag = 0;
  uint32_t seq_flags = 0;
  uint32_t pkt_seq_cnt_or_pkt_name = 0;
  uint32_t len = 0;
  uint32_t telemetryType = 0;
  uint32_t packetDataFieldIndex = 0;
  std::string prmHdrSsStr;
  std::string firstTwoOctets;
  std::string secondTwoOctets;
  std::string thirdTwoOctets;
  uint32_t firstTwoOctetsUint32 = 0;
  uint32_t secondTwoOctetsUint32 = 0;
  uint32_t thirdTwoOctetsUint32 = 0;
  bool receivedElement = false;
  bool foundSixOctets = false;
  bool printedDidNotWorkMessage = false;

  bool printedTelemetry1 = false;
  bool printedTelemetry2 = false;
  bool printedTelemetry3 = false;
  bool printedTelemetry4 = false;
  bool printedTelemetry5 = false;
  bool printedTelemetry6 = false;
  bool printedTelemetry7 = false;
  bool printedTelemetryUnknown = false;

  uint8_t bytes[6];

    while (true)
    {
        telemetryTypeError = false;

        uint8_t elem;

        if (q.isEmpty() == false)
        {
            elem = q.deQueue();
            receivedElement = true;
        }
        else
        {
          if (receivedElement == true)
          {
            std::cout << std::endl << std::endl;
            std::cout << "That sequence of hex characters did not work. Try again." << std::endl << std::endl;
            receivedElement = false;
          }

          usleep(100000);
          continue;
        }

        // elem = q.deQueue();

        // printDebug("elem", elem);

        if (packetPrimaryHeaderParsed == true)
        {
            if (packetDataFieldIndex < len)
            {
              packetDataFieldSs << std::hex << std::setw(2) << std::setfill('0') << (((uint8_t) elem ) & 0xff);

              if (packetDataFieldIndex == (len - 1))
              {
                if (sec_hdr_flag == true)
                {
                  // std::cout << "Packet Data Field: " << std::hex << packetDataFieldSs.str().c_str() << std::endl;
                  // printDebug("len", len);

                  std::string telemetryTypeStr = packetDataFieldSs.str().substr(0,2);
                  telemetryType = strtoul(telemetryTypeStr.c_str(), NULL, 16);
                  // std::string telemetryStr = packetDataFieldSs.str().substr(2,2 * len);

                  packetDataFieldSs.str(std::string());

                  switch (telemetryType)
                  {
                  case 1:
                        printf("Handling Power Telemetry\n");
                        break;
                  case 2:
                        printf("Handling Guidance Telemetry\n");
                        break;
                  case 3:
                        printf("Handling CDH Telemetry\n");
                        break;
                  case 4:
                        printf("Handling Communications Telemetry\n");
                        break;
                  case 5:
                        printf("Handling Payload Telemetry\n");
                        break;
                  case 6:
                        printf("Handling Attitude Telemetry\n");                  
                        break;
                  case 7:
                        printf("Handling Test Telemetry\n");
                        break;
                  case 8:
                        printf("EMERGENCY_MODE: THE SPACECRAFT IS IN EMERGENCY_MODE\n");
                        printf("You made it!\nHere's your flag:\n");
                        printf("%s\n", flag); 
                        exit(0);              
                        // break;              
                  default:
                        // printf("Handling Unknown Telemetry\n");
                        telemetryTypeError = true;
                        break;
                  }

                  fflush(stdout);

                  usleep(500000);

                  // if (telemetryTypeError == true)
                  // {
                  //   continue;
                  // }
                }

                 packetPrimaryHeaderParsed = false;

                 packetDataFieldIndex = 0;

                 len = 0;
              }
              else
              {
                packetDataFieldIndex++;
              }

            }

            continue;
        }

        runningBytes.push(elem);

        // printDebug("elem", elem);

        if (runningBytes.size() > 4)
        {
          runningBytes.pop();

          tmp_queue = runningBytes;

          uint8_t tmpbuf[4];

          bzero(tmpbuf, sizeof(tmpbuf));

          uint8_t index = 0;

          std::stringstream ss;

          while (!tmp_queue.empty())
          {
            ss << std::hex << std::setw(2) << std::setfill('0') << (((unsigned int) tmp_queue.front()) & 0xff);

            tmpbuf[index] = tmp_queue.front();
            tmp_queue.pop();
            index++;
          }

          std::string testline = ss.str();

          // std::cout << "testline is: " << testline.c_str() << std::endl << std::endl;

          std::string downlinkpreamble = "1acffc1d";

          if (memcmp(testline.c_str(), downlinkpreamble.c_str(), 4) == 0)
          {
            foundDownlinkPreamble = true;
            justFoundDownlinkPreamble = true;
          }
        }

        if (foundDownlinkPreamble == true)
        {
          if (justFoundDownlinkPreamble == true)
          {
            justFoundDownlinkPreamble = false;
          }
          else
          {
            if (primaryPacketHeaderByteIndex < 6)
            {

              primHdrSs << std::hex << std::setw(2) << std::setfill('0') << (((unsigned int) elem ) & 0xff);

              ((uint8_t*)bytes)[primaryPacketHeaderByteIndex] = elem & 0xff;

              if (primaryPacketHeaderByteIndex == 5)
              {
                foundDownlinkPreamble = false;
                primaryPacketHeaderByteIndex = 0;

                // std::string testline2 = primHdrSs.str();
                // std::cout << "6 octets are: " << std::hex << testline2.c_str() << std::endl << std::endl;
                // testline2.clear();

                prmHdrSsStr = primHdrSs.str();
                firstTwoOctets = prmHdrSsStr.substr(0,4);
                secondTwoOctets = prmHdrSsStr.substr(4,4);
                thirdTwoOctets = prmHdrSsStr.substr(8,4);

                firstTwoOctetsUint32 = strtoul(firstTwoOctets.c_str(), NULL, 16);
                secondTwoOctetsUint32 = strtoul(secondTwoOctets.c_str(), NULL, 16);
                thirdTwoOctetsUint32 = strtoul(thirdTwoOctets.c_str(), NULL, 16);
                
                std::cout << std::endl << std::endl;
             
                primHdrSs.str(std::string());
                prmHdrSsStr.clear();
                firstTwoOctets.clear();
                secondTwoOctets.clear();
                thirdTwoOctets.clear();

                apid = readPktPrimHdrBitField(APID, firstTwoOctetsUint32);                
                pvn = readPktPrimHdrBitField(PVN, firstTwoOctetsUint32);              
                pkt_type = readPktPrimHdrBitField(PKT_TYPE, firstTwoOctetsUint32);
                sec_hdr_flag = readPktPrimHdrBitField(SEC_HDR_FLAG, firstTwoOctetsUint32);
                seq_flags = readPktPrimHdrBitField(SEQ_FLAGS, secondTwoOctetsUint32);
                pkt_seq_cnt_or_pkt_name = readPktPrimHdrBitField(PKT_SEQ_CNT_OR_PKT_NAME, secondTwoOctetsUint32);
                len = thirdTwoOctetsUint32 + 1;

                printDebug("Packet Version Number", pvn);
                printDebug("Packet Type", pkt_type);
                printDebug("Secondary Header Flag", sec_hdr_flag);
                printDebug("Application Process Identifier", apid);
                printDebug("Sequence Flags", seq_flags);
                printDebug("Packet Sequence Count or Packet Name", pkt_seq_cnt_or_pkt_name);
                printDebug("Packet Data Length", len);

                std::cout << std::endl << std::endl;

                foundSixOctets = true;
                printedDidNotWorkMessage = false;

                // If there are error conditions in the bits ...
                if ((pvn != 0) || (pkt_type != 0) || ((apid == 0x07ff) && (sec_hdr_flag == 1)))
                {
                  // Start over looking for the next packet.
                  continue;
                }

                packetPrimaryHeaderParsed = true;
                foundDownlinkPreamble = false;

              }
              else
              {
                  foundSixOctets = false;
                  primaryPacketHeaderByteIndex++;
              }
            }
          }
        }
        else
        {
          primHdrSs.str(std::string());
        }

        // usleep(300000);
        usleep(500000);
        // usleep(1000000);
    }

    thrd_exit(EXIT_SUCCESS);
}

int main(int argc, const char *argv[])
{
    printIntroArt();
    printIntroText();

    thrd_t threads[NUM_THREADS];
    int rc;

    rc = thrd_create(&threads[0], (thrd_start_t) getSatellitePacketBytes, NULL);
    if (rc == thrd_error) 
    {
        printf("ERROR; thrd_create() call failed for thread 0.\n");
        exit(EXIT_FAILURE);
    }    

    rc = thrd_create(&threads[1], (thrd_start_t) processSatellitePacketBytes, NULL);
    if (rc == thrd_error) 
    {
        printf("ERROR; thrd_create() call failed for thread 1.\n");
        exit(EXIT_FAILURE);
    }  

    rc = thrd_create(&threads[2], (thrd_start_t) startTimer, NULL);
    if (rc == thrd_error) 
    {
        printf("ERROR; thrd_create() call failed for thread 2.\n");
        exit(EXIT_FAILURE);
    } 

    int result = 0;
    thrd_join(threads[2], &result);

    exit(0);
}
