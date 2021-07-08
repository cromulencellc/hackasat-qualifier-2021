# Quals Challenge: Quaternion #

**Category:** Deck 36, Main Engineering
**Relative Difficulty:** 1/5
**Author:** [Cromulence](https://cromulence.com/)

A spacecraft is considered "pointing" in the direction of its z-axis or `[0,0,1]` vector in the "satellite body frame."

In the J2000 frame, the same spacecraft is pointing at `[0.14129425 -0.98905974  0.04238827]`.
Determine the spacecraft attitude quaternion `[Qx Qy Qz Qw]`.

## Building ##
Builds the challenge and solver containers `quaternion:challenge` and `quaternion:solver`
```sh
make build
```

## Testing ##
Test the solver container `quaternion:solver` against the challenge container `quaternion:challenge`
```sh
make test
```
