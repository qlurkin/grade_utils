from numbers import Number
import difflib
from frozendict import frozendict

def checktypes(*types):
	def decorator(f):
		def wrapper(*args):
			assert len(types)==len(args), 'wrong number of types'
			for (a, t) in zip(args,types):
				assert isinstance(a, t), 'arg {} does not match {}'.format(a, t)
			return f(*args)
		return wrapper
	return decorator

def getHashableVersion(a):
	if isinstance(a, int):
		return a
	if isinstance(a, str):
		return a
	if isinstance(a, list):
		hashableElem = []
		for elem in a:
			hashableElem.append(getHashableVersion(elem))
		return tuple(hashableElem)
	if isinstance(a, set):
		return frozenset(a)
	if isinstance(a, tuple):
		hashableElem = []
		for elem in a:
			hashableElem.append(getHashableVersion(elem))
		return tuple(hashableElem)
	if isinstance(a, dict):
		hashableValuedDict = {}
		for key, value in a.items():
			hashableValuedDict[key]=getHashableVersion(value)
		return frozendict(hashableValuedDict)
	raise TypeError('Unsupported Type for Hashable Convertion')

@checktypes(Number, Number)
def comp_int(a, b):
	if a > b:
		return comp_int(b, a)
	
	if b-a > b/10:
		return 0
	
	return (a-b)*10/b+1

@checktypes(str, str)
def comp_str(a, b):
	return difflib.SequenceMatcher(None, a, b).ratio()

@checktypes(list, list)
def comp_list(a, b):	
	if len(a) > len(b):
		return comp_list(b, a)
	
	similarities = []
	for i, elemA in enumerate(a):
		for j, elemB in enumerate(b):
			similarities.append({
				'a': i,
				'b': j,
				'similarity': comp(elemA, elemB)
			})
	
	similarities.sort(key=lambda elem: abs(elem['a'] - elem['b']))
	similarities.sort(key=lambda elem: 1 - elem['similarity'])

	#print(similarities)

	flagA = len(a)*[False]
	flagB = len(b)*[False]
	order = len(a)*[None]
	S = 0
	count = 0
	for similarity in similarities:
		if (not flagA[similarity['a']]) and (not flagB[similarity['b']]):
			S += similarity['similarity']
			count += 1
			flagA[similarity['a']] = True
			flagB[similarity['b']] = True
			order[similarity['a']] = similarity['b']
			#print(similarity['a'], similarity['b'])

	#print(flagA)
	#print(flagB)
	#print(order)

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
	#print('order factor:', orderFactor)

	count += len(b) - len(a)
	return S/count * (1-orderFactor)

@checktypes(set, set)
def comp_set(a, b):
	if len(a) > len(b):
		return comp_set(b, a)

	for elem in a:
		pass

	

def comp(a, b):
	if type(a) != type(b):
		return 0
	if isinstance(a, int):
		return comp_int(a, b)
	if isinstance(a, str):
		return comp_str(a, b)
	if isinstance(a, list):
		return comp_list(a, b)
	raise TypeError('Unsupported Type for Comparaison: {}'.format(type(a)))


if __name__ == "__main__":
	n = 100
	print(comp(list(range(1, n)), list(range(n-1, 0, -1))))
	print(comp([1, 1, 1], [1, 1, 1]))