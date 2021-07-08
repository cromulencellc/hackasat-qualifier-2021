# Quals Challenge: hindsight #

**Category:** Astronomy, Astrophysics, Astrometry, and Astrodynamics (AAAA)
**Relative Difficulty:** 6/6
**Author:** [Cromulence](https://cromulence.com/)

Revenge of the space book!

Due to budget cutbacks, your optical sensor on your satellite was made with parts from the flea market. This sensor is terrible at finding stars in the field of view. Readings of individual positions of stars is very noisy. To make matters worse, the sensor can't even measure magnitudes of stars either.

Budget cutbacks aside, make your shareholders proud by identifying which stars the sensor is looking at based on the provided star catalog. 

## Running ##

Run the challenge with

socat -v tcp-listen:1337,reuseaddr "exec:python3 challenge.py"

And run the solver with

python3 solver.py

## Notes ##

This challenge is based on the my_0x20 or myspace challenge from HAS1 quals. It adds complexity to the problem of discovering which stars are in view by removing star magnitudes, and adding more error to positions of stars. This problem can be solved using similar computer vision techniques as the last time, but it needs much more introspection on star patterns. The solution was made by creating triangles from the catalog, and using three parameters to describe a parameter: interial moment, ratio of smallest to largest side, and total area. After finding candidate triangles and matching, it also eliminates outliers using the median standard deviation.
