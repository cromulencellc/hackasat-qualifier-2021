# Quals Challenge: Error Correction #

**Category:** We're On the Same Wavelength
**Relative Difficulty:** 3/5
**Author:** [Cromulence](https://cromulence.com/)

Our spacecraft just downlinked some important telemetry but a bit error is preventing us from decoding it. Use Viterbi decoding to correct the bit error and get the flag.

## Building ##

This repository contains two Docker images: The `generator` and the `solver`.
You can build both with:

```sh
make build
```

The resulting Docker images will be tagged as `error-corr:generator` and
`generator:solver`.

You can also build just one of them with `make generator` or `make solver`
respectively.
