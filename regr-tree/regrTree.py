import numpy as np

class treeNode():
    def __init__(self, feature, value, left, right):
        featureToSplitOn = feature
        valueOfSplit = value
        leftBranch = left
        rightBranch = right

def loadDataSet(file):
    dataMat = []
    fr = open(file)
    for line in fr.readlines():
        currLine = line.strip().split('\t')
        # reformat values to float type
        floatLine = map(float, currLine)
        dataMat.append(floatLine)
    return dataMat

# calculate the y mean as leaf node
def regLeaf(dataSet):
    return np.mean(dataSet[:, -1])

# calculate total variance of dataSet
def regErr(dataSet):
    return np.var(dataSet[:, -1]) * np.shape(dataSet)[0]

# determine the best feature to split dataSet
def chooseBestSplit(dataSet, leafType = regLeaf, errType = regErr, ops = (1, 4)):
    m, n = np.shape(dataSet)
    S = errType(dataSet)
    tolS = ops[0]   # minimum variance decrease as good split
    tolN = ops[1]   # minimum sample size in dataSet to split
    
    # return as leaf node if all feature values are equal
    if len(set(dataSet[:, -1].T.tolist()[0])) == 1:
        return None, leafType(dataSet)
    
    bestS = np.inf
    bestIndex = 0
    bestValue = 0
    
    # iterate feature by index
    for featureIdx in range(n - 1):
        # iterate in current feature value set
        for splitVal in set(dataSet[:, featureIdx]):
            # binary split as left and right matrix by input splitVal
            mat0, mat1 = binSplitDataSet(dataSet, featureIdx, splitVal)
            if (np.shape(mat0)[0] < tolN) or (np.shape(mat1)[0] < tolN):
                continue
            
            # calculate the new total variance of left and right matrix
            newS = errType(mat0) + errType(mat1)
            if newS < bestS:
                bestIndex = featureIdx
                bestValue = splitVal
                bestS = newS
    
    # return as leaf node if split is not good enough
    if (S - bestS) < tolS:
        return None, leafType(dataSet)
    
    # return as leaf node if dataSet size is too small
    mat0, mat1 = binSplitDataSet(dataSet, bestIndex, bestValue)
    if (np.shape(mat0)[0] < tolN) or (np.shape(mat1)[0] < tolN):
        return None, leafType(dataSEt)
    
    return bestIndex, bestValue

# binary split data set by comparing target feature to specific value
def binSplitDataSet(dataSet, feature, value):
    mat0 = dataSet[np.nonzero(dataSet[:, feature] > value)[0], :][0]
    mat1 = dataSet[np.nonzero(dataSet[:, feature] <= value)[0], :][0]
    return mat0, mat1

def createTree(dataSet, leafType = regLeaf, errType = regErr, ops = (1, 4)):
    feature, value = chooseBestSplit(dataSet, leafType, errType, ops)
    if feature == None:
        return value
       
    regTree = {}
    regTree['spIdx'] = feature
    regTree['spVal'] = value
       
    lSet, rSet = binSplitDataSet(dataSet, feature, value)
    regTree['left'] = createTree(lSet, leafType, errType, ops)
    regTree['right'] = createTree(rSet, leafType, errType, ops)
    return regTree

# check whether it is a tree, not a leaf node
def isTree(obj):
    return (type(obj).__name__ == 'dict')

# tree subside processing, return as mean value
def getMean(tree):
    if isTree(tree['left']):
        tree['left'] = getMean(tree['left'])
    if isTree(tree['right']):
        tree['right'] = getMean(tree['right'])
    return (tree['left'] + tree['right']) / 2.0

def prune(tree, testData):
    # check if testData is empty
    if np.shape(testData)[0] == 0:
        return getMean(tree)
    
    if (isTree(tree['left']) or isTree(tree['right'])):
        lSet, rSet = binSplitDataSet(testData, tree['spIdx'], tree['spVal'])
    if isTree(tree['left']):
        tree['left'] = prune(tree['left'], lSet)
    if isTree(tree['right']):
        tree['right'] = prune(tree['right'], rSet)
    
    if not isTree(tree['left']) and not isTree(tree['right']):
        lSet, rSet = binSplitDataSet(testData, tree['spIdx'], tree['spVal'])
        
        errorNoMerge = sum(np.power(lSet[:, -1] - tree['left'], 2)) + \
            sum(np.power(rSet[:, -1] - tree['right'], 2))
        treeMean = (tree['left'] + tree['right']) / 2.0
        errorMerge = sum(np.power(testData[:, -1] - treeMean, 2))
        
        # merge tree if error/deviation is smaller
        if errorMerge < errorNoMerge:
            print 'merging...'
            return treeMean
        else:
            return tree
    else:
        return tree

def modelLeaf(dataSet):
    ws, X, Y = linearSolve(dataSet)
    return ws

def modelErr(dataSet):
    ws, X, Y = linearSolve(dataSet)
    yHat = X * ws
    return sum(np.power(Y - yHat, 2))

def linearSolve(dataSet):
    m, n = np.shape(dataSet)
    X = np.mat(np.ones((m, n)))
    Y = np.mat(np.ones((m, 1)))
    
    # reformat dataSet to X and Y
    X[:, 1:n] = dataSet[:, 0:n-1]
    Y = dataSet[:, -1]
    xTx = X.T * X
    
    if np.linalg.det(xTx) == 0.0:
        raise NameError('This matrix is singular, cannot do inverse, \n\
        try increasing the second value of the ops')
    ws = xTx.I * (X.T * Y)
    return ws, X, Y

## tree forecast and evaluation

def regTreeEval(model, inData):
    return float(model)

def modelTreeEval(model, inData):
    n = np.shape(inData)[1]
    X = np.mat(np.ones((1, n+1)))
    X[:, 1:n+1] = inData
    return float(X * model)

def treeForecast(tree, inData, modelEval = regTreeEval):
    # if it's a single digit or array, eg. 1.0 or [1.0]
    if not isTree(tree):
        return modelEval(tree, inData)
    
    # recursive tree until hit the leaf node target
    if inData[tree['spIdx']] > tree['spVal']:
        if isTree(tree['left']):
            return treeForecast(tree['left'], inData, modelEval)
        else:
            return modelEval(tree['left'], inData)
    else:
        if isTree(tree['right']):
            return treeForecast(tree['right'], inData, modelEval)
        else:
            return modelEval(tree['right'], inData)

def createForecast(tree, testData, modelEval = regTreeEval):
    m = len(testData)
    yHat = np.mat(np.zeros((m, 1)))
    for i in range(m):
        yHat[i, 0] = treeForecast(tree, np.mat(testData[i]), modelEval)
    return yHat
