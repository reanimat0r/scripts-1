#!/bin/sh

# Generate an OpenSSH moduli file suitable for replacing /etc/ssh/moduli.
#
# This script executes in two parts:
#
# 1. Generate candidate primes for DH key exachange.
# 2. Run the candidates through the Miller-Rabin primality test.
# 
# Prime bit sizes range from 1024-bits to 8192-bits, in 512-bit intervals.
# Generating the candidates takes about 45 minutes on an older quad core Xeon.
# Generating the safe primes takes about 2 weeks on the same machine.
#
# Author: Aaron Toponce
# Date: Wed Jan 7, 2015
# License: Public Domain

NPROC=$(nproc)

grep -qo ' ht ' /proc/cpuinfo && NPROC=$((${NPROC}/2 ))

# generate the candidate primes files first
BITS=1024
while [ $BITS -le 8192 ]; do
    TMP=$NPROC
    until [ $TMP -eq 0 ]; do
        if [ $TMP -gt 1 ]; then
            ssh-keygen -G /dev/stdout -b $BITS | gzip -1c > moduli.${BITS}.gz &
            BITS=$((${BITS}+512))
        else
            ssh-keygen -G /dev/stdout -b $BITS | gzip -1c > moduli.${BITS}.gz
            BITS=$((${BITS}+512))
        fi
        TMP=$((${TMP}-1))
    done
done

echo -n "$(date +'%F %T')"

# now work on getting to the safe primes
BITS=1024
while [ $BITS -le 8192 ]; do
    echo "$BITS: $(date +'%F %T')"
    TMP=0
    TOTAL_LINES=$(gzip -dc moduli.${BITS}.gz | wc -l)
    LINES_PER_FILE=$(((${TOTAL_LINES}+${NPROC}-1)/${NPROC}))
    
    gzip -dc moduli.${BITS}.gz | split -a 1 -dl $LINES_PER_FILE 
        --filter="gzip -1c > moduli.${BITS}.$FILE.gz"

    while [ $TMP -lt $NPROC ]; do
        if [ $TMP -lt $((${NPROC}-1)) ]; then
            gzip -dc moduli.${BITS}.x${TMP}.gz | 
                ssh-keygen -T moduli.${BITS}.safe.${TMP} &
        else
            gzip -dc moduli.${BITS}.x${TMP}.gz | 
                ssh-keygen -T moduli.${BITS}.safe.${TMP}
        fi
        TMP=$((${TMP}+1))
    done
    cat moduli.${BITS}.safe.? >> moduli.${BITS}.safe
    rm moduli.${BITS}.safe.? moduli.${BITS}.x?.gz
    BITS=$((${BITS}+512))
done

cat moduli.????.safe > moduli
rm moduli.????.safe
