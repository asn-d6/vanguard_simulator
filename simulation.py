import time
import logging
import datetime
import sys

import topology
import adversary

# Time units. This is how many seconds we move forward in every tick.
# Increasing this value will make the simulation finish faster but will provide more rough timing stats.
TIME_UNIT = 1000 # seconds

class SimulationState(object):
    """
    A SimulationState holds the state of a single prop247 simulation.

    During a simulation, the onion service picks and rotates guards, while the
    adversary is continuously working towards a guard discovery attack. We keep
    the time and progress it in ticks; in every tick we check whether we need
    to rotate any guards or whether the adversary pwned any guards. When the
    adversary gets to compromise G1 (i.e. deanonymize the onion service) , the
    simulation is over.
    """
    def __init__(self, topology_model, sybil_model, pwnage_model, guard_lifetime_type):
        self.adversary = adversary.Adversary(self, sybil_model, pwnage_model)
        self.topology_model = topology_model
        self.guard_lifetime_type = guard_lifetime_type

        self.topology = None

        # The current simulated time
        self.time = 0

        # Here are various simulation stats we want to keep:
        self.total_guard_rotations = None
        self.time_to_g1 = None
        self.time_to_g2 = None
        self.time_to_g3 = None
        self.times_left_for_g2_rotation = []
        self.guard_pwnages = []
        self.guard_sybils = []
        self.winning_path = None

    def get_time(self):
        return self.time

    def start_simulation(self):
        self.topology = topology.Topology(self.adversary, self, self.topology_model, self.guard_lifetime_type)

    def move_simulated_time_forward(self):
        """
        Move simulated time forward and check for any needed roattions or
        compromises.
        """
        self.time += TIME_UNIT

        # Sleep a bit so that logs don't go so fast...
        # time.sleep(0.7)

        #logging.info("Time is now: %d" % (self.time))

        self.topology.handle_node_rotations()
        self.topology.handle_node_compromises()

    # Stat keeping functions:
    def register_guard_rotation(self, guard):
        if not self.total_guard_rotations:
            self.total_guard_rotations = 0

        self.total_guard_rotations += 1

    def stats_register_time_left_before_g2_rotation(self,guard):
        """
        A guard just got compromised in L3. Register time left to rotate for all L2.
        """
        assert(guard.layer_num == 3)
        l2_guard_layer = self.topology.get_next_guard_layer(guard.guard_layer)

        logging.debug("Registering new remainging time")

        now = self.get_time()
        for guard in l2_guard_layer.guards:
            assert(guard.layer_num == 2)
            time_left_to_rotate = guard.rotation_time - now
            self.times_left_for_g2_rotation.append(time_left_to_rotate)

    def stats_count_guard_compromise(self, compromised_guard):
        now = self.get_time()

        if compromised_guard.layer_num == 1:
            self.set_time_to_g1(now)
            self.get_winning_path(compromised_guard)
        elif compromised_guard.layer_num == 2:
            self.set_time_to_g2(now)
        elif compromised_guard.layer_num == 3:
            self.set_time_to_g3(now)

        if compromised_guard.is_compromised == "pwned":
            self.register_new_pwnage(compromised_guard)
        elif compromised_guard.is_compromised == "sybiled":
            self.register_new_sybil(compromised_guard)

    def set_time_to_g1(self, time):
        """We just learned a G1 node for the first time. Keep the time"""
        if not self.time_to_g1:
            self.time_to_g1 = time

    def set_time_to_g2(self, time):
        """We just learned a G2 node for the first time. Keep the time"""
        if not self.time_to_g2:
            self.time_to_g2 = time

    def set_time_to_g3(self, time):
        """We just learned a G3 node for the first time. Keep the time"""
        if not self.time_to_g3:
            self.time_to_g3 = time

    def register_new_pwnage(self, pwned_guard):
        if pwned_guard not in self.guard_pwnages:
            self.guard_pwnages.append(str(pwned_guard))

    def register_new_sybil(self, sybiled_guard):
        if sybiled_guard not in self.guard_sybils:
            self.guard_sybils.append(str(sybiled_guard))

    def get_winning_path(self, g1_guard):
        """G1 got compromised. The game is over. Find the winning path"""
        g1 = g1_guard
        g2 = None
        g3 = None

        if g1_guard.is_targetted:
            g2 = g1_guard.is_targetted

        if g2:
            g3 = g2.is_targetted

        self.winning_path = str(g3) + " -> " + str(g2) + " -> " +  str(g1)

    def stats_dump(self):
        assert(self.time_to_g1)
        logging.warn("=" * 80)
        logging.warn("Adversary '%s' won the game!", self.adversary)
        logging.warn("Guard rotations: %s" % str(self.total_guard_rotations))
        logging.warn("Time to deanonymization: %d hours" % (self.time_to_g1 / 3600))
        if self.time_to_g2:
            logging.warn("Time to guard discovery: %d hours" % (self.time_to_g2 / 3600))
        if self.time_to_g3:
            logging.warn("Time to become G3: %d hours" % (self.time_to_g3 / 3600))
        logging.warn("Times left to G2 rotation: %s" % str(self.times_left_for_g2_rotation))

        logging.warn("Pwned guards: %s" % str(self.guard_pwnages))
        logging.warn("Sybiled guards: %s" % str(self.guard_sybils))

        logging.warn("Winning path: %s" % str(self.winning_path))

