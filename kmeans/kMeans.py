import numpy as np

def loadDataSet(filename):
	dataMat = []
	fr = open(filename)
	for line in fr.readlines():
		currLine = line.strip().split('\t')
		floatLine = map(float, currLine)
		dataMat.append(floatLine)
	return dataMat

# calculate euclidean distance
def distEclid(vecA, vecB):
	return np.sqrt(np.sum(np.power(vecA - vecB, 2)))

# generate random centroids
def randCent(dataSet, k):
	n = np.shape(dataSet)[1]
	centroids = np.mat(np.zeros((k, n)))
	for j in range(n):
		minJ = min(dataSet[:, j])
		rangeJ = float(max(dataSet[:, j]) - minJ)
		# generate random center for each column with k rows
		centroids[:, j] = minJ + rangeJ * np.random.rand(k, 1)
	return centroids

def kMeans(dataSet, k, distMeans = distEclid, createCent = randCent):
	m = np.shape(dataSet)[0]
	# create matrix to save clustering result for each data row
	clusterAssment = np.mat(np.zeros((m, 2)))
	centroids = createCent(dataSet, k)
	clusterChanged = True

	# terminate loop until clustering result is stable
	while clusterChanged:
		clusterChanged = False

		# check each row in input dataSet
		for i in range(m):
			minDist = np.inf
			minIndex = -1

			# check each row in random centroids
			for j in range(k):
				# find nearest centroid for current data row
				distJI = distMeans(centroids[j, :], dataSet[i, :])
				if distJI < minDist:
					minDist = distJI
					minIndex = j
			# save nearest centroid index and distance
			if clusterAssment[i, 0] != minIndex:
				clusterChanged = True
			clusterAssment[i, :] = minIndex, minDist ** 2
		print centroids

		# calculate mean of data points for each centroid
		for cent in range(k):
			# filter clusterAssment by each centroid index 0,1,2...k-1
			ptsInClust = dataSet[np.nonzero(clusterAssment[:, 0].A == cent)[0], :]
			centroids[cent, :] = np.mean(ptsInClust, axis = 0)

	return centroids, clusterAssment

# bisecting k-means algorithm
def biKmeans(dataSet, k, distMeans = distEclid):
	m = np.shape(dataSet)[0]
	clusterAssment = np.mat(np.zeros((m, 2)))
	centroid0 = np.mean(dataSet, axis = 0).tolist()[0]
	centList = [centroid0]

	# create an initial clustering matrix
	for j in range(m):
		clusterAssment[j, 1] = distMeans(np.mat(centroid0), dataSet[j, :]) ** 2

	while (len(centList) < k):
		lowestSSE = np.inf

		for i in range(len(centList)):
			# try to split each cluster 0,1,2..., calculate the sse
			ptsInCurrCluster = \
				dataSet[np.nonzero(clusterAssment[:, 0].A == i)[0], :]
			centroidMat, splitClustAss = \
				kMeans(ptsInCurrCluster, 2, distMeans)
			sseSplit = np.sum(splitClustAss[:, 1])
			sseNotSplit = \
				np.sum(clusterAssment[np.nonzero(clusterAssment[:, 0].A != i)[0], 1])
			print 'sse split: %f and not split: %f' % (sseSplit, sseNotSplit)

			if (sseSplit + sseNotSplit) < lowestSSE:
				bestIdxToSplit = i
				bestNewCents = centroidMat
				bestClustAss = splitClustAss.copy()
				lowestSSE = sseSplit + sseNotSplit

		# re-assign cluster index to bestClustAss after split
		bestClustAss[np.nonzero(bestClustAss[:, 0].A == 0)[0], 0] = bestIdxToSplit
		bestClustAss[np.nonzero(bestClustAss[:, 0].A == 1)[0], 0] = len(centList)
		print 'split cluster: %d -> %d + %d ' \
			% (bestIdxToSplit, bestIdxToSplit, len(centList))
		print 'the size of best cluster to split is:', len(bestClustAss)

		# update centroid list on bestIdxToSplit and add new centroid
		centList[bestIdxToSplit] = bestNewCents[0, :]
		centList.append(bestNewCents[1, :])

		# update clusterAssment on bestIdxToSplit to bestClustAss
		clusterAssment[np.nonzero(clusterAssment[:, 0].A == \
			bestIdxToSplit)[0], :] = bestClustAss
	
	return centList, clusterAssment
