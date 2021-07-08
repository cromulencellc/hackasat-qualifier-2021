# Quals Challenge: Groundead #

**Category:** Presents from Marco
**Relative Difficulty:** 1/5
**Author:** [Cromulence](https://cromulence.com/)

In this challenge, you will be given the source code for a ground station. 

This source code has a vulnerability in it that can be exploited by an operator. 

The exploit is this: make the satellite it communicates with send a CCSDS telemetry packet that indicates the satellite is in “EMERGENCY MODE”. 

An “EMERGENCY MODE” telemetry packet sent to the ground station can only originate from the satellite. 

Other telemetry packets that originate from the satellite are power, guidance, CDH, communications, payload, and attitude telemetry. 

The only way the exploit can be achieved is for the ground station to first send a CCSDS test command packet to the satellite. 

A test command is used to test that the satellite is working properly by merely echoing the test command back to the ground station. 

This test command packet may contain a payload consisting of test data (“dummy data”). 

When prompted by the ground station, enter your test command as a string of hex characters. 

Once you are able to cause the satellite to report an “EMERGENCY MODE” warning, you will receive the flag. 