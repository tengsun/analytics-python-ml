import numpy as np

def loadSimpleData():
	dataMat = np.mat([[1.0, 2.1],
		[2.0, 1.1],
		[1.3, 1.0],
		[1.0, 1.0],
		[2.0, 1.0]])  # [1.5, 1.6]])
	labels = [1.0, 1.0, -1.0, -1.0, 1.0]
	return dataMat, labels

# single layer classify tree model
def stumpClassify(dataMat, dimen, threshVal, threshIneq):
	result = np.ones((np.shape(dataMat)[0], 1))
	if threshIneq == 'lt':
		result[dataMat[:, dimen] <= threshVal] = -1.0
	else:
		result[dataMat[:, dimen] > threshVal] = 1.0
	return result

# data array, class labels and weighted vector D
def buildStump(dataArr, labels, D):
	dataMat = np.mat(dataArr)
	labelMat = np.mat(labels).T
	m, n = np.shape(dataMat)
	
	numSteps = 10
	bestStump = {}
	bestClassEst = np.mat(np.zeros((m, 1)))
	minError = np.inf
	
	# iterate features
	for i in range(n):
		rangeMin = dataMat[:, i].min()
		rangeMax = dataMat[:, i].max()
		stepSize = (rangeMax - rangeMin) / numSteps

		# extend steps range
		for j in range(-1, int(numSteps) + 1):
			for inequal in ['lt', 'gt']:
				threshVal = (rangeMin + float(j) * stepSize)
				predictedVals = \
					stumpClassify(dataMat, i, threshVal, inequal)

				# mark error predicated label
				errArr = np.mat(np.ones((m, 1)))
				errArr[predictedVals == labelMat] = 0
				weightedErr = D.T * errArr
				# print 'split: dim %d, thresh %.2f, thresh inequal: '\
				# 	'%s, the weighted error is %.3f' \
				# 	% (i, threshVal, inequal, weightedErr)
				# print predictedVals

				if weightedErr < minError:
					minError = weightedErr
					bestClassEst = predictedVals.copy()
					bestStump['dim'] = i
					bestStump['thresh'] = threshVal
					bestStump['ineq'] = inequal

	return bestStump, minError, bestClassEst

def adaBoostTrainDS(dataArr, labels, numIt = 40):
	weakClassifiers = []

	m = np.shape(dataArr)[0]
	D = np.mat(np.ones((m, 1)) / m)
	# aggregated class estimation for each point
	aggClassEst = np.mat(np.zeros((m, 1)))

	for i in range(numIt):
		bestStump, error, classEst = buildStump(dataArr, labels, D)
		print 'D: ', D.T
		print 'classEst: ', classEst.T

		# eg. error = 0.2, alpha = 1/2 * ln4
		alpha = float(0.5 * np.log((1.0 - error) / max(error, 1e-16)))
		bestStump['alpha'] = alpha
		weakClassifiers.append(bestStump)

		# if classify right, 1 * 1 = 1, -1 * -1 = 1, exp(-alpha)
		# if classify wrong, 1 * -1 = -1, -1 * 1 = -1, exp(alpha)
		expon = np.multiply(-1 * alpha * np.mat(labels).T, classEst)
		# eg. old D' = 0.2, right class, exp(-1/2 * ln4) = 0.5, new D' = 0.1
		# eg. old D' = 0.2, wrong class, exp(1/2 * ln4) = 2, new D' = 0.4
		D = np.multiply(D, np.exp(expon))
		# eg. 0.4 / (0.4 + 0.1 * 4) = 0.5
		D = D / D.sum()

		aggClassEst += alpha * classEst
		print 'aggClassEst: ', aggClassEst.T

		# The sign function returns -1 if x < 0, 1 if x > 0
		aggErrors = np.multiply(np.sign(aggClassEst) != \
			np.mat(labels).T, np.ones((m, 1)))
		errorRate = aggErrors.sum() / m
		print 'total error: ', errorRate
		if errorRate == 0.0:
			break
	return weakClassifiers

def adaClassify(dataToClass, classifiers):
	dataMat = np.mat(dataToClass)
	m = np.shape(dataMat)[0]
	aggClassEst = np.mat(np.zeros((m, 1)))
	for i in range(len(classifiers)):
		classEst = stumpClassify(dataMat, classifiers[i]['dim'], \
			classifiers[i]['thresh'], classifiers[i]['ineq'])
		aggClassEst += classifiers[i]['alpha'] * classEst
		print aggClassEst
	return np.sign(aggClassEst)
