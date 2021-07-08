// ======================================================================
// \title  FlagSvrComponentImpl.cpp
// \author has
// \brief  cpp file for FlagSvr component implementation class
//
// \copyright
// Copyright 2009-2015, by the California Institute of Technology.
// ALL RIGHTS RESERVED.  United States Government Sponsorship
// acknowledged.
//
// ======================================================================


#include <QualsRef/FlagSvr/FlagSvrComponentImpl.hpp>
#include "Fw/Types/BasicTypes.hpp"
// #include<iostream>
// #include<fstream>
// #include<sstream>
// #include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include<string>

// static const char theFlagCode[128] = FLAG_CODE;
const char theFlagCode[] = FLAG_CODE;

namespace Ref {

  // ----------------------------------------------------------------------
  // Construction, initialization, and destruction
  // ----------------------------------------------------------------------

  // const std::string FlagSvrComponentImpl::m_theFlagCode = FLAG_CODE;

  FlagSvrComponentImpl ::
    FlagSvrComponentImpl(
        const char *const compName
    ) : FlagSvrComponentBase(compName)
  {

  }

  void FlagSvrComponentImpl ::
    init(
        const NATIVE_INT_TYPE instance
    )
  {
    FlagSvrComponentBase::init(instance);
    this->m_FlagSvrNoopCnt = 0;
    // char flagMaxLen[160];
    // memset(flagMaxLen, 0, sizeof(flagMaxLen));
    // memcpy(flagMaxLen, getenv("SAT_FLAG"), strlen(getenv("SAT_FLAG")));
    this->m_theFlag = getenv("SAT_FLAG");
    this->m_theFlag.resize(160);
    setenv("SAT_FLAG", "ThisIsNotTheFlagYouAreLookingFor", 1);
    // std::ifstream f(FLAG_DATA_FILE);
    // if(f) {
    //   std::ostringstream ss;
    //   ss << f.rdbuf();
    //   this->m_theFlag = ss.str();
    //   f.close();
    //   remove(FLAG_DATA_FILE);
    // }
  }

  FlagSvrComponentImpl ::
    ~FlagSvrComponentImpl(void)
  {

  }

  // ----------------------------------------------------------------------
  // Command handler implementations
  // ----------------------------------------------------------------------

  void FlagSvrComponentImpl ::
    FS_FlagEnable_cmdHandler(
        const FwOpcodeType opCode,
        const U32 cmdSeq,
        const Fw::CmdStringArg& passcode
    )
  {    
    Fw::LogStringArg logStr(passcode.toChar());
    this->log_ACTIVITY_HI_FS_FLAG_DATA_ATTEMPT(logStr);
    if(this->m_FlagSvrNoopCnt == 5) {
      std::string stringPasscodeInput = passcode.toChar();
      std::string theFlagCodeStr = theFlagCode;
      if(theFlagCodeStr.compare(stringPasscodeInput) == 0) {
        size_t flagLen = this->m_theFlag.length();
        int start = 0;
        Fw::TlmString tlmStringData0(this->m_theFlag.substr(start,40).c_str());
        start = start + 40;
        Fw::TlmString tlmStringData1(this->m_theFlag.substr(start,40).c_str());
        start = start + 40;
        Fw::TlmString tlmStringData2(this->m_theFlag.substr(start,40).c_str());
        start = start + 40;
        Fw::TlmString tlmStringData3(this->m_theFlag.substr(start,40).c_str());
        this->log_ACTIVITY_HI_FS_FLAG_RETRIEVED_SUCCESS();
        this->tlmWrite_FS_THE_FLAG_PART_0(tlmStringData0);
        this->tlmWrite_FS_THE_FLAG_PART_1(tlmStringData1);
        this->tlmWrite_FS_THE_FLAG_PART_2(tlmStringData2);
        this->tlmWrite_FS_THE_FLAG_PART_3(tlmStringData3);
        setenv("SAT_FLAG", "FLAG_FOUND", 1);
      }
    }
    this->cmdResponse_out(opCode,cmdSeq,Fw::COMMAND_OK);
  }

  void FlagSvrComponentImpl ::
    FS_FlagSvrNoop_cmdHandler(
        const FwOpcodeType opCode,
        const U32 cmdSeq
    )
  {
    this->m_FlagSvrNoopCnt++;
    this->tlmWrite_FS_NOOP_CNT(this->m_FlagSvrNoopCnt);
    this->cmdResponse_out(opCode,cmdSeq,Fw::COMMAND_OK);
  }

} // end namespace Ref
