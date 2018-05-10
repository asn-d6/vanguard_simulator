import logging

import guard
import util

"""
This file implements a guard layer and its functionalities.
A guard layer is a set of guards with their own own rotation times.
"""

class GuardLayer(object):
    def __init__(self, layer_num, num_guards, topology, adversary, guard_lifetime_type, state):
        self.layer_num = layer_num
        self.topology = topology
        self.adversary = adversary
        self.num_guards = num_guards
        self.state = state
        self.guard_lifetime_type = guard_lifetime_type

        self.guards = []

    def init_guards(self):
        for i in xrange(self.num_guards):
            self.add_new_guard()

        self.log_guardlayer()

    def __str__(self):
        return "L%d" % self.layer_num

    def log_guardlayer(self):
        """Do some guard layer logging"""
        guard_names = [guard.nickname for guard in self.guards]
        logging.info("%s topology: %s", self, str(guard_names))
        logging.info("="*80)

    def add_new_guard(self):
        """Add new guard to this guard layer"""
        new_guard_nick = util.get_guard_name()
        new_guard = guard.Guard(new_guard_nick, self, self.topology, self.adversary,
                                self.guard_lifetime_type, self.state)
        self.guards.append(new_guard)
        return new_guard

    def handle_rotations(self):
        """Handle rotations for this guard layer"""
        for guard in self.guards:
            if not guard.has_rotated():
                # It's not time to rotate yet
                continue

            # Rotate this guard
            self.guards.remove(guard)
            # Pick new guard
            new_guard = self.add_new_guard()
            assert(guard not in self.guards)

            self.state.register_guard_rotation(new_guard)

            # Do some logging
            logging.info("%s: Rotated %s and replaced with %s",
                         self, guard, new_guard)
            self.log_guardlayer()

    def handle_new_compromises(self):
        for guard in self.guards:
            # This one is already compromised
            if guard.is_compromised:
                continue

            if guard.is_pwned():
                guard.is_compromised = "pwned"
            elif guard.is_sybiled:
                guard.is_compromised = "sybiled"

            if guard.is_compromised:
                self.adversary.guard_compromised(guard)
