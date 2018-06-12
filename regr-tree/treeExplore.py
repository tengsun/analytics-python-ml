from Tkinter import *
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import regrTree

def reDraw(tolS, tolN):
    reDraw.f.clf()
    reDraw.a = reDraw.f.add_subplot(111)
    if chkBtnVar.get():
        if tolN < 2:
            tolN = 2
        myTree = regrTree.createTree(reDraw.rawData, regrTree.modelLeaf, \
                                     regrTree.modelErr, ops = (tolS, tolN))
        yHat = regrTree.createForecast(myTree, reDraw.testData, \
                                     regrTree.modelTreeEval)
    else:
        myTree = regrTree.createTree(reDraw.rawData, ops = (tolS, tolN))
        yHat = regrTree.createForecast(myTree, reDraw.testData)
    reDraw.a.scatter(reDraw.rawData[:, 0], reDraw.rawData[:, 1], s = 5)
    reDraw.a.plot(reDraw.testData, yHat, linewidth = 2.0)
    reDraw.canvas.show()

def getInputs():
    try:
        tolN = int(tolNEntry.get())
    except:
        tolN = 10
        print 'please enter integer for tolN'
        tolNEntry.delete(0, END)
        tolNEntry.insert(0, '10')
    try:
        tolS = float(tolSEntry.get())
    except:
        tolS = 1.0
        print 'please enter float for tolS'
        tolSEntry.delete(0, END)
        tolSEntry.insert(0, '1.0')
    return tolN, tolS

def drawNewTree():
    tolN, tolS = getInputs()
    reDraw(tolS, tolN)

root = Tk()

# Label(root, text = 'Plot Placeholder').grid(row = 0, columnspan = 3)
reDraw.f = Figure(figsize = (5, 4), dpi = 100)
reDraw.canvas = FigureCanvasTkAgg(reDraw.f, master = root)
reDraw.canvas.show()
reDraw.canvas.get_tk_widget().grid(row = 0, columnspan = 3)

# tolN label and input field
Label(root, text = 'tolN').grid(row = 1, column = 0)
tolNEntry = Entry(root)
tolNEntry.grid(row = 1, column = 1)
tolNEntry.insert(0, '10')

# tolS label and input field
Label(root, text = 'tolS').grid(row = 2, column = 0)
tolSEntry = Entry(root)
tolSEntry.grid(row = 2, column = 1)
tolSEntry.insert(0, '1.0')

# ReDarw button 
Button(root, text = 'ReDraw', command = drawNewTree).grid(row = 1, \
                                            column = 2, rowspan = 3)

# Model Tree checkbox
chkBtnVar = IntVar()
chkBtn = Checkbutton(root, text = 'Model Tree', variable = chkBtnVar)
chkBtn.grid(row = 3, column = 0, columnspan = 2)

reDraw.rawData = np.mat(regrTree.loadDataSet('data/sine.txt'))
reDraw.testData = np.arange(min(reDraw.rawData[:, 0]), \
                            max(reDraw.rawData[:, 0]), 0.01)
reDraw(1.0, 10)

root.mainloop()
