import math
import cmath
from numbers import Number
import difflib
import numpy as np

class UnorderedList(list):
    pass

def checktypes(*types):
    def decorator(f):
        def wrapper(*args):
            assert len(types)==len(args), 'wrong number of types'
            for (a, t) in zip(args,types):
                assert isinstance(a, t), 'arg {} does not match {}'.format(a, t)
            return f(*args)
        return wrapper
    return decorator

@checktypes(int, int)
def comp_int(a, b):
    if a==b:
        return 1.0
    return 0.0

@checktypes(float, float)
def comp_float(a, b):
    if math.isclose(a, b, rel_tol=1e-2, abs_tol=1e-4):
        return 1.0
    return 0.0

@checktypes(complex, complex)
def comp_complex(a, b):
    if cmath.isclose(a, b, rel_tol=1e-2, abs_tol=1e-4):
        return 1.0
    return 0.0

@checktypes(Number, Number)
def comp_num(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return comp_float(a, b)
    if isinstance(a, int) and isinstance(b, int):
        return comp_int(a, b)
    if isinstance(a, int) and isinstance(b, float):
        if b.is_integer():
            return comp_int(a, int(b))
        return comp_float(float(a), b)
    if isinstance(a, float) and isinstance(b, int):
        return comp_num(b, a)
    if isinstance(a, complex) and isinstance(b, complex):
        return comp_complex(a, b)
    if isinstance(a, complex):
        return comp_num(b, a)
    if isinstance(b, complex):
        if b.imag == 0.0:
            return comp_num(b.real, a)
        return 0.0
    if isinstance(a, (np.int64, np.int32)):
        return comp_num(int(a), b)
    if isinstance(b, (np.int64, np.int32)):
        return comp_num(a, int(b))

    raise TypeError('Unsupported Number Comparaison')

@checktypes(str, str)
def comp_str(a, b):
    return (difflib.SequenceMatcher(None, a, b).ratio() * difflib.SequenceMatcher(None, b, a).ratio())**2

def shorter_first(A, B):
    if len(A) > len(B):
        return B, A
    return A, B

def compute_mapping(A, B):
    A, B = shorter_first(A, B)

    similarities = []
    for i, elemA in enumerate(A):
        for j, elemB in enumerate(B):
            similarities.append({
                'a': i,
                'b': j,
                'similarity': comp(elemA, elemB)
            })
    
    similarities.sort(key=lambda elem: abs(elem['a'] - elem['b']))
    similarities.sort(key=lambda elem: 1 - elem['similarity'])

    flagA = len(A)*[False]
    flagB = len(B)*[False]
    res = []
    for similarity in similarities:
        if (not flagA[similarity['a']]) and (not flagB[similarity['b']]):
            flagA[similarity['a']] = True
            flagB[similarity['b']] = True
            res.append(similarity)

    return res

@checktypes(list, list)
def comp_list(a, b):
    a, b = shorter_first(a, b)
    if len(a) == 0 or len(b) == 0:
        return 1.0/(max(len(b), len(a))+1)

    similarities = compute_mapping(a, b)

    S = sum([similarity['similarity'] for similarity in similarities])
    count = len(similarities)

    order = min(len(a), len(b)) * [None]
    for similarity in similarities:
        order[similarity['a']] = similarity['b']

    def countContiguousSwapOperation(L):
        count = 0
        for i in range(len(L)):
            for j in range(len(L)-i-1):
                if L[j] > L[j+1]:
                    L[j], L[j+1] = L[j+1], L[j]
                    count += 1
        return count

    orderOperation = countContiguousSwapOperation(order)
    orderFactor = orderOperation/(len(order)**2)

    count += len(b) - len(a)
    return S/count * (1-orderFactor)

@checktypes(UnorderedList, UnorderedList)
def comp_unordered_list(a, b):
    a, b = shorter_first(a, b)
    if len(a) == 0 or len(b) == 0:
        return 1.0/(max(len(b), len(a))+1)

    similarities = compute_mapping(list(a), list(b))

    S = sum([similarity['similarity'] for similarity in similarities])
    count = len(similarities)

    count += len(b) - len(a)
    return S/count

@checktypes(set, set)
def comp_set(a, b):
    return comp(UnorderedList(a), UnorderedList(b))

@checktypes(dict, dict)
def comp_dict(a, b):
    a, b = shorter_first(a, b)
    if len(a) == 0 or len(b) == 0:
        return 1.0/(max(len(b), len(a))+1)
    keysA = list(a.keys())
    keysB = list(b.keys())
    similarities = compute_mapping(keysA, keysB)

    S = 0
    count = 0
    for similarity in similarities:
        kA = keysA[similarity['a']]
        kB = keysB[similarity['b']]
        simK = similarity['similarity']
        simV = comp(a[kA], b[kB])
        S += (simK + simV) / 2
        count += 1

    count += len(b) - len(a)
    return S/count

def comp_bool_str(b, s):
    if isinstance(b, str):
        return comp_bool_str(s, b)
    assert isinstance(b, bool), "b must be a boolean"
    assert isinstance(s, str), "s must be a string"
    if str(b).lower() == s.lower().strip():
        return 0.5
    return 0.0

@checktypes(tuple, tuple)
def comp_tuple(a, b):
    return comp_list(list(a), list(b))


def comp(a, b):
    typeGrade = 0.0
    if isinstance(a, (float, complex)) and isinstance(b, (float, complex)):
        typeGrade = 1.0
    if isinstance(a, (int, np.int64, np.int32)) and isinstance(b, (int, np.int64, np.int32)):
        typeGrade = 1.0
    if (type(a) == type(b)):
        typeGrade = 1.0
    
    valueGrade = 0.0
    if (isinstance(a, str) and isinstance(b, bool)) or (isinstance(b, str) and isinstance(a, bool)):
        valueGrade = comp_bool_str(a, b)
    elif isinstance(a, (int, float, complex, np.int32, np.int64)) and isinstance(b, (int, float, complex, np.int32, np.int64)):
        valueGrade = comp_num(a, b)
    elif isinstance(a, str) and isinstance(b, str):
        valueGrade = comp_str(a, b)
    elif isinstance(a, UnorderedList) and isinstance(b, UnorderedList):
        valueGrade = comp_unordered_list(a, b)
    elif isinstance(a, list) and isinstance(b, list):
        valueGrade = comp_list(a, b)
    elif isinstance(a, set) and isinstance(b, set):
        valueGrade = comp_set(a, b)
    elif isinstance(a, dict) and isinstance(b, dict):
        valueGrade = comp_dict(a, b)
    elif isinstance(a, tuple) and isinstance(b, tuple):
        valueGrade = comp_tuple(a, b)
    
    return 0.9 * valueGrade + 0.1 * typeGrade

if __name__ == "__main__":
    print(comp(np.float64(42), 42.0))
    print(isinstance(np.float64(42), float))
    print(comp(np.int64(42), 42))
    print(comp(42, np.int64(42)))
    print(comp(np.int64(42), np.int64(42)))
    print(comp(list(np.array([1, 2, 3]) + np.array([3, 2, 1])), [4, 4, 4]))
    print(comp_num(np.int64(42), 42))

