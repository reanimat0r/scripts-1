#!/usr/bin/python

# Python implementation of http://xorshift.di.unimi.it/xorshift1024star.c
# Also released to the public domain

# Start with 16x 64-bit seeds
s = [
    28278612253763936382, 36298246713927356883,
    44979006082269828712, 14957337241762651207,
    29136122752540461035, 36301291101189644095,
     2619421885291555036, 686098512079929285,
    33217332582194747152, 56101619543791635899,
    64406556516425135242, 25719179272736507682,
    22752549146219005043, 18202154590671241618,
    50429450325440841034, 888366721593104755,
]

for i in xrange(30):
    s1, s0 = s[0], s[1]
    s[0] = s0
    s1 = s1 ^ (s1 << 23)
    s[1] = (s1 ^ s0 ^ (s1 >> 17) ^ (s0 >> 26)) + s0
    print s[1]
