import random
import logging

"""
This file introduces adversary models and functionality.
"""

# Sybil probabilities: First element is sybil prob for L1, second is for L2, third is for L3
# The prob is less for L1 than the others, because L1 is guard node which are
# supposed to be more trusted (have been around for longer) than random middle
# nodes
SYBIL_PROBS = {
    "tiny" : (0.01, 0.01, 0.01),
    "weak" : (0.02, 0.02, 0.02),
    "medium" : (0.05, 0.05, 0.05),
    "hard" : (0.07, 0.07, 0.07),
    "hell" : (0.10, 0.10, 0.10)
    }

# Three types of pwnage adversary: basic, APT, FVEY (see get_pwnage_time_*() functions below)
PWNAGE_MODELS = ("none", "basic", "APT", "FVEY", "rubberhose1", "rubberhose2")

class Adversary(object):
    """
    An adversary is constantly trying to pwn the client. She will keep on
    compromising guards and improving her Line Of Sight so that she can target
    more guards and compromise them. She never rests until she deanons the client.

    An adversary object is an oracle we consult to check whether a guard was
    compromised by a Sybil attack, or how long it will take the adversary to
    pwn a guard. All these depend on the adversary model we have chosen (see
    ADVERSARIES dictionary above).
    """
    def __init__(self, state, sybil_model, pwnage_model, stop_at_guard_discovery):
        self.state = state

        self.sybil_type = sybil_model
        self.pwnage_type = pwnage_model
        self.stop_at_guard_discovery = stop_at_guard_discovery

        # Terrible hack for dump_parameters (the adversary type is static for the whole experiment)
        global adversary_string
        adversary_string = "%s" % str(self)

    def __str__(self):
        return "Sybil: %s, Pwnage: %s" % (self.sybil_type, self.pwnage_type)

    def guard_compromised(self, compromised_guard):
        """
        A guard was compromised either by Sybil or pwnage. Do the appropriate
        actions
        """

        self.state.stats_count_guard_compromise(compromised_guard)

        # If it's an L1 guard, the adversary won!  Also if the optional flag
        # stop_at_guard_discovery is set, then the adversary wins at guard
        # discovery.
        if compromised_guard.layer_num == 1:
            self.game_won()
            raise AdversaryWon
        elif self.stop_at_guard_discovery and compromised_guard.layer_num == 2:
            self.game_won()
            raise AdversaryWon

        assert(compromised_guard.layer_num == 2 or
               compromised_guard.layer_num == 3)

        # If it's an L3 guard that got compromised, keep some exta statistics.
        if compromised_guard.layer_num == 3:
            self.state.stats_register_time_left_before_g2_rotation(compromised_guard)

        # This guard is either L2 or L3, we need to go to the next guard layer,
        # and mark all guards as targetted, since now the adversary can see
        # them and will need to capture them next.
        next_guard_layer = self.state.topology.get_next_guard_layer(compromised_guard.guard_layer)
        for guard in next_guard_layer.guards:
            # Target this guard
            if not guard.is_targetted:
                guard.is_targetted = compromised_guard
            # Add pwnage time since the adversary is now actively trying to pwn it
            if not guard.pwnage_time:
                guard.pwnage_time = self.get_pwnage_time(guard)

    def try_sybil(self, guard):
        # Dig into the adversary dictionary and get the sybil probs for this adversary type
        assert(self.sybil_type in SYBIL_PROBS)
        sybil_probs = SYBIL_PROBS[self.sybil_type]
        if (sybil_probs == None):
            return False

        if guard.layer_num == 1:
            sybil_prob = sybil_probs[0]
        elif guard.layer_num == 2:
            sybil_prob = sybil_probs[1]
        elif guard.layer_num == 3:
            sybil_prob = sybil_probs[2]

        if random.random() <= sybil_prob:
            logging.info("[*] %s got SYBILed!", guard)
            return True

        return False

    def get_pwnage_time(self, guard):
        """
        Get time needed to pwn this Guard, based on adversary type
        """

        # Dig into the adversary dictionary and get the sybil probs for this adversary type
        assert(self.pwnage_type in PWNAGE_MODELS)

        if (self.pwnage_type == "none"):
            return -1
        elif (self.pwnage_type == "basic"):
            return self.get_pwnage_time_basic(guard)
        elif (self.pwnage_type == "APT"):
            return self.get_pwnage_time_apt(guard)
        elif (self.pwnage_type == "FVEY"):
            return self.get_pwnage_time_FVEY(guard)
        elif (self.pwnage_type == "rubberhose1"):
            return self.get_pwnage_time_rh1(guard)
        elif (self.pwnage_type == "rubberhose2"):
            return self.get_pwnage_time_rh2(guard)

    def get_pwnage_time_basic(self, guard):
        """
        Basic adversary has 50% chance to pwn within 15 days (chance increases linearly within those 15 days)
        """
        now = self.state.get_time()
        roll = random.random()

        # Let's first handle the 50% chance where this guard will never get owned
        # Return negative value to signal that
        if (roll > 0.5):
            logging.info("\t %s will never get pwned", guard.nickname)
            return -1

        # Now let's handle the pwnage within 15 days in a linear way
        maximum = 60*60*24*15
        time_to_pwnage = maximum * 2*  float(roll)

        logging.info("\t %s will get pwned in %d hours",
                     guard.nickname, time_to_pwnage/3600)

        return now + time_to_pwnage

    def get_pwnage_time_apt(self, guard):
        """
        APT: 75% chance within 15 days, 100% chance between 15days and 1 month (linear)
        """
        now = self.state.get_time()
        roll = random.random()

        # Handle the 75% chance within 15 days
        if (roll < 0.75):
            maximum = 60*60*24*15
            time_to_pwnage = maximum * float(roll)
        else:  # Handle the 100% within a month (so within 15 days to 30 days)
            minimum = 60*60*24*15
            maximum = 60*60*24*30
            #we actually need to reroll here
            roll = random.random()
            time_to_pwnage = minimum + (maximum - minimum) * float(roll)

        logging.info("\t %s will get pwned in %d hours",
                     guard.nickname, time_to_pwnage/3600)

        return now + time_to_pwnage

    def get_pwnage_time_FVEY(self, guard):
        """
        FVEY: 50% chance to pwn within 2 days (with MLAT), 75% chance to pwn within 7 days (with exploit)
        """
        now = self.state.get_time()
        roll = random.random()

        if (roll > 0.75):
            logging.info("\t %s will never get pwned", guard.nickname)
            return -1

        # Handle the 50% chance within 2 days
        if (roll < 0.5):
            maximum = 60*60*24*2
            time_to_pwnage = maximum * float(roll)
        elif (roll <= 0.75):
            #also need to reroll here
            roll = random.random()
            maximum = 60*60*24*7
            time_to_pwnage = maximum * float(roll)

        logging.info("\t %s will get pwned in %d hours",
                     guard.nickname, time_to_pwnage/3600)

        return now + time_to_pwnage

    def get_pwnage_time_rh1(self, guard):
        """
        Rubberhose 1: Takes 2 days for the thugs to show up, which rises to 50% within 2 weeks
        """
        now = self.state.get_time()
        roll = random.random()

        if (roll > 0.5):
            logging.info("\t %s has too many guards of its own for thugs", guard.nickname)
            return -1

        time_to_pwnage = 60*60*24*2 + 60*60*24*12 * 2* float(roll)

        logging.info("\t %s will get pwned in %d hours",
                     guard.nickname, time_to_pwnage/3600)

        return now + time_to_pwnage

    def get_pwnage_time_rh2(self, guard):
        """
        Rubberhose 1: Takes 1 week for the thugs to show up, which rises to 50% within 3 weeks
        """
        now = self.state.get_time()
        roll = random.random()

        if (roll > 0.5):
            logging.info("\t %s has too many guards of its own for thugs", guard.nickname)
            return -1

        time_to_pwnage = 60*60*24*7 + 60*60*24*14 * 2* float(roll)

        logging.info("\t %s will get pwned in %d hours",
                     guard.nickname, time_to_pwnage/3600)

        return now + time_to_pwnage


    def game_won(self):
        """We just won the game!"""
        self.state.stats_dump()

def dump_parameters():
    return "Adversary type: %s\n" % adversary_string

class AdversaryWon(Exception): pass
