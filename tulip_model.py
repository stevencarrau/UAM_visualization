from tulip import transys,abstract,spec,synth
from itertools import chain, combinations,product
import copy
import time

def powerset(s):
    x = len(s)
    a = []
    for i in range(1,1<<x):
        a.append({s[j] for j in range(x) if (i &(1<<j))})
    return a

# sys = transys.FTS()
max_requests = 4
num_vertiports = 1
max_service = 1


env_vars = {}
sys_vars = {}
for i in range(1,max_requests+1):
	env_vars['r{}'.format(i)] = (0,num_vertiports)
env_vars['available'] = (0,max_service)
for j in range(max_service):
	sys_vars['a{}'.format(j)] = (0,max_requests)

sys_safe = set()
env_safe = set()
for n in range(max_service):
	str = 'available={} -> '.format(n)
	disallowed_combos = combinations(range(max_service), max_service - n)
	for request_combo in disallowed_combos:
		str += '!('
		for request in request_combo:
			str += 'a{} != 0 || '.format(request)
		str = str[:-3]
		str += ') || '
	str = str[:-3]
	sys_safe |= set([str])
	for m in range(1, max_service + 1):
		possible_request_combo = powerset(range(1, max_requests + 1))
		for request_set in possible_request_combo:
			str2 = 'available = {} && '.format(m)
			str2 += '('
			for request in request_set:
				str2 += 'r{} != 0 && '.format(request)
			for request in set(range(1, max_requests + 1)).difference(request_set):
				str2 += 'r{} = 0 && '.format(request)
			str2 = str2[:-3]
			str2 += ') -> ('
			allowed_available_combos = list(combinations(range(max_service), m))
			for k in allowed_available_combos:
				accept_available_combos = list(product(tuple(k), list(request_set)))
				for accept_set in accept_available_combos:
					str2 += 'a{} = {} || '.format(accept_set[0], accept_set[1])
				str2 = str2[:-3]
				str2 += ') || ('
			str2 = str2[:-4]
			sys_safe |= set([str2])
all_combos = list(powerset(range(max_service)))
prev_rhs = ''
for n in range(1, max_service + 1):
	request_combo = combinations(range(1, max_requests + 1), max_requests - n + 1)
	str = 'available = {} ->'.format(n)
	rhs = ' ( ('
	for combos in all_combos:
		if len(combos) == n:
			for request in combos:
				rhs += 'a{} != 0 && '.format(request)
			rhs = rhs[:-3]
			rhs += ') || ('
	rhs = rhs[:-4]
	rhs += ') '
	for request_set in request_combo:
		rhs += '|| ('
		for request in request_set:
			rhs += 'r{} = 0 && '.format(request)
		rhs = rhs[:-3]
		rhs += ')'
	str += rhs
	str += prev_rhs
	prev_rhs = copy.deepcopy(rhs)
	prev_rhs = '&& (' + prev_rhs
	prev_rhs += ')'
	sys_safe |= set([str])
all_combos = combinations(range(max_service), 2)
for combos in all_combos:
	sys_safe |= set(['a{} != a{} || (a{} = 0 || a{} = 0)\n'.format(combos[0], combos[1], combos[0], combos[1])])
for n in range(1, max_requests + 1):
	str = 'r{} = 0 -> !('.format(n)
	for m in range(max_service):
		str += 'a{} = {} || '.format(m, n)
	str = str[:-3]
	str += ')\n'
	sys_safe |= set([str])

## Environment trans
for n in range(1, max_requests + 1):
	str = 'r{} != 0 && ('.format(n, n)
	str2 = 'r{} != 0 && ('.format(n, n)
	for m in range(max_service):
		str += 'a{} != {} && '.format(m, n)
		str2 += 'a{} = {} || '.format(m, n)
	str = str[:-3]
	str += ') -> X (r{} = r{})'.format(n, n)
	str2 = str2[:-3]
	str2 += ') -> X r{} = 0'.format(n, n)
	env_safe |= set([str,str2])

# env_safe |= set(['r1=0'])
sys_prog = set()
env_prog = set()

## Liveness - Sys

for n in range(1, max_requests + 1):
	sys_prog |= set(['r{} = 0'.format(n)])

## Liveness - Env
str = ''
for n in range(1, max_service + 1):
	str += 'available = {} || '.format(n)
str = str[:-3]
env_prog |= set([str])

env_init = set()
sys_init = set()

# Create a GR(1) specification
specs = spec.GRSpec(env_vars=env_vars, sys_vars=sys_vars, env_init=env_init,sys_init=sys_init,env_safety=env_safe, sys_safety=sys_safe, env_prog=set(), sys_prog=set())
specs.moore = False
specs.plus_one = False
# specs.qinit = '\E \A'  # Moore initial condition synthesized too

#
# Controller synthesis
#
# At this point we can synthesize the controller using one of the available
# methods.
#
start = time.time()
ctrl = synth.synthesize(specs,solver='slugs')
print(ctrl)
t = time.time()
print('Synth Time: {}'.format(t-start))
