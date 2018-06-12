import numpy as np

# load phrase data and class
def loadDataSet():
    postingList = [['my', 'dog', 'has', 'flea', 'problems', 'help', 'please'],
                   ['maybe', 'not', 'take', 'him', 'to', 'dog', 'park', 'stupid'],
                   ['my', 'dalmation', 'is', 'so', 'cute', 'I', 'love', 'him'],
                   ['stop', 'posting', 'stupid', 'worthless', 'garbage'],
                   ['mr', 'licks', 'ate', 'my', 'steak', 'how', 'to', 'stop', 'him'],
                   ['quit', 'buying', 'worthless', 'dog', 'food', 'stupid']]
    # 0 - normal, 1 - offensive
    classVector = [0, 1, 0, 1, 0, 1]
    return postingList, classVector

# build vocabulary list
def createVocabList(dataSet):
    vocabSet = set([])
    for phrase in dataSet:
        # combine the two sets
        vocabSet = vocabSet | set(phrase)
    return list(vocabSet)

# mark phrase in vocabulary list
def phrase2Vector(vocabList, inputPhrase):
    phraseVector = [0] * len(vocabList)
    for word in inputPhrase:
        if word in vocabList:
            phraseVector[vocabList.index(word)] = 1
        # else:
        #    print "the word %s is not in my vocabulary." %word
    return phraseVector

# set-of-words -> bag-of-words
def phrase2BagVector(vocabList, inputPhrase):
    phraseVector = [0] * len(vocabList)
    for word in inputPhrase:
        if word in vocabList:
            phraseVector[vocabList.index(word)] += 1
        # else:
        #    print "the word %s is not in my vocabulary." %word
    return phraseVector

# unified train matrix, and relevant categories
def trainNaiveBayes(trainMatrix, trainCategory):
    numTrainPhrases = len(trainMatrix)
    numWords = len(trainMatrix[0])
    
    # offensive phrase's category value is 1
    pOffensive = sum(trainCategory) / float(numTrainPhrases)
    
    # set word initial and sum to 1.0 and 2.0 to avoid zero
    p0Num = np.ones(numWords)
    p1Num = np.ones(numWords)
    p0Sum = 2.0
    p1Sum = 2.0
    
    # count words vector and sum value in 0 and 1 category
    for i in range(numTrainPhrases):
        if trainCategory[i] == 0:
            p0Num += trainMatrix[i]
            p0Sum += sum(trainMatrix[i])
        else:
            p1Num += trainMatrix[i]
            p1Sum += sum(trainMatrix[i])
    
    # calculate p(w|ci) vector
    p0Vector = p0Num / p0Sum
    p1Vector = p1Num / p1Sum
    
    return p0Vector, p1Vector, pOffensive

def classifyNaiveBayes(inputVector, p0Vec, p1Vec, pClass1):
    # p(w|ci) * p(ci) -> ln(a*b) = ln(a) + ln(b)
    # ln(p(w|ci)) = ln(p(w0|ci)) + ln(p(w1|ci)) + ... + ln(p(wn|ci))
    p1 = sum(inputVector * np.log(p1Vec)) + np.log(pClass1)
    p0 = sum(inputVector * np.log(p0Vec)) + np.log(1 - pClass1)
    # print "p0 = %f, p1 = %f" %(p0, p1)
    
    if p1 > p0:
        return 1
    else:
        return 0

def testNaiveBayes():
    phrases, classes = loadDataSet()
    vocabList = createVocabList(phrases)
    trainMat = []
    for phrase in phrases:
        trainMat.append(phrase2Vector(vocabList, phrase))
    p0V, p1V, pOff = trainNaiveBayes(trainMat, classes)

    testPhrase = ['love', 'my', 'dalmation']
    testVector = phrase2Vector(vocabList, testPhrase)
    print "%r classified as %d" %(testPhrase, classifyNaiveBayes(testVector, p0V, p1V, pOff))
    
    testPhrase = ['stupid', 'garbage']
    testVector = phrase2Vector(vocabList, testPhrase)
    print "%r classified as %d" %(testPhrase, classifyNaiveBayes(testVector, p0V, p1V, pOff))

## spam email test
def textParse(longText):
    import re
    tokens = re.split("\\W*", longText)
    tokens = [tk.lower() for tk in tokens if len(tk) > 2]
    return tokens

