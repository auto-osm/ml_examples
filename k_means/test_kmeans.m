#!/usr/bin/octave

m =[ 0.00000   0.57735;
    0.00000   0.57735;
    0.70711  -0.00000;
    0.00000   0.57735;
    0.70711  -0.00000]


clusters = chieh_kmean(2, m', 2)