import datetime
import logging
import random
import time
import argparse
import sys

import adversary
import simulation
import stats
import util

"""
Basic simulation entry point:

A prop247 experiment is conducted by doing NUM_SIMULATIONS simulations, where
in each one an Adversary is trying to launch a guard discovery attack against
an onion service. An adversary wins when she deanonymizes the onion service by
compromising its G1 node.

In each simulation we keep various statistics in a StatsCache object and in the
end we aggregate the statistics and graph them in a hopefully useful way.
"""

# Number of simulations for an experiment to complete
# I suggest 10 for testing, and 500 to 1000 for actual final results (gonna take a while tho).
NUM_SIMULATIONS=10

DEFAULT_TOPOLOGY = "2-4-4"
DEFAULT_ADVERSARY_SYBIL = "medium"
DEFAULT_ADVERSARY_PWNAGE = "APT"

def parse_cmd_args():
    parser = argparse.ArgumentParser("vanguard_sim.py",
                                      formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("topology", type=str, default=DEFAULT_TOPOLOGY,
                        help="Guard topology to use (e.g. '1-2-4', '2-4-4', etc.)")
    parser.add_argument("sybil_model", type=str,
                        choices=adversary.SYBIL_PROBS.keys(),
                        default=DEFAULT_ADVERSARY_SYBIL,
                        help="Adversary Sybil attack strength")
    parser.add_argument("pwnage_model", type=str,
                        choices=adversary.PWNAGE_MODELS,
                        default=DEFAULT_ADVERSARY_PWNAGE,
                        help="Adversary Pwnage attack strength")

    return parser.parse_args()

def start():
    """
    Do a prop247 experiment. Run a bunch of simulations and then output
    statistics about them
    """

    args = parse_cmd_args()

    topology = args.topology
    sybil_model = args.sybil_model
    pwnage_model = args.pwnage_model

    stats_cache = stats.StatsCache(topology, sybil_model, pwnage_model)

    for i in xrange(NUM_SIMULATIONS):
        run_full_simulation(stats_cache, topology, sybil_model, pwnage_model)

    # Dump the stats we've all been waiting for
    stats_cache.dump_experiment_parameters()

    stats_cache.dump_stats()

def run_full_simulation(stats_cache, topology, sybil_model, pwnage_model):
    """
    Start and complete a simulation run, then when it's done handle its results.
    """

    # Initialize simulation state
    state = simulation.SimulationState(topology, sybil_model, pwnage_model)

    # Run simulation until it's done and then handle results
    try:
        run_simulation_helper(state)
    except adversary.AdversaryWon:
        stats_cache.register_run(state)

def run_simulation_helper(state):
    """
    This function actually carries out the simulation until it's done.
    """
    util.reset_guard_name_list()
    state.start_simulation()

    while True:
        state.move_simulated_time_forward()

def main():
    # Setup perfect randomness
    random.seed(time.time())

    # Setup logging
    logger = logging.getLogger('')
    # XXX take the filename from argparse
    hdlr = logging.FileHandler('/tmp/vanguard.log')
    logger.addHandler(hdlr)

    # Turn logging severity to 11
    logging.getLogger("").setLevel(logging.DEBUG)

    start()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Caught ^C. Closing.")
        sys.exit(1)

