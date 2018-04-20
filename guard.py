import logging
import random

# Rotation parameters
FIRST_GUARD_ROTATION_MIN = 3 * 60*60*24*30 # three months
FIRST_GUARD_ROTATION_MAX = 4 * 60*60*24*30 # four months
SECOND_GUARD_ROTATION_MIN = 10 * 60*60*24 # ten days
SECOND_GUARD_ROTATION_MAX = 12 * 60*60*24 # twelve days
THIRD_GUARD_ROTATION_MIN = 10 * 60*60 # ten hours
THIRD_GUARD_ROTATION_MAX = 14 * 60*60 # fourteen hours

class Guard(object):
    """
    A guard is the heart of our experiment. Each client has multiple active
    guards at any given time assigned to different GuardLayers. Once a guard is
    chosen, it will stick for a while, and then rotate based on its lifetime.

    A guard can also get compromised: When a guard is first chosen, we toss a
    coin (based on the current experiment parameters), and we decide whether it
    got Sybiled or not. Furthermore, if the adversary can target this guard
    (i.e. can see it) it targets it for pwnage, and sets a timer which upon
    expiration pwns the guard and compromises it.
    """
    def __init__(self, nickname, guard_layer, topology, adversary, state):
        self.adversary = adversary
        self.nickname = nickname
        self.guard_layer = guard_layer
        self.topology = topology
        self.state = state
        self.layer_num = guard_layer.layer_num

        logging.info("[!] New guard created: %s", nickname)

        # Is this guard a sybil?
        self.is_sybiled = adversary.try_sybil(self)

        # When will this guard rotate?
        self.rotation_time = self.get_rotation_time()

        # Is this guard in the adversary's line of sight?
        # If this Guard is targetted, this variable contains the Guard that got
        # compromised and allowed the adversary to target this guard (e.g. if
        # this is a targetted L1 guard, this variable contains the L2 guard
        # that allowed the adversary to target it).
        # If this guard is not targetted, this variable is False.
        self.is_targetted = self.is_targetted_func()
        if self.is_targetted:
            logging.info("\t %s is targetted", self)

        # If the adversary can see this guard, when will it get pwned?
        if self.is_targetted:
            self.pwnage_time = adversary.get_pwnage_time(self)
        else:
            self.pwnage_time = None

        # Is this guard compromised? Updated in handle_new_compromises()
        # Set to "sybiled" if it got sybiled, or to "pwned" if it got pwned.
        self.is_compromised = False

    def __str__(self):
        return "%s (L%s)" % (self.nickname, self.layer_num)

    def is_targetted_func(self):
        """
        Check if this Guard is in the adversary's Line of Sight.

        e.g. If this guard is in L2, then the adversary needs to be in L3.
        """

        prev_guard_layer = self.topology.get_previous_guard_layer(self.guard_layer)

        # If this is an L3 guard, then the adversary targets it by definition
        if not prev_guard_layer:
            logging.info("\t targetted because it's in L3")
            return "L3"

        # If it's an L2 or L1 guard: Check all guards of the previous layer to
        # see if any are compromised
        for guard in prev_guard_layer.guards:
            if guard.is_compromised:
                logging.info("\t targetted because compromised prev guard (%s)", guard)
                return guard

        return False

    def get_rotation_time(self):
        now = self.state.get_time()

        # Get rotation delay depending on guard layer
        if self.layer_num == 1:
            rot_delay = random.randint(FIRST_GUARD_ROTATION_MIN,
                                       FIRST_GUARD_ROTATION_MAX)
        elif self.layer_num == 2:
            rot_delay = random.randint(SECOND_GUARD_ROTATION_MIN,
                                       SECOND_GUARD_ROTATION_MAX)
        elif self.layer_num == 3:
            rot_delay = random.randint(THIRD_GUARD_ROTATION_MIN,
                                       THIRD_GUARD_ROTATION_MAX)
        else:
            assert(False) # shouldn't be in here

        logging.info("\t %s will rotate in %d seconds",
                     self, rot_delay)

        return now + rot_delay

    def has_rotated(self):
        """Return True if this node needs to rotate"""
        now = self.state.get_time()

        assert(self.rotation_time)

        if self.rotation_time <= now:
            return True

        return False

    def is_pwned(self):
        """Return True if this node got pwned"""
        now = self.state.get_time()

        # This guard is not targetted yet
        if not self.pwnage_time:
            return False

        # If it's negative, this guard will not get pwned in a reasonable timeframe.
        if self.pwnage_time < 0:
            return False

        if self.pwnage_time <= now:
            logging.info("[*] %s got PWNed!", self)
            return True

        return False

def dump_parameters():
    params = "Guard lifetimes: (%d hours - %d hours), (%d hours - %d hours), (%d hours - %d hours)\n" % \
        (FIRST_GUARD_ROTATION_MIN / 3600, FIRST_GUARD_ROTATION_MAX / 3600,
         SECOND_GUARD_ROTATION_MIN / 3600, SECOND_GUARD_ROTATION_MAX / 3600,
         THIRD_GUARD_ROTATION_MIN / 3600, THIRD_GUARD_ROTATION_MAX / 3600)
    # params += "Guard lifetime sampling logic: uniform, uniform, uniform\n"
    return params
