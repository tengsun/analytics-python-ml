def loadDataSet():
	dataSet = [['r', 'z', 'h', 'j', 'p'], 
				['z', 'y', 'x', 'w', 'v', 'u', 't', 's'],
				['z'],
				['r', 'x', 'n', 'o', 's'],
				['y', 'r', 'x', 'z', 'q', 't', 'p'],
				['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]
	return dataSet

def createInitSet(dataSet):
	resultDict = {}
	for tx in dataSet:
		resultDict[frozenset(tx)] = 1
	return resultDict

# define tree node data structure
class treeNode:
	# init function
	def __init__(self, nameValue, numOccur, parentNode):
		self.name = nameValue
		self.count = numOccur
		# link to similar node
		self.nodeLink = None
		self.parent = parentNode
		self.children = {}

	# increase count value
	def inc(self, numOccur):
		self.count += numOccur

	# display tree structure
	def disp(self, ind = 1):
		print ' ' * ind, self.name, self.count, '(',id(self),')'
		for child in self.children.values():
			child.disp(ind + 1)

# create FP growth tree
def createTree(initSet, minSupp = 1):
	# create init header table as {'x': 4}
	headerTable = {}
	for tx in initSet:
		for item in tx:
			headerTable[item] = headerTable.get(item, 0) + initSet[tx]
	
	# delete element if < min support value
	for k in headerTable.keys():
		if headerTable[k] < minSupp:
			del(headerTable[k])

	# return none if nothing meet requirement
	freqItemSet = set(headerTable.keys())
	if len(freqItemSet) == 0:
		return None, None

	# re-org header table to {'x': [4, <node>]}
	for k in headerTable:
		headerTable[k] = [headerTable[k], None]
	printHeader(headerTable)

	resultTree = treeNode('[*]', 1, None)
	for txSet, count in initSet.items():
		txItemDict = {}
		for item in txSet:
			# only filter the frequent items
			if item in freqItemSet:
				txItemDict[item] = headerTable[item][0]
		if len(txItemDict) > 0:
			# sort items by count values in header table
			orderedItems = [v[0] for v in sorted(txItemDict.items(), \
				key = lambda x: x[1], reverse = True)]
			print 'tx dict:', txItemDict, 'sorted:', orderedItems
			updateTree(orderedItems, resultTree, headerTable, count)

	printHeader(headerTable)
	return resultTree, headerTable

def updateTree(items, inTree, headerTable, count):
	# increase count if node exists
	if items[0] in inTree.children:
		print 'increase %s count: %d+1' % (items[0], inTree.children[items[0]].count)
		inTree.children[items[0]].inc(count)
	# create new node if not exists
	else:
		print 'create new tree node: %s' % items[0]
		inTree.children[items[0]] = treeNode(items[0], count, inTree)
		if headerTable[items[0]][1] == None:
			headerTable[items[0]][1] = inTree.children[items[0]]
		else:
			updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
		printHeader(headerTable, items[0])
	# inTree.disp()

	# recursive process rest items
	if len(items) > 1:
		updateTree(items[1::], inTree.children[items[0]], headerTable, count)

def updateHeader(currNode, targetNode):
	while (currNode.nodeLink != None):
		currNode = currNode.nodeLink
	currNode.nodeLink = targetNode

def printHeader(headerTable, item = None):
	if item != None:
		items = [item]
	else:
		items = headerTable.keys()
	
	for k in items:
		currNode = headerTable[k][1]
		info = str(currNode) if (currNode == None) else \
			currNode.name + ':' + str(currNode.count) + '(' + str(id(currNode)) + ')'
		while (currNode != None and currNode.nodeLink != None):
			currNode = currNode.nodeLink
			info += ' -> ' + \
			currNode.name + ':' + str(currNode.count) + '(' + str(id(currNode)) + ')'
		print '[%s:%s] -> %s' % (k, headerTable[k][0], info)

# find conditional pattern base
def ascendTree(leafNode, prefixPath):
	if leafNode.parent != None:
		#print 'ascend tree node:', leafNode.name, leafNode.count
		prefixPath.append(leafNode.name)
		ascendTree(leafNode.parent, prefixPath)

def findPrefixPath(basePattern, treeNode):
	condPattBases = {}
	while treeNode != None:
		prefixPath = []
		ascendTree(treeNode, prefixPath)
		
		print 'prefix path:', prefixPath
		if len(prefixPath) > 1:
			condPattBases[frozenset(prefixPath[1:])] = treeNode.count
		
		# check next node by link pointer
		treeNode = treeNode.nodeLink
	return condPattBases

def mineTree(inTree, headerTable, minSupp, prefix, freqItemList):
	# sort items in header table by count
	sortedItems = \
		[v[0] for v in sorted(headerTable.items(), key = lambda p: p[1])]

	for item in sortedItems:
		newFreqSet = prefix.copy()
		newFreqSet.add(item)
		freqItemList.append(newFreqSet)

		# find prefix path by item
		condPattBases = findPrefixPath(item, headerTable[item][1])
		# reuse func to create conditional fp tree
		myCondTree, myHead = createTree(condPattBases, minSupp)
		print 'conditional tree for:', newFreqSet
		if myCondTree != None:
			myCondTree.disp(1)

		if myHead != None:
			mineTree(myCondTree, myHead, minSupp, newFreqSet, freqItemList)
