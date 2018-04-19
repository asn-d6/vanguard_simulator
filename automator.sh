#!/bin/sh

# This script runs an experiment for each possible configuration.
# This will take many many hours by default so I suggest you customize it.

sybil_models="weak medium hard hell"
pwnage_models="basic APT FVEY rubberhose1 rubberhose2"
topology_models="1-2-4 1-2-6 1-2-8 1-4-4 1-4-6 1-4-8 2-2-4 2-2-6 2-2-8 2-4-4 2-4-6 2-4-8"

for sybil in $sybil_models
do
    for pwnage in $pwnage_models
    do
        for topology in $topology_models
        do
            echo "Now doing:" $topology $pwnage $sybil
            pypy vanguard_sim.py $topology $sybil $pwnage
            python stats.py
        done
    done
done



