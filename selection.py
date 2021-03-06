from random import Random
from collections import defaultdict
from itertools import combinations
from util import Progress 

def iterbits(h):
    z = 0
    result = []
    while h > 0:
        b = 1 << z
        if h & b == b:
            yield z
            h = h & ~b
        z += 1

def bits(h):
    return list(iterbits(h))

def invert(s):
    result = [ None ] * len(s)
    for h in range(1, len(s)):
        index = s[h]
        if h == 1 << index:
            result[h] = index
        else:
            subset = h & ~(1 << index)
            result[h] = result[subset]
    return tuple(result)

def trace(s, x):
    result = []
    while x != 0:
        v = s[x]
        result.append(v)
        x = x & ~(1<<v)
    return result

def cotrace(s, x):
    result = []
    while x != 0:
        result.append(x)
        v = s[x]
        x = x & ~(1 << v)
    return result

def tabulate(n, f):
    result = [None]
    for i in range(1, 1<<n):
        b = bits(i)
        result.append(f(b))
    return tuple(result)

def canonical(s):
    z = len(bits(len(s)-1))
    t = trace(s, (1 << z) - 1)
    mapping = t[:]
    result = list(s)
    for (i, x) in enumerate(t):
        mapping[x] = i
    for i in range(1, 1<<z):
        mb = sum((1 << mapping[b] for b in bits(i)))
        result[mb] = mapping[s[i]]
    return tuple(result)

def findloop(f, x):
    visited =  {}
    j = 0
    while not x in visited:
        visited[x] = j
        j += 1
        x = f(x)
    v = visited[x]
    return (v, j - v, x)

def sets_by_selection(s):
    result = defaultdict(lambda: [])
    for i in range(1, len(s)):
        result[s[i]].append(i)
    return result

def closed_union(s):
    sbs = sets_by_selection(s)
    for (y, xs) in sbs.items():
        for (x1, x2) in combinations(xs, 2):
            if s[x1 | x2] != y:
                return False
    return True

def closed_intersection(s):
    sbs = sets_by_selection(s)
    for (y, xs) in sbs.items():
        for (x1, x2) in combinations(xs, 2):
            if s[x1 & x2] != y:
                return False
    return True

def randsel(R, N):
    result = [None]
    for i in range(1, 1<<N):
        b = bits(i)
        result.append(R.choice(b))
    return tuple(result)

def always_before(s):
    before = set()
    for i in range(1, len(s)):
        b = bits(i)
        v = s[i]
        b.remove(v)
        for o in b:
            before.add((v, o))
    return [(x, y) for (x, y) in before if not (y, x) in before]

def subseq_sets(s, h):
    t = trace(s, h)
    result = set()
    for i in range(len(t)):
        for j in range(i+1, len(t)+1):
            st = t[i:j]
            result.add(sum((1<<b for b in st)))
    return result

def additional_sets(s, x, old_sets): 
    return set((im for im in subseq_sets(s, x) if not im in old_sets))

def blr_nextstate(s, visited, candidates, chains):
    best = None
    best_addsets = None
    maxlen = -1
    for c in candidates:
        addsets = additional_sets(s, c, visited)
        if len(addsets) > maxlen:
            best = c
            best_addsets = addsets
            maxlen = len(addsets)
    for addset in best_addsets:
        visited.add(addset)
    candidates2 = [c for c in candidates if not c in visited]
    candidates.clear()
    candidates.extend(candidates2)
    chains.append(trace(s, best))

def build_list_repr(s):
    candidates = list(range(1, len(s)))
    candidates.sort(key=lambda x: -x)
    state = (s, set(), candidates, [])
    while len(candidates) > 0:
        blr_nextstate(*state)
    return state[3]


def check_contiguous_pair(s, parent, child):
    if parent & child == 0:
        return True
    t = trace(s, parent)
    prevInChild = False
    foundUpEdge = False
    for x in t:
        inChild = (1 << x) & child != 0
        isEdge = inChild and not prevInChild
        if foundUpEdge and isEdge:
            return False
        foundUpEdge |= isEdge
        prevInChild = inChild
    return True

