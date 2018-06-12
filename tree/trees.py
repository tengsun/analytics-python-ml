from math import log
import operator
import pickle
import treePlotter

# create data to test fish
def createDataSet():
    dataSet = [[1, 1, 'yes'],
               [1, 1, 'yes'],
               [1, 0, 'no'],
               [0, 1, 'no'],
               [0, 1, 'no']]
    labels = ['no surfacing', 'flippers']
    return dataSet, labels

# calculate shannon entropy
def calculateEntropy(dataSet):
    numEntries = len(dataSet)
    labelCounts = {}
    for vector in dataSet:
        # use last column label to calculate
        curr = vector[-1]
        if curr not in labelCounts.keys():
            labelCounts[curr] = 0
        labelCounts[curr] += 1
    entropy = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key]) / numEntries
        entropy -= prob * log(prob, 2)
        # print "key: %s, probability: %f, log func: %f" \
        #    %(key, prob, log(prob, 2))
    return entropy

# split data set by axis & value
def splitDataSet(dataSet, axis, value):
    # create new data set to avoid change on original one
    reducedDataSet = []
    for vector in dataSet:
        if vector[axis] == value:
            reducedVector = vector[:axis]
            reducedVector.extend(vector[axis + 1:])
            reducedDataSet.append(reducedVector)
    return reducedDataSet

# choose the best split feature
def chooseBestSplitFeature(dataSet):
    # last column is the class label
    numFeatures = len(dataSet[0]) - 1
    baseEntropy = calculateEntropy(dataSet)
    print "original entropy: %f" %(baseEntropy)
    bestInfoGain = 0.0
    bestFeature = -1
    
    # iterate features and calculate entropy
    for i in range(numFeatures):
        # convert column i data to feature list
        featureList = [example[i] for example in dataSet]
        # retrieve unique values of each feature
        uniqueVals = set(featureList)
        newEntropy = 0.0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet) / float(len(dataSet))
            newEntropy += prob * calculateEntropy(subDataSet)
        reducedEntropy = baseEntropy - newEntropy
        print "curr index: %d, new entropy: %f, reduced entropy: %f" \
            %(i, newEntropy, reducedEntropy)
        
        if (reducedEntropy > bestInfoGain):
            bestInfoGain = reducedEntropy
            bestFeature = i
    
    return bestFeature

# find the top class in the list
def majorityCount(classList):
    classCount = {}
    for vote in classList:
        if vote not in classCount.keys():
            classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.iteritems(), 
        key = operator.itemgetter(1), reverse = True)
    return sortedClassCount[0][0]

# input data set and feature labels
def createTree(dataSet, featureLabels):
    classList = [example[-1] for example in dataSet]
    
    # stop and return if all classes are the same
    if classList.count(classList[0]) == len(classList):
        return classList[0]
    
    # check if all the features have been used up
    # return majority class in case not classified
    if len(dataSet[0]) == 1:
        return majorityCount(classList)
    
    # select best feature and label
    bestFeature = chooseBestSplitFeature(dataSet)
    bestFeatureLabel = featureLabels[bestFeature]
    print 'best feature is: %d - %s' % (bestFeature, bestFeatureLabel)
    myTree = {bestFeatureLabel: {}}
    
    del(featureLabels[bestFeature])
    featureValues = [example[bestFeature] for example in dataSet]
    uniqueValues = set(featureValues)
    for value in uniqueValues:
        subLabels = featureLabels[:]
        
        # iterate to construct sub-trees
        myTree[bestFeatureLabel][value] = \
            createTree(splitDataSet(dataSet, bestFeature, value), subLabels)
    
    return myTree

# classification using decision tree algorithm
# featureLabels and testVector are consistent
def classify(inputTree, featureLabels, testVector):
    currKey = inputTree.keys()[0]
    currDict = inputTree[currKey]
    
    # get correct feature index by current key
    featureIndex = featureLabels.index(currKey)
    for key in currDict.keys():
        if testVector[featureIndex] == key:
            if type(currDict[key]).__name__ == 'dict':
                classLabel = classify(currDict[key], featureLabels, testVector)
            else:
                classLabel = currDict[key]
    return classLabel

# store tree to local file
def storeTree(inputTree, filename):
    fw = open(filename, 'w')
    pickle.dump(inputTree, fw)
    fw.close()

# restore tree from local file
def grabTree(filename):
    fr = open(filename)
    return pickle.load(fr)

## lenses doctor query test
def checkLenses():
    fr = open('data/lenses.txt')
    lenses = [line.strip().split('\t') for line in fr.readlines()]
    lensesLabels = ['age', 'prescript', 'astigmatic', 'tearRate']
    lensesTree = createTree(lenses, lensesLabels)
    print lensesTree
    treePlotter.createPlot(lensesTree)
