# Vanguards simulation

This project roughly implements and simulates [Tor proposal
247](https://gitweb.torproject.org/torspec.git/tree/proposals/247-hs-guard-discovery.txt)
in an attempt to analyze the security properties of vanguards and [optimize
their parameters](https://github.com/asn-d6/vanguard_simulator/wiki/Optimizing-vanguard-topologies).
It's meant to guide and consult the
[Vanguards](https://github.com/mikeperry-tor/vanguards) Tor controller.

## What is a vanguard simulation?

Each vanguard simulation is basically a game between a Tor client and an
adversary. Time is kept and it's constantly ticking. The Tor client picks its
vanguards and rotates them over time, while the adversary constantly tries to
compromise the client's guards using Sybil and "pwnage" attacks.

A simulation ends when the adversary wins. The adversary wins when it manages
to compromise the first guard layer of the client, which effectively
deanonymizes the client.

[Sybil attacks are meant to simulate the attacker controlling some percentage
of the Tor network and eventually becoming the client's guards though the
client's guard rotations. "Pwnage" attacks are meant to simulate the attacker
compromising the client's guard nodes directly using software exploits or
coercion attacks.]

## What does this project do?

This project is able to run the above simulation scenario using different
parameters (i.e. adversary models and guard topologies). We call each run of
this project an "experiment". In every "experiment", we run multiple vanguard
simulations with the same parameters, and keep various statistics. In the end
of the experiment we produce graphs that help us analyze the security
properties of vanguard and optimize its parameters.

## What kind of statistics do I get out of it?

For each experiment, the vanguard simulator will produce the following data:

- CDF graph of hours to deanonymize client for the experiment's configuration.

  This is an important metric that estimates the anonymity guarantee we can
  have with the current configuration.

- CDF graph of hours to compromise first G3 node for the experiment's configuration.

  This shows us how strong against Sybil attacks the L3 is, in the current
  configuration.

- CDF graph of remaining G2 lifetime in hours when a G3 gets first compromised.

  This shows us how much time the adversary has to compromise G2 upon learning
  its identity.

- Various other metrics per experiment like ''average number of rotations'' and
  ''average hours to deanon''

Feel free to add your own metrics or suggest ones that can be useful and I will
do them.

## How do I use it?

For this project to work, you will need some extra Python libraries. You can
get them like this:

          # apt install python-numpy python-pandas python-seaborn

You can then run an experiment as follows:

          $ python vanguard_sim.py 2-4-8 hard APT

which will run an experiment with a 2-4-8 topology, against a "hard" sybil
adversary with "APT" pwnage capabilities. Please see adversary.py for the
various adversary models.

There is also the 'automator.sh' bash script which will run an experiment for
each possible configuration, there are hundreds of them tho, so it's gonna take
a while! I suggest you customize it to only run the ones you care about.

There will be logs produced in /tmp/vanguard.log which will allow you to monitor
the run of the experiment. These logs are very useful to verify the correctness
of the project.

## Notes

Here are some things you might want to tweak:

- The number of simulation runs per experiment is controlled by
  NUM_SIMULATIONS. It's currently set to a low value for testing, but make sure
  you increase this before getting some final results (so that the law of large
  numbers kicks in).

- Also feel free to customize the adversary models in adversary.py based on your
  preferences. I suggest you give new names to new models so that we don't get
  confused with the old ones.

- You might also want to change the default guard lifetimes in guard.py .

The code quality is "quasi-documented research-level code". This means that if
you encounter a bug (quite likely), it's better to let asn know, except if you
want to get your hands dirty.