def check_contiguous(s, h):
    t = bits(h)
    if len(t) == 1 or 1 << len(t) == len(s):
        return False
    for i in range(1, len(s)):
        if not check_contiguous_pair(s, i, h):
            return False
    return True

def contiguous_elems(s):
    for h in range(1, len(s)):
        if check_contiguous(s, h):
            yield h

def alpha(n):
    def maxud(bs):
        return max((b for b in bs if not b-1 in bs))
    return tabulate(n, maxud)

def maximize(state, f, x):
    v = f(x)
    if state[1] == None or v >= state[1]:
        state[0] = x
        state[1] = v
    
def split_trace_before_and_after(s, h, t):
    isAfter = False
    before = []
    after = []
    for y in t:
        if (1 << y) & h != 0:
            isAfter = True
        else:
            if isAfter:
                after.append(y)
            else:
                before.append(y)
    return (tuple(before), tuple(after))

def is_contractible(s, cont):
    m = {}
    for h in range(1, len(s)):
        if h & cont == 0:
            continue
        tba = split_trace_before_and_after(s, cont, trace(s, h))
        index = h & ~cont
        if index in m:
            prevTba = m[index]
            if prevTba != tba:
                return False
        m[index] = tba
    return True

def has_contractible_subset(s):
    for cont in contiguous_elems(s):
        if is_contractible(s, cont):
            return True
    return False

def contractible_subsets(s):
    for cont in contiguous_elems(s):
        if is_contractible(s, cont):
            yield cont

def generate_selections(R, N, L, selSet):
    loopProg = Progress(1)
    setProg = Progress(300)
    for i in range(L):
        s = randsel(R, N)
        l = findloop(invert, s)
        if l[1] == 2:
            s = l[2]
            selSet.add(canonical(s))
            selSet.add(canonical(invert(s)))
        loopProg.update("Loop: " + str(i // 10000))
        setProg.update("#: " + str(len(selSet)))

def terminal_elements(s):
    N = len(bits(len(s) - 1))
    candidates = set(range(N))
    for h in range(1, len(s)):
        t = trace(s, h)
        for (i, x) in enumerate(t):
            if i != 0 and i != len(t) - 1:
                candidates.discard(x)
    return candidates

def generate_all_rsms(N):
    cs = list(combinations(range(N), 2))
    def generate_rsms(cs, i, current):
        if i == len(cs):
            yield current
        else:
            (a,b)=cs[i]
            current.append((0, a, b))
            for r in generate_rsms(cs, i+1, current):
                yield r
            current.pop()
            current.append((0, b, a))
            for r in generate_rsms(cs, i+1, current):
                yield r
            current.pop()
            current.append((1, a, b))
            for r in generate_rsms(cs, i+1, current):
                yield r
            current.pop()
            current.append((1, b,a))
            for r in generate_rsms(cs, i+1, current):
                yield r
            current.pop()
    def build_dominators(rsm):
        dom0 = defaultdict(lambda:set())
        dom1 = defaultdict(lambda:set())
        dom = (dom0, dom1)
        for (i, a, b) in rsm:
            dom[i][b].add(a)
        return dom
    def survivors(dom, vals):
        s1 = set((v for v in vals if len(vals & dom[v]) == 0))
        return s1
    def survivors2(dom1, dom2, vals):
        return survivors(dom2, survivors(dom1, vals))
    def dom_to_sel(N, dom1, dom2):
        result = [None] * (1 << N)
        for i in range(1, 1<<N):
            b = set(bits(i))
            surv = survivors2(dom1, dom2, b)
            if len(surv) != 1:
                return None
            result[i] = next(iter(surv))
        return tuple(result)
    for rsm in generate_rsms(cs, 0, []):
        doms = build_dominators(rsm)
        s = dom_to_sel(N, doms[0], doms[1])
        if s != None:
            yield s

