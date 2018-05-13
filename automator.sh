#!/bin/sh

# This script runs an experiment for each possible configuration.
# This will take many many hours by default so I suggest you customize it.

sybil_models="tiny medium hell"
pwnage_models="none rubberhose1 rubberhose2"
topology_models="2-3-4 2-3-6 2-4-6 2-4-8"

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



