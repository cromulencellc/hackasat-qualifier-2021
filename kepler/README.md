# Quals Challenge: Kepler #

**Category:** Guardians of the...
**Relative Difficulty:** 1/5
**Author:** [Cromulence](https://cromulence.com/)

Your spacecraft has provided its Cartesian ICRF position (km) and velocity (km/s). What is its orbit (expressed as Keplerian elements)?

## Building ##
Builds the challenge and solver containers `kepler:challenge` and `kepler:solver`
```sh
make build
```

## Testing ##
Test the solver container `kepler:solver` against the challenge container `kepler:challenge`
```sh
make test
```
