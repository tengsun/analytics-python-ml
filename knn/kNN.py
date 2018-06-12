from numpy import *
from os import listdir
import operator

# sample data set
def createDataSet():
	group = array([[1.0, 1.1], [1.0, 1.0], [0, 0], [0, 0.1]])
	labels = ['A', 'A', 'B', 'B']
	return group, labels

# inX - input x to be classified
# dataSet - training sample data
# labels - training classify labels
# k - number of neighbors
def classify0(inX, dataSet, labels, k):
	dataSetSize = dataSet.shape[0]
	diffMat = tile(inX, (dataSetSize, 1)) - dataSet
	sqDiffMat = diffMat ** 2
	sqDists = sqDiffMat.sum(axis = 1)
	dists = sqDists ** 0.5
	# get indices of sorted distance
	sortedDistIndices = dists.argsort()
	classCountDict = {}
	for i in range(k):
		voteLabel = labels[sortedDistIndices[i]]
		classCountDict[voteLabel] = classCountDict.get(voteLabel, 0) + 1
	sortedClassCount = sorted(classCountDict.iteritems(), 
		key = operator.itemgetter(1), reverse = True)
	return sortedClassCount[0][0]

# for dating test case
def file2matrix(filename):
	fr = open(filename)
	lines = fr.readlines()
	numOfLines = len(lines)
	returnMat = zeros((numOfLines, 3))
	labelVector = []
	index = 0
	for line in lines:
		line = line.strip()
		listFromLine = line.split('\t')
		returnMat[index, :] = listFromLine[0:3]
		labelVector.append(int(listFromLine[-1]))
		index += 1
	return returnMat, labelVector

# normalize digit values
def autoNorm(dataSet):
	minVals = dataSet.min(0)
	maxVals = dataSet.max(0)
	ranges = maxVals - minVals
	normDataSet = zeros(shape(dataSet))
	m = dataSet.shape[0]
	normDataSet = dataSet - tile(minVals, (m, 1))
	normDataSet = normDataSet / tile(ranges, (m, 1))
	return normDataSet, ranges, minVals

# dating data test code
def datingClassTest():
	hoRatio = 0.10
	datingMat, datingLabels = file2matrix('data/datingTestSet2.txt')
	normMat, ranges, minVals = autoNorm(datingMat)
	m = normMat.shape[0]
	numTestVectors = int(m * hoRatio)
	errorCount = 0.0
	for i in range(numTestVectors):
		classifierResult = classify0(normMat[i, :], normMat[numTestVectors:m, :], \
			datingLabels[numTestVectors:m], 3)
		if (classifierResult != datingLabels[i]):
			errorCount += 1.0
			print "[%d]: the classifier came back with: %d, the real answer is: %d" \
				%(i, classifierResult, datingLabels[i])
		else:
			print "[%d]: the classification is correct" %(i)
	print "the total error rate is: %f" %(errorCount / float(numTestVectors))

# input dating data forecast
def classifyPerson():
	resultList = ['not at all', 'in small doses', 'in large doses']
	flyingMiles = float(raw_input("frequent flier miles earned per year?"))
	videoGames = float(raw_input("percentage of time spent playing video games?"))
	iceCream = float(raw_input("liters of ice cream consumed per year?"))
	datingMat, datingLabels = file2matrix('data/datingTestSet2.txt')
	normMat, ranges, minVals = autoNorm(datingMat)
	inArray = array([flyingMiles, videoGames, iceCream])
	classifierResult = classify0((inArray - minVals) / ranges, normMat, datingLabels, 3)
	print "you will probably like this person:", resultList[classifierResult - 1]

## hand-writing number recognition

def img2vector(filename):
	lineVector = zeros((1, 1024))
	fr = open(filename)
	for i in range(32):
		lineString = fr.readline()
		for j in range(32):
			lineVector[0, 32 * i + j] = int(lineString[j])
	return lineVector

def handwritingNumberTest():
	# prepare number labels and training data
	numberLabels = []
	trainingFileList = listdir('data/digits/trainingDigits')
	m = len(trainingFileList)
	trainingMat = zeros((m, 1024))
	
	for i in range(m):
		filename = trainingFileList[i]
		if filename.find('.') != -1:
			fileString = filename.split('.')[0]
			numberValue = int(fileString.split('_')[0])
			
			numberLabels.append(numberValue)
			trainingMat[i, :] = img2vector('data/digits/trainingDigits/%s' %filename)
		else:
			print 'invalid file name: ' + filename
	
	# prepare test data
	testFileList = listdir('data/digits/testDigits')
	errorCount = 0.0
	mTest = len(testFileList)
	
	for i in range(mTest):
		filename = testFileList[i]
		if filename.find('.') != -1:
			fileString = filename.split('.')[0]
			numberValue = int(fileString.split('_')[0])
			
			# compare test result and actual value
			vectorToTest = img2vector('data/digits/testDigits/%s' %filename)
			classifierResult = classify0(vectorToTest, trainingMat, numberLabels, 3)
			if classifierResult != numberValue:
				errorCount += 1.0
				print 'the classifier came back with: %d, the real answer is: %d in file [%s]' \
					% (classifierResult, numberValue, filename)
			
		else:
			print 'invalid file name: ' + filename
	
	print 'the total number of errors is: %d' %errorCount
	print 'the total error rate is: %f' %(errorCount / float(mTest))