def spamEmailTest():
    docList = []; classList = []; fullText = []
    
    # read 25 files in spam and ham folder, total is 50
    for i in range(1, 26):
        wordList = textParse(open('data/email/spam/%d.txt' %i).read())
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(1)
        wordList = textParse(open('data/email/ham/%d.txt' %i).read())
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(0)
    vocabList = createVocabList(docList)
    
    # build train number set (size=40) and test number set (size=10)
    trainNumSet = range(50); testNumSet = []
    for i in range(10):
        randIndex = int(np.random.uniform(0, len(trainNumSet)))
        testNumSet.append(trainNumSet[randIndex])
        del(trainNumSet[randIndex])
    
    # build train matrix (size=40)
    print 'train number set: %s' %trainNumSet
    trainMat = []; trainClasses = []
    for docIndex in trainNumSet:
        trainMat.append(phrase2BagVector(vocabList, docList[docIndex]))
        trainClasses.append(classList[docIndex])
    p0V, p1V, pSpam = trainNaiveBayes(trainMat, trainClasses)
    
    errorCount = 0
    print 'test number set: %s' %testNumSet
    for docIndex in testNumSet:
        wordVector = phrase2BagVector(vocabList, docList[docIndex])
        resultClass = classifyNaiveBayes(wordVector, p0V, p1V, pSpam)
        actualClass = classList[docIndex] 
        if resultClass != actualClass:
            errorCount += 1
            print "No. %d analysis result is %d, but actually is %d" \
                %(docIndex, resultClass, actualClass)
    print "the error rate is %f" %(float(errorCount)/len(testNumSet))

## words and location classification

def calcMostFreq(vocabList, fullText):
    import operator
    freqDict = {}
    for token in vocabList:
        freqDict[token] = fullText.count(token)
    sortedFreq = sorted(freqDict.iteritems(), key = operator.itemgetter(1), \
                        reverse = True)
    return sortedFreq[:30]

def localWords(feed1, feed0):
    import feedparser
    docList = []
    classList = []
    fullText = []
    
    # prepare doc list and full text array
    minLen = min(len(feed1['entries']), len(feed0['entries']))
    for i in range(minLen):
        wordList = textParse(feed1['entries'][i]['summary'])
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(1)
        wordList = textParse(feed0['entries'][i]['summary'])
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(0)
     
    # create vocabulary list and top 30 frequent words
    vocabList = createVocabList(docList)
    top30Words = calcMostFreq(vocabList, fullText)
    print 'vocabulary list length: %d' %len(vocabList)
     
    # remove top 30 frequent words from vocabulary list
    # comment or uncomment to see the result differences
    for word in top30Words:
        if word[0] in vocabList:
            vocabList.remove(word[0])
     
    # pick out 10 from training set randomly as test set
    trainingSet = range(2 * minLen)
    testSet = []
    for i in range(10):
        randIndex = int(np.random.uniform(0, len(trainingSet)))
        testSet.append(trainingSet[randIndex])
        del(trainingSet[randIndex])
         
    trainMat = []
    trainClasses = []
    print 'train number set: %s' %trainingSet
    for docIndex in trainingSet:
        trainMat.append(phrase2BagVector(vocabList, docList[docIndex]))
        trainClasses.append(classList[docIndex])
    p0V, p1V, pLoc1 = trainNaiveBayes(trainMat, trainClasses)
     
    errorCount = 0
    print 'test number set: %s' %testSet
    for docIndex in testSet:
        wordVector = phrase2BagVector(vocabList, docList[docIndex])
        resultClass = classifyNaiveBayes(wordVector, p0V, p1V, pLoc1)
        actualClass = classList[docIndex]
        if resultClass != actualClass:
            errorCount += 1
            print "No. %d analysis result is %d, but actually is %d" \
                %(docIndex, resultClass, actualClass)
    print "the error rate is %f" %(float(errorCount)/len(testSet))
    return vocabList, p0V, p1V

def getTopWords(ny, sf):
    import operator
    import feedparser
    # ny = feedparser.parse('http://newyork.craigslist.org/stp/index.rss')
    # sf = feedparser.parse('http://sfbay.craigslist.org/stp/index.rss')
    vocabList, pSF, pNY = localWords(ny, sf)
    
    topSF = []
    topNY = []
    for i in range(len(pSF)):
        if pSF[i] > 0.006: topSF.append((vocabList[i], pSF[i]))
        if pNY[i] > 0.006: topNY.append((vocabList[i], pNY[i]))
    
    sortedSF = sorted(topSF, key = lambda pair: pair[1], reverse = True)
    print '--- SF Bay (%d) ---' % len(sortedSF)
    topSFWords = []
    for item in sortedSF:
        topSFWords.append(item[0])
    print topSFWords
    
    sortedNY = sorted(topNY, key = lambda pair: pair[1], reverse = True)
    print '--- New York (%d) ---' % len(sortedNY)
    topNYWords = []
    for item in sortedNY:
        topNYWords.append(item[0])
    print topNYWords
