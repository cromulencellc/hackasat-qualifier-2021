# Quals Challenge: Noise #

**Category:** We're On the Same Wavelength
**Relative Difficulty:** 3/5
**Author:** [Cromulence](https://cromulence.com/)

We've captured this noisy IQ data from a satellite and need to decode it. Figure out how to filter the noise while maintaining the signal characteristics, then demodulate and decode the signal to get the flag. The satellite is transmitting using CCSDS packets and an unknown modulation.

## Building ##

This repository contains two Docker images: The `generator` and the `solver`.
You can build both with:

```sh
make build
```

The resulting Docker images will be tagged as `noise:generator` and
`generator:solver`.

You can also build just one of them with `make generator` or `make solver`
respectively.
