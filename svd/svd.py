import numpy as np

def loadData():
	return [[1, 1, 1, 0, 0],
			[2, 2, 2, 0, 0],
			[1, 1, 1, 0, 0],
			[5, 5, 5, 0, 0],
			[1, 1, 0, 2, 2],
			[0, 0, 0, 3, 3],
			[0, 0, 0, 1, 1]]

def loadData2():
	return[[0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 5],
           [0, 0, 0, 3, 0, 4, 0, 0, 0, 0, 3],
           [0, 0, 0, 0, 4, 0, 0, 1, 0, 4, 0],
           [3, 3, 4, 0, 0, 0, 0, 2, 2, 0, 0],
           [5, 4, 5, 0, 0, 0, 0, 5, 5, 0, 0],
           [0, 0, 0, 0, 5, 0, 1, 0, 0, 5, 0],
           [4, 3, 4, 0, 0, 0, 0, 5, 5, 0, 1],
           [0, 0, 0, 4, 0, 4, 0, 0, 0, 0, 4],
           [0, 0, 0, 2, 0, 2, 5, 0, 0, 1, 2],
           [0, 0, 0, 0, 5, 0, 0, 0, 0, 4, 0],
           [1, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0]]

def simMatrix():
	mat = loadData()
	u, sigma, vt = np.linalg.svd(mat)
	# keep 3 values to cover 90% info
	sig3 = np.mat([[sigma[0], 0, 0], \
				   [0, sigma[1], 0], \
				   [0, 0, sigma[2]]])
	simMat = u[:, :3] * sig3 * vt[:3, :]
	print simMat

# three methods to calculate similarity

def ecludSim(inA, inB):
	return 1.0 / (1.0 + np.linalg.norm(inA - inB))

def pearsSim(inA, inB):
	if len(inA) < 3:
		return 1.0
	return 0.5 + 0.5 * np.corrcoef(inA, inB, rowvar = 0)[0][1]

def cosSim(inA, inB):
	num = float(inA.T * inB)
	denom = np.linalg.norm(inA) * np.linalg.norm(inB)
	return 0.5 + 0.5 * (num / denom)

# meal recommendation for users

def standEst(dataMat, user, item, simMeas):
	n = np.shape(dataMat)[1]
	simTotal = 0.0
	rateSimTotal = 0.0

	for j in range(n):
		userRating = dataMat[user, j]
		# skip data item if user didn't rate it
		if userRating == 0:
			continue
		# find users who rate both on item and j
		overlap = np.nonzero(np.logical_and(dataMat[:, item].A > 0, \
											dataMat[:, j].A > 0))[0]
		print 'users', overlap, 'has rating on %d and %d' % (item, j)
		if len(overlap) == 0:
			similarity = 0
		else:
			similarity = simMeas(dataMat[overlap, item], \
								dataMat[overlap, j])
		print 'the %d and %d similarity is: %f' % (item, j, similarity)

		simTotal += similarity
		rateSimTotal += similarity * userRating

	if simTotal == 0:
		return 0
	else:
		return rateSimTotal / simTotal

def svdEst(dataMat, user, item, simMeas):
	n = np.shape(dataMat)[1]
	simTotal = 0.0
	rateSimTotal = 0.0

	# use svd to reduce data dimensionality to 4
	u, sigma, vt = np.linalg.svd(dataMat)
	sig4 = np.mat(np.eye(4) * sigma[:4])
	xformedItems = dataMat.T * u[:, :4] * sig4.I

	for j in range(n):
		userRating = dataMat[user, j]
		if userRating == 0 or j == item:
			continue
		similarity = simMeas(xformedItems[item, :].T, \
							xformedItems[j, :].T)
		print 'the %d and %d similarity is: %f' % (item, j, similarity)

		simTotal += similarity
		rateSimTotal += similarity * userRating

	if simTotal == 0:
		return 0
	else:
		return rateSimTotal / simTotal

def recommend(dataMat, user, N = 3, simMeas = cosSim, estMethod = standEst):
	unratedItems = np.nonzero(dataMat[user, :].A == 0)[1]
	
	if len(unratedItems) == 0:
		return 'you rated everything'

	itemScores = []
	# calculate every item score if user didn't rate it
	for item in unratedItems:
		estimatedScore = estMethod(dataMat, user, item, simMeas)
		itemScores.append((item, estimatedScore))
	return sorted(itemScores, key = lambda j: j[1], reverse = True)[:N]
