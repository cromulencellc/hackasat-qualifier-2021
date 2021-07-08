# Quals Challenge: Kepler 2 GEO #

**Category:** Guardians of the...
**Relative Difficulty:** 2/5
**Author:** [Cromulence](https://cromulence.com/)

Continuing from the first Kepler challenge, you have determined that your spacecraft is in a geosynchronous transfer orbit (GTO). Determine the maneuver (time and instantanous deltaV vector) required to circularize the orbit into geostationary.

## Building ##
Builds the challenge and solver containers `kepler2:challenge` and `kepler2:solver`
```sh
make build
```

## Testing ##
Test the solver container `kepler2:solver` against the challenge container `kepler2:challenge`
```sh
make test
```
