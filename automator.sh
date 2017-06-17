#!/bin/sh

# This script runs an experiment for each possible configuration.
# This will take many many hours by default so I suggest you customize it.

sybil_models="weak medium hard"
pwnage_models="basic APT FVEY"
topology_models="1-2-4 1-2-6 1-2-8 1-4-4 1-4-6 1-4-8 2-2-4 2-2-6 2-2-8 2-4-4 2-4-6 2-4-8"

for sybil in $sybil_models
do
    for pwnage in $pwnage_models
    do
        for topology in $topology_models
        do
            echo "Now doing:" $topology $pwnage $sybil
            python vanguard_sim.py $topology $sybil $pwnage
        done
    done
done



