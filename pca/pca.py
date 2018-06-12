import numpy as np
import matplotlib.pyplot as plt

def loadDataSet(filename, delim = '\t'):
	fr = open(filename)
	strArr = [line.strip().split(delim) for line in fr.readlines()]
	dataArr = [map(float, line) for line in strArr]
	return np.mat(dataArr)

def pca(dataMat, topNfeat = 9999999):
	# calculate covariance matrix
	meanVals = np.mean(dataMat, axis = 0)
	meanRemoved = dataMat - meanVals
	covMat = np.cov(meanRemoved, rowvar = 0)

	# calculate eigen value and vector
	eigVals, eigVects = np.linalg.eig(np.mat(covMat))

	# select top N eigen vector
	eigValIdx = np.argsort(eigVals)
	eigValIdx = eigValIdx[:-(topNfeat + 1):-1]
	redEigVects = eigVects[:, eigValIdx]

	lowDataMat = meanRemoved * redEigVects
	reconMat = (lowDataMat * redEigVects.T) + meanVals
	return lowDataMat, reconMat

def pcaPlot():
	dataMat = loadDataSet('data/testSet.txt')
	lowDataMat, reconMat = pca(dataMat, 1)

	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.scatter(dataMat[:, 0].flatten().A[0], dataMat[:, 1].flatten().A[0], \
		marker = '^', s = 90)
	ax.scatter(reconMat[:, 0].flatten().A[0], reconMat[:, 1].flatten().A[0], \
		marker = 'o', s = 50, c = 'red')
	plt.show()

def replaceNaNWithMean():
	dataMat = loadDataSet('data/secom.data', ' ')
	numFeatures = np.shape(dataMat)[1]
	for i in range(numFeatures):
		meanVal = np.mean(dataMat[np.nonzero(~np.isnan(dataMat[:, i].A))[0], i])
		dataMat[np.nonzero(np.isnan(dataMat[:, i].A))[0], i] = meanVal
	return dataMat
