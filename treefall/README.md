# Quals Challenge: Treefall #

**Category:** Rapid Unplanned Disassembly
**Relative Difficulty:** 1/5
**Author:** [Cromulence](https://cromulence.com/)

If a tree falls in the forest...
Find the bug in the command parser's source code and exploit it. It was compiled with g++ 9.3.0.

# Description

parser.c is a udp server that parses out individual commands and increments a table based on the command id. Each command type is defined in an enumeration, and is used to index into the table. The parser incorrectly parses the command as a signed integer through the enumeration, and so teams can negatively index into the table to get an arbitrary increment. This can be used to increment the lock_state global with an id of -8. Teams will have to trigger this increment 254 times, to overflow back around to change the lock_state to 0 (UNLOCKED). Then, simply sending the COMMAND_GETKEYS will return the flag.

# Running

    docker run --rm -i -e SEED=1465500232115169100 -e FLAG=flag{TESTflag1234} -p ${CHAL_PORT}:${CHAL_PORT}/udp -e CHAL_PORT=${CHAL_PORT} -e CHAL_FLAG=${CHAL_FLAG} ${CHAL_NAME}:challenge 2>&1

## Considerations

This bug does not work using gcc 9.3.0, but does work with g++ 9.3.0. This is most likely due to  enumeration type algorithms, where the c compiler will choose an unsigned int for the type, but the c++ compiler will choose signed int.

(It may work on other versions of g++, but it hasn't been tested)



