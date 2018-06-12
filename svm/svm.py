import numpy as np

def loadDataSet(filename):
    dataMat = []
    labelMat = []
    file = open(filename)
    for line in file.readlines():
        dataArr = line.strip().split('\t')
        dataMat.append([float(dataArr[0]), float(dataArr[1])])
        labelMat.append(float(dataArr[2]))
    return dataMat, labelMat

# i is alpha index, m is number of alpha variables
def selectRandomJ(i, m):
    j = i
    while (j == i):
        j = int(np.random.uniform(0, m))
    return j

# adjust alpha value to keep within [L, H]
def adjustAlpha(aj, H, L):
    if aj > H:
        aj = H
    if aj < L:
        aj = L
    return aj

def smoSimple(dataMatIn, labelMatIn, C, toler, maxIter):
    dataMat = np.mat(dataMatIn)
    labelMat = np.mat(labelMatIn).transpose()
    b = 0
    m, n = np.shape(dataMat)
    alphas = np.mat(np.zeros((m, 1)))
    iter = 0
    
    while (iter < maxIter):
        alphaPairsChanged = 0
        
        for i in range(m):
            fXi = float(np.multiply(alphas, labelMat).T * \
                        (dataMat * dataMat[i, :].T)) + b
            Ei = fXi - float(labelMat[i])
            
            if (((labelMat[i] * Ei < -toler) and (alphas[i] < C)) or \
                ((labelMat[i] * Ei > toler) and (alphas[i] > 0))):
                j = selectRandomJ(i, m)
                fXj = float(np.multiply(alphas, labelMat).T * \
                        (dataMat * dataMat[j, :].T)) + b
                Ej = fXj - float(labelMat[j])
            
                oldAlphaI = alphas[i].copy()
                oldAlphaJ = alphas[j].copy()
                
                if (labelMat[i] != labelMat[j]):
                    L = max(0, alphas[j] - alphas[i])
                    H = min(C, C + alphas[j] - alphas[i])
                else:
                    L = max(0, alphas[j] + alphas[i] - C)
                    H = min(C, alphas[j] + alphas[i])
                
                if L == H:
                    print "L == H"
                    continue
                
                eta = 2.0 * dataMat[i, :] * dataMat[j, :].T - \
                        dataMat[i, :] * dataMat[i, :].T - \
                        dataMat[j, :] * dataMat[j, :].T
                
                if eta >= 0:
                    print "eta >= 0"
                    continue
                
                alphas[j] -= labelMat[j] * (Ei - Ej) / eta
                alphas[j] = adjustAlpha(alphas[j], H, L)
                
                if (abs(alphas[j] - oldAlphaJ) < 0.00001):
                    print "j not moving enough"
                    continue
                
                alphas[i] += labelMat[j] * labelMat[i] * \
                            (oldAlphaJ - alphas[j])
                b1 = b - Ei - labelMat[i] * (alphas[i] - oldAlphaI) * \
                        dataMat[i, :] * dataMat[i, :].T - \
                        labelMat[j] * (alphas[j] - oldAlphaJ) * \
                        dataMat[i, :] * dataMat[j, :].T
                b2 = b - Ej - labelMat[i] * (alphas[i] - oldAlphaI) * \
                        dataMat[i, :] * dataMat[j, :].T - \
                        labelMat[j] * (alphas[j] - oldAlphaJ) * \
                        dataMat[j, :] * dataMat[j, :].T
                
                if (0 < alphas[i]) and (C > alphas[i]):
                    b = b1
                elif (0 < alphas[j]) and (C > alphas[j]):
                    b = b2
                else:
                    b = (b1 + b2) / 2.0
                alphaPairsChanged += 1
                print "iter: %d i: %d, pairs changed %d" %(iter, i, alphaPairsChanged)
            
        if (alphaPairsChanged == 0):
            iter += 1
        else:
            iter = 0
        print "iteration number: %d" %iter
        
    return b, alphas
