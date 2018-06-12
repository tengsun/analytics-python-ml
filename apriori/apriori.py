def loadDataSet():
	return map(set, [[1,3,4], [2,3,5], [1,2,3,5], [2,5]])

# create collection of items with size = 1
def createC1(dataSet):
	C1 = []
	for tx in dataSet:
		for item in tx:
			if not [item] in C1:
				C1.append([item])
	C1.sort()
	return map(frozenset, C1)

# scan dataSet with candidates, filter by minSupport
def scanDataSet(dataSet, Ck, minSupport):
	# candidate count dictionary
	canCount = {}
	for tx in dataSet:
		for can in Ck:
			if can.issubset(tx):
				if not canCount.has_key(can):
					canCount[can] = 1
				else:
					canCount[can] += 1
	
	# calculate support data and filter
	numItems = float(len(dataSet))
	supportList = []
	supportData = {}
	for key in canCount:
		support = canCount[key] / numItems
		if support >= minSupport:
			supportList.insert(0, key)
		supportData[key] = support

	return supportList, supportData

# create Ck by Lk(frequent item sets) and k(set size)
def aprioriGen(Lk, k):
	resultList = []
	lenLk = len(Lk)
	for i in range(lenLk):
		for j in range(i + 1, lenLk):
			# merge if the first k-2 items are same
			L1 = list(Lk[i])[:k - 2]
			L2 = list(Lk[j])[:k - 2]
			L1.sort()
			L2.sort()
			# print '%s | %s, k = %d, %s | %s' \
			#	% (Lk[i], Lk[j], k, L1, L2)
			if L1 == L2:
				resultList.append(Lk[i] | Lk[j])
	return resultList

def apriori(dataSet, minSupport = 0.5):
	C1 = createC1(dataSet)
	L1, supportData = scanDataSet(dataSet, C1, minSupport)
	L = [L1]
	k = 2
	# C1->L1, C2->L2, ..., Ck->Lk
	while (len(L[k - 2]) > 0):
		Ck = aprioriGen(L[k - 2], k)
		Lk, Sk = scanDataSet(dataSet, Ck, minSupport)
		supportData.update(Sk)
		L.append(Lk)
		k += 1
	return L, supportData

# generate association rules by freqSet L and supportData
def generateRules(L, supportData, minConf = 0.7):
	ruleList = []
	# can not gen rule with only one item, so starts from 1
	for i in range(1, len(L)):
		for freqSet in L[i]:
			H1 = [frozenset([item]) for item in freqSet]
			print 'i = %d, freqSet = %s, H1 = %s' % (i, freqSet, H1)
			if (i > 1):
				rulesFromConseq(freqSet, H1, supportData, ruleList, minConf)
			else:
				calcConf(freqSet, H1, supportData, ruleList, minConf)
	return ruleList

def calcConf(freqSet, H, supportData, ruleList, minConf):
	prunedH = []
	for conseq in H:
		# P -> H = support(P | H) / support(P)
		conf = supportData[freqSet] / supportData[freqSet - conseq]
		if conf >= minConf:
			print freqSet - conseq, '-->', conseq, 'conf:', conf
			ruleList.append((freqSet - conseq, conseq, conf))
			prunedH.append(conseq)
	return prunedH

def rulesFromConseq(freqSet, H, supportData, ruleList, minConf):
	m = len(H[0])
	if (len(freqSet) > (m + 1)):
		Hmp1 = aprioriGen(H, m + 1)
		Hmp1 = calcConf(freqSet, Hmp1, supportData, ruleList, minConf)
		if (len(Hmp1) > 1):
			rulesFromConseq(freqSet, Hmp1, supportData, ruleList, minConf)
