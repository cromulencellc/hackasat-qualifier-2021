# Quals Challenge: Among Us #

**Category:** Rapid Unplanned Disassembly
**Relative Difficulty:** 3/5
**Author:** [Cromulence](https://cromulence.com/)

The three of us vote on star-tracker data and someone among us is acting a bit sus (you). Find a way to "convince" the interface module that you have the only vote that matters...

**Background:**

The interface is expecting messages from you. Your message should have the format: 

{4 byte directive}{32 byte key}{4 byte msg length}{msg}

Anytime you get a response back from the interface with your key, you should generate a new key by running your old key through a sha256 hashing algorithm. 

The following directives are available to you:
    POSE_QUESTION = 0
    VOTER_VOTE = 1
    MSG_RESPONSE = 2
    VOTER_LOG_CACHE = 3
    VOTER_LOG_SAVE = 4
    VOTER_READY = 5
    INVALID_DIRECTIVE = 99

You will receive the question as a double array[4] of quaternions with the POSE_QUESTION directive.

The first processor to vote in a round commits their vote. You may only commit your vote once per round. If you agree with a currently commited vote, you should not vote. You should only vote if you do not agree with the current commit.

You will be notified from the interface when there is a new commit from any processor, including yourself.

If you receive a message from the interface with a key of all 0xFF, that message is meant as information for all the processors on the bus. Do not iterate your key.

```
Example:

00000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff200000008b37328ffcc1ef3f739d465a2a6fbf3f00000000000000000000000000000000

Directive                     Generic Key                             Len of msg
    |                               |                                      |
[------][--------------------------------------------------------------][------][-->Everything else is msg up to len]
01000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff200000008b37328ffcc1ef3fc5724bab2171bf3f00000000000000000000000000000000

```

## Running Challenge ##
Create and run the challenge container `amongus:challenge`
```sh
make challenge
nc localhost 12345
```

## Running Solver ##
Create and run the solver container `amongus:solver` against the challenge container `amongus:challenge`
```sh
make solver
```

## Debugging Challenge Locally ##

Download libc2.27 from debian archives.

`patchelf --set-interpreter {path_to_glibc2.27} ./challenge`

```
gdb -q ./challenge
gdb> set exec-wrapper env 'LD_LIBRARY_PATH=/home/john/Downloads/libcdown/libc6_2.27/lib/x86_64-linux-gnu/'
gdb> run
```
