# Overview
A vulnerable service with your "bank account" information running on the target system. Too bad it has already been exploited by a piece of ransomware. The ransomware took over the target, encrypted some files on the file system, and resumed the executive loop. The ransomware tried to clean itself up, but forgot a few details.

# Description
The challenge has a fairly easy buffer overflow bug to exploit with a convenient staging area. The challenge automatically exploits the vulnerable service, and encrypts the flag before giving control to the challenger. The malware has to play by the same rules that the challenger has to follow, but also restarts the main loop so the challenger can still play. The goal of the challenge is to follow the steps of the ransomware.

## Part 1 
Just need to exploit the service to get file system access. This part of the challenge is meant to be pretty easy. It just takes a simple buffer overflow of a memcpy to local struct, and returning to a memory page that they can load with their code to get system access.

## Part 2
Requires a good amount of snooping and probably a fairly complex, it could be considered a forensics challenge. The ransomware cleans up the filesystem pretty well, but leaves a lot of information in the execution context because its stack frames still exist (it calls back to the main loop, rather than returning to it). 

There's a red herring of trying to print out the flags that were loaded into memory. The ransomware squashes them with it's initial loader, the challengers can use this to figure out the first steps of the malware, but the majority of the malware exists in a memory mapped page. This should hopefully be enough to make the challengers try to search for the existing malware. By following the clues the challengers can figure out which memory page the challenge allocated for itself, and then dump it out to reverse engineer it. The malware also doesn't clean up the encryption key off the heap, which can be leaked from the ransomware stack frame. By combining this information with the leftover shell script that encrypted the files the challengers should be able to leak the flag and the key at the same time. 

# Running 
The Generator is the same for both part 1 and 2. Note: There is a kings_ransom1 and kings_ransom2

    docker run --rm -v <abs/path/to/out>:/out kings_ransom1:generator

The challenges are both run in the same way, they have different images so they can have seperate flags to match with the infrastructure. The challenges expect SERVICE_HOST and SERVICE_PORT to be provided by the runner, as well as FLAG. It will startup a service listening on that port and print the host and port information to the challenger as follows

    docker run --rm -i -e SERVICE_HOST=... -e SERVICE_PORT=... -e FLAG=flag{...} -p ${SERVICE_PORT}:54321 kings_ransom:challenge"
