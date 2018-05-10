import logging

import guardlayer

global topology_string

class Topology(object):
    """
    A Topology object specifies the current guard topology of the onion service.

    A guard topology is a high-level object that defines how many guards are in
    each guard layer , and how the guards are connected, it's also responsible for
    rotating guards and checking whether they are compromised.

    A Topology is basically a bunch of GuardLayers connected with each other.
    """
    def __init__(self, adversary, state, topology_str, guard_lifetime_type):
        self.adversary = adversary
        self.state = state
        self.guard_lifetime_type = guard_lifetime_type

        self.first_layer = None
        self.second_layer = None
        self.third_layer = None

        # Terrible hack for dump_parameters (the topology type is static for the whole experiment)
        global topology_string
        topology_string = topology_str
        self.init_guard_layers(topology_str)

    def get_topology_config_from_str(self, top_str):
        """
        Return topology configuration (L1,L2,L3) given the topology as as a string "L1-L2-L3"
        e.g. "1-2-4" -> (1,2,4)
        """

        # split the string up
        topology_list = top_str.split("-")
        # turn them into integers
        topology_list = map(int, topology_list)

        # Let's do some basic sanitization
        assert(len(topology_list) == 3)
        assert(min(topology_list) > 0)
        assert(max(topology_list) < 10)

        return topology_list

    def init_guard_layers(self, top_str):
        # Get the number of guards per layer
        topology_config = self.get_topology_config_from_str(top_str)

        self.third_layer = guardlayer.GuardLayer(layer_num=3, num_guards=topology_config[2],
                                                 topology=self, adversary=self.adversary,
                                                 guard_lifetime_type=self.guard_lifetime_type,
                                                 state=self.state)
        self.second_layer = guardlayer.GuardLayer(layer_num=2, num_guards=topology_config[1],
                                                  topology=self, adversary=self.adversary,
                                                  guard_lifetime_type=self.guard_lifetime_type,
                                                  state=self.state)
        self.first_layer = guardlayer.GuardLayer(layer_num=1, num_guards=topology_config[0],
                                                 topology=self, adversary=self.adversary,
                                                 guard_lifetime_type=self.guard_lifetime_type,
                                                 state=self.state)

        self.third_layer.init_guards()
        self.second_layer.init_guards()
        self.first_layer.init_guards()

    def handle_node_rotations(self):
        # Is there a better order here?
        self.first_layer.handle_rotations()
        self.second_layer.handle_rotations()
        self.third_layer.handle_rotations()

    def handle_node_compromises(self):
        # Is there a better order here?
        self.first_layer.handle_new_compromises()
        self.second_layer.handle_new_compromises()
        self.third_layer.handle_new_compromises()

    """Given L1 return L2. Given L2 return L3. Given L3 return None"""
    def get_previous_guard_layer(self, guard_layer):
        # All guard layers should be initialized at this point
        assert(self.first_layer and self.second_layer and self.third_layer)

        if (guard_layer == self.first_layer):
            return self.second_layer

        if (guard_layer == self.second_layer):
            return self.third_layer

        if (guard_layer == self.third_layer):
            return None

        # Should never get here if we are fully initialized
        assert(False)

    """Given L1 return None. Given L2 return L1. Given L3 return L2"""
    def get_next_guard_layer(self, guard_layer):
        # All guard layers should be initialized at this point
        assert(self.first_layer and self.second_layer and self.third_layer)

        if (self.first_layer and guard_layer == self.first_layer):
            return None

        if (self.second_layer and guard_layer == self.second_layer):
            return self.first_layer

        if (self.third_layer and guard_layer == self.third_layer):
            return self.second_layer

        assert(False)

def dump_parameters():
    return "Topology type: %s\n" % topology_string
