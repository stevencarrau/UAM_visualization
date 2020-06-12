# Import the packages that we need
from __future__ import print_function

from tulip import spec
from tulip import synth


#
# Environment specification
#
# The environment can issue a park signal that the robot must respond
# to by moving to the lower left corner of the grid.  We assume that
# the park signal is turned off infinitely often.
#
env_vars = {'park'}
env_init = set()                # empty set
env_safe = set()                # empty set
env_prog = '!park'              # []<>(!park)

#
# System dynamics
#
# The system specification describes how the system is allowed to move
# and what the system is required to do in response to an environmental
# action.
#
sys_vars = {}
sys_vars['loc'] = (0, 5)

sys_init = {'loc=0'}
sys_safe = {
    'loc=0 -> X (loc=1 || loc=3)',
    'loc=1 -> X (loc=0 || loc=4 || loc=2)',
    'loc=2 -> X (loc=1 || loc=5)',
    'loc=3 -> X (loc=0 || loc=4)',
    'loc=4 -> X (loc=3 || loc=1 || loc=5)',
    'loc=5 -> X (loc=4 || loc=2)',
}
sys_prog = set()                # empty set

#
# System specification
#
# The system specification is that the robot should repeatedly revisit
# the upper right corner of the grid while at the same time responding
# to the park signal by visiting the lower left corner.  The LTL
# specification is given by
#
#     []<> X5 && [](park -> <>(loc=0))
#
# Since this specification is not in GR(1) form, we introduce an
# environment variable X0reach that is initialized to True and the
# specification [](park -> <>(loc=0)) becomes
#
#     [](X (X0reach) <-> (loc=0) || (X0reach && !park))
#

# Augment the system description to make it GR(1)
sys_vars['X0reach'] = 'boolean'
sys_init |= {'X0reach'}
sys_safe |= {'(X (X0reach) <-> (loc=0)) || (X0reach && !park)'}
sys_prog |= {'X0reach', 'loc=5'}

# Create a GR(1) specification
specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                    env_safe, sys_safe, env_prog, sys_prog)
specs.qinit = '\E \A'  # Moore initial condition synthesized too
specs.plus_one = False
specs.moore = False

#
# Controller synthesis
#
# At this point we can synthesize the controller using one of the available
# methods.
#

ctrl = synth.synthesize(specs,solver='omega')
ctrl2 = synth.synthesize(specs,solver='slugs')
print(ctrl)
print(ctrl2)
assert ctrl is not None, 'unrealizable'