import itertools
import os
import copy
import subprocess

def powerset(s):
    x = len(s)
    a = []
    for i in range(1,1<<x):
        a.append({s[j] for j in range(x) if (i &(1<<j))})
    return a

def write_request_handler(infile=None):
    max_requests = 6
    num_vertiports = 4
    max_service = 3
    if infile == None:
        infile = 'request_handler_example'
        filename = infile + '.structuredslugs'
    else:
        filename = infile + '.structuredslugs'
    file = open(filename, 'w')
    file.write('[INPUT]\n')
    for n in range(1,max_requests+1):
        file.write('r{}:0...{}\n'.format(n, num_vertiports))
    file.write('available:0...{}\n'.format(max_service))
    file.write('\n[OUTPUT]\n')
    for n in range(max_service):
        file.write('a{}:0...{}\n'.format(n, max_requests))
    file.write('\n[ENV_INIT]\n')
    file.write('\n[SYS_INIT]\n')
    file.write('\n[SYS_TRANS]\n')
    for n in range(max_service):
        str = 'available = {} -> '.format(n)
        disallowed_combos = itertools.combinations(range(max_service), max_service - n)
        for request_combo in disallowed_combos:
            str += '!('
            for request in request_combo:
                str += 'a{} != 0 \/ '.format(request)
            str = str[:-3]
            str += ') \/ '
        str = str[:-3]
        str += '\n'
        file.write(str)
        for m in range(1,max_service+1):
            possible_request_combo = powerset(range(1,max_requests+1))
            for request_set in possible_request_combo:
                str2 = 'available = {} /\ '.format(m)
                str2 += '('
                for request in request_set:
                    str2 += 'r{} != 0 /\ '.format(request)
                for request in set(range(1,max_requests+1)).difference(request_set):
                    str2 += 'r{} = 0 /\ '.format(request)
                str2 = str2[:-3]
                str2 += ') -> ('
                allowed_available_combos = list(itertools.combinations(range(max_service),m))
                for k in allowed_available_combos:
                    accept_available_combos = list(itertools.product(k,list(request_set)))
                    for accept_set in accept_available_combos:
                        str2+= 'a{} = {} \/ '.format(accept_set[0],accept_set[1])
                    str2 = str2[:-3]
                    str2 += ') \/ ('
                str2 = str2[:-4]
                str2 += '\n'
                file.write(str2)
    all_combos = powerset(range(max_service))
    prev_rhs = ''
    for n in range(1,max_service+1):
        request_combo = itertools.combinations(range(1,max_requests+1),max_requests-n+1)
        str = 'available = {} ->'.format(n)
        rhs = ' ( ('
        for combos in all_combos:
            if len(combos) == n:
                for request in combos:
                    rhs += 'a{} != 0 /\ '.format(request)
                rhs = rhs[:-3]
                rhs += ') \/ ('
        rhs = rhs[:-4]
        rhs += ') '
        for request_set in request_combo:
            rhs += '\/ ('
            for request in request_set:
                rhs+= 'r{} = 0 /\ '.format(request)
            rhs = rhs[:-3]
            rhs += ')'
        str += rhs
        str += prev_rhs
        prev_rhs = copy.deepcopy(rhs)
        prev_rhs = '/\ ('+prev_rhs
        prev_rhs += ')'
        str += '\n'
        file.write(str)
    all_combos = itertools.combinations(range(max_service),2)
    for combos in all_combos:
        file.write('a{} != a{} \/ (a{} = 0 \/ a{} = 0)\n'.format(combos[0],combos[1],combos[0],combos[1]))
    for n in range(1,max_requests+1):
        str = 'r{} = 0 ->!('.format(n)
        for m in range(max_service):
            str += 'a{} = {} \/ '.format(m,n)
        str = str[:-3]
        str += ')\n'
        file.write(str)
    file.write('\n[ENV_TRANS]\n')
    for n in range(1,max_requests+1):
        str = 'r{} != 0 /\ ('.format(n, n)
        str2 = 'r{} != 0 /\ ('.format(n, n)
        for m in range(max_service):
            str += 'a{} != {} /\ '.format(m,n)
            str2 += 'a{} = {} \/ '.format(m,n)
        str = str[:-3]
        str += ') -> r{}\' = r{}\n'.format(n, n)
        str2 = str2[:-3]
        str2 += ') -> r{}\' = 0\n'.format(n, n)
        file.write(str)
        file.write(str2)
    file.write('\n[SYS_LIVENESS]\n')
    for n in range(1,max_requests+1):
        file.write('r{} = 0\n'.format(n))
    file.write('\n[ENV_LIVENESS]\n')
    str = ''
    for n in range(1, max_service + 1):
        str += 'available = {} \/ '.format(n)
    str = str[:-3]
    file.write(str)
    file.close()
    # os.system(
    #     'python /Users/suda/Documents/slugs/tools/StructuredSlugsParser/compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
    #
    # print('Computing controller...')
    # sp = subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > ' + infile + '.json',
    #                       shell=True, stdout=subprocess.PIPE)
    # sp.wait()


write_request_handler('RawFile')