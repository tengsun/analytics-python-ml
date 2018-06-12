import numpy as np
import matplotlib.pyplot as plt
from numpy import inf

def loadDataSet(file):
    dataMat = []
    labelMat = []
    dataLen = len(open(file).readline().split('\t')) - 1
    
    fr = open(file)
    for line in fr.readlines():
        lineArr = []
        currLine = line.strip().split('\t')
        
        # reformat string to float value
        for i in range(dataLen):
            lineArr.append(float(currLine[i]))
        
        # add to data matrix and label matrix
        dataMat.append(lineArr)
        labelMat.append(float(currLine[-1]))
    
    return dataMat, labelMat

# standard regression, formula: y = ws[0] + ws[1] * x
def standRegression(xArr, yArr):
    xMat = np.mat(xArr)
    yMat = np.mat(yArr).T
    
    xTx = xMat.T * xMat
    if np.linalg.det(xTx) == 0.0:
        print 'This matrix is singular, cannot do inverse'
        return

    ws = xTx.I * (xMat.T * yMat)
    return ws

# draw regression line and plot
def regressionPlot():
    xArr, yArr = loadDataSet('data/ex0.txt')
    xMat = np.mat(xArr)
    yMat = np.mat(yArr)
    ws = standRegression(xArr, yArr)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(xMat[:, 1].flatten().A[0], yMat.T[:, 0].flatten().A[0])
    
    # sort in order to draw line
    xCopy = xMat.copy()
    xCopy.sort(0)
    yHat = xCopy * ws
    ax.plot(xCopy[:, 1], yHat)
    
    plt.show()

# LWLR, locally weighted linear regression
def lwlr(testPoint, xArr, yArr, k = 1.0):
    xMat = np.mat(xArr)
    yMat = np.mat(yArr).T
    m = np.shape(xMat)[0]
    weights = np.mat(np.eye((m)))
    
    # iterate to calculate weights matrix
    for j in range(m):
        diffMat = testPoint - xMat[j, :]
        # decrease the weights by exponential rate
        weights[j, j] = np.exp(diffMat * diffMat.T / (-2.0 * k ** 2))
    
    xTx = xMat.T * (weights * xMat)
    if np.linalg.det(xTx) == 0.0:
        print 'This matrix is singular, cannot do inverse'
        return

    ws = xTx.I * (xMat.T * (weights * yMat))
    return testPoint * ws

def lwlrTest(testArr, xArr, yArr, k = 1.0):
    m = np.shape(testArr)[0]
    yHat = np.zeros(m)
    for i in range(m):
        yHat[i] = lwlr(testArr[i], xArr, yArr, k)
    return yHat

def lwlrPlot():
    xArr, yArr = loadDataSet('data/ex0.txt')
    # adjust k value to 1.0, 0.01, 0.003
    yHat = lwlrTest(xArr, xArr, yArr, 0.01)
    xMat = np.mat(xArr)
    yMat = np.mat(yArr)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(xMat[:, 1].flatten().A[0], yMat.T[:, 0].flatten().A[0], s = 2, c = 'red')
    
    # sort xMat by column index = 1
    sortedIndex = xMat[:, 1].argsort(0)
    xSort = xMat[sortedIndex][:, 0, :]
    ax.plot(xSort[:, 1], yHat[sortedIndex])
    
    plt.show()

# calculate the diff between actual and forecast data
def rssError(yArr, yHatArr):
    return ((yArr - yHatArr) ** 2).sum()

# ridge regression, when n > m (features > sample size)
def ridgeRegression(xMat, yMat, lam = 0.2):
    xTx = xMat.T * xMat
    denom = xTx + np.eye(np.shape(xMat)[1]) * lam
    if np.linalg.det(denom) == 0.0:
        print 'This matrix is singular, cannot do inverse'
        return
    
    ws = denom.I * (xMat.T * yMat)
    return ws

def ridgeTest(xArr, yArr):
    xMat = np.mat(xArr)
    yMat = np.mat(yArr).T
    
    yMean = np.mean(yMat, 0)
    yMat = yMat - yMean
    
    xMeans = np.mean(xMat, 0)
    xVar = np.var(xMat, 0)
    # standardize the xMat values
    xMat = (xMat - xMeans) / xVar
    numTestPts = 30
    
    wMat = np.zeros((numTestPts, np.shape(xMat)[1]))
    for i in range(numTestPts):
        ws = ridgeRegression(xMat, yMat, np.exp(i - 10))
        wMat[i, :] = ws.T
    return wMat

def ridgePlot():
    abX, abY = loadDataSet('data/abalone.txt')
    ridgeWeights = ridgeTest(abX, abY)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(ridgeWeights)
    plt.show()

def stageWise(xArr, yArr, eps = 0.01, numIt = 100):
    xMat = np.mat(xArr)
    yMat = np.mat(yArr).T
    
    yMean = np.mean(yMat, 0)
    yMat = yMat - yMean
    
    xMeans = np.mean(xMat, 0)
    xVar = np.var(xMat, 0)
    # standardize the xMat values
    xMat = (xMat - xMeans) / xVar
    
    m, n = np.shape(xMat)
    returnMat = np.zeros((numIt, n))
    ws = np.zeros((n, 1))
    wsTest = ws.copy()
    wsMax = ws.copy()
    
    for i in range(numIt):
        print ws.T
        lowestError = inf
        
        for j in range(n):
            for sign in [-1, 1]:
                wsTest = ws.copy()
                wsTest[j] += eps * sign
                yTest = xMat * wsTest
                rssE = rssError(yMat.A, yTest.A)
                if rssE < lowestError:
                    lowestError = rssE
                    wsMax = wsTest
        ws = wsMax.copy()
        returnMat[i, :] = ws.T
    
    return returnMat
