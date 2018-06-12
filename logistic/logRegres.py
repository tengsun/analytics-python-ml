import numpy as np

# load sample data
def loadDataSet():
    dataMat = []
    labelMat = []
    file = open('data/testSet.txt')
    for line in file.readlines():
        # line content: x1 x2 label
        dataArray = line.strip().split()
        # set x0 = 1.0
        dataMat.append([1.0, float(dataArray[0]), float(dataArray[1])])
        labelMat.append(int(dataArray[2]))
    return dataMat, labelMat

# define sigmoid function
def sigmoid(inX):
    return 1.0 / (1 + np.exp(-inX))

# gradient ascent function
def gradAscent(dataMatIn, labelMatIn):
    # convert to numpy matrix for transpose
    dataMatrix = np.mat(dataMatIn)
    labelMatrix = np.mat(labelMatIn).transpose()
    m, n = np.shape(dataMatrix)
    # distance of each step
    alpha = 0.001
    # maximum iteration times
    maxCycles = 500
    # initialize weights vector
    weights = np.ones((n, 1))
    
    for k in range(maxCycles):
        # h is a column vector [m * 1] with values within (0, 1)
        h = sigmoid(dataMatrix * weights)
        # calculate the diff between actual value and forecast value
        # apply diff to x0, x1, x2 by multiple data matrix transpose
        # then adjust the weights according to the direction of diff
        diff = (labelMatrix - h)
        weights = weights + alpha * dataMatrix.transpose() * diff
    
    # convert matrix to array
    return weights.getA()

# stochastic gradient ascent function
def stochasticGradAscent(dataMatIn, labelMatIn, numIter = 150):
    dataMatrix = np.array(dataMatIn)
    labelMatrix = labelMatIn
    m, n = np.shape(dataMatrix)
    weights = np.ones(n)
    
    for j in range(numIter):
        
        dataIndex = range(m)
        for i in range(m):
            # reduce alpha's value as iteration goes on
            alpha = 4 / (1.0 + j + i) + 0.01
            
            # pick data randomly for weights adjustment
            randIndex = int(np.random.uniform(0, len(dataIndex)))
            h = sigmoid(sum(dataMatrix[randIndex] * weights))
            diff = labelMatrix[randIndex] - h
            weights = weights + alpha * dataMatrix[randIndex] * diff
            
            # remove random index
            del(dataIndex[randIndex])
    return weights

def plotBestFit(weights):
    import matplotlib.pyplot as plt
    dataMat, labelMat = loadDataSet()
    dataArr = np.array(dataMat)
    n = np.shape(dataArr)[0]
    xcord1 = []; ycord1 = []
    xcord2 = []; ycord2 = []
    for i in range(n):
        if int(labelMat[i]) == 1:
            xcord1.append(dataArr[i, 1]); ycord1.append(dataArr[i, 2])
        else:
            xcord2.append(dataArr[i, 1]); ycord2.append(dataArr[i, 2])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(xcord1, ycord1, s = 30, c = 'red', marker = 's')
    ax.scatter(xcord2, ycord2, s = 30, c = 'green')
    x = np.arange(-3.0, 3.0, 0.1)
    
    # z = w0 * x0 + w1 * x1 + w2 * x2, set z = 0 to draw divide line
    y = (-weights[0] - weights[1] * x) / weights[2]
    ax.plot(x, y)
    plt.xlabel('X1'); plt.ylabel('X2')
    plt.show()

## estimating horse fatalities from colic

def classifyVector(inX, weights):
    prob = sigmoid(sum(inX * weights))
    if prob > 0.5:
        return 1.0
    else:
        return 0.0

def colicTest():
    frTrain = open('data/horse/horseColicTraining.txt')
    frTest = open('data/horse/horseColicTest.txt')
    
    # prepare training set and labels
    trainingSet = []
    trainingLabels = []
    for line in frTrain.readlines():
        currLine = line.strip().split('\t')
        lineArr = []
        numFeatures = len(currLine) - 1
        for i in range(numFeatures):
            lineArr.append(float(currLine[i]))
        trainingSet.append(lineArr)
        trainingLabels.append(float(currLine[numFeatures]))
    
    # calculate weights after training
    weights = stochasticGradAscent(trainingSet, trainingLabels, 500)
    
    errCount = 0
    numTest = 0.0
    for line in frTest.readlines():
        numTest += 1.0
        currLine = line.strip().split('\t')
        lineArr = []
        numFeatures = len(currLine) - 1
        for i in range(numFeatures):
            lineArr.append(float(currLine[i]))
        
        # compare classify result and actual value
        classifyResult = classifyVector(lineArr, weights)
        if (int(classifyResult) != int(currLine[numFeatures])):
            errCount += 1
    
    errRate = float(errCount) / numTest
    print 'the error rate of test is %f' % errRate
    return errRate

def multiTest():
    numTests = 10
    errorSum = 0.0
    for k in range(numTests):
        errorSum += colicTest()
    print 'after %d iterations the average error rate is %f' \
        % (numTests, errorSum / float(numTests))
