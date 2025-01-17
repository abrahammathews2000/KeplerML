# runs multiple classifiers on multiple training sets and test sets
# prints the classification accuracy in each case
# NOTE: work in progress

import numpy as np
import pyfits as pf
import itertools
from scipy.io.idl import readsav
from scipy.spatial import distance
import pylab as pl
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.mixture import GMM
from astroML.datasets import fetch_sdss_specgals
from astroML.decorators import pickle_results
from sklearn import naive_bayes
from sklearn import svm
from astroML.classification import GMMBayes
#from __future__ import print_function

dataset = np.load('../data/dataset.npy')
logdata = np.load('../data/logdata.npy')

n2=len(dataset)
print n2
q=12
testdata = np.empty([n2,q])
plotdata = np.empty([n2,q])

#order: teff,   logg,   maxpkht, sndht, maxper, sndper, 
#       maxflx, sndflx, range,   rms4,  mdv3,   pdcvar

j=0
for i in [2,3,15,18,16,19,17,20,5,24,7,28]:
    mean = np.mean(logdata[:,i])
    std = np.mean(logdata[:,i])
    testdata[:,j] = (logdata[:,i]-mean)/std
    if i!=2 and i!=3:
        plotdata[:,j] = logdata[:,i]
    else:
        plotdata[:,j] = dataset[:,i]
    j=j+1

teff = dataset[:,2]
logg = dataset[:,3]

rrlyrae = [5520878, 3733346, 5299596, 6070714, 6100702,   6763132, 6936115, 7176080]
rtest = [7742534, 7988343, 8344381, 9508655, 9591503,   9947026, 10789273, 11802860]
instrip = [2571868, 2987660, 3629496, 5356349, 5437206,   6668729, 7304385, 7974841, 8018827, 8324268]
itest = [8351193, 8489712, 8915335, 9291618, 9351622,   10537907, 10974032, 11572666, 11874676, 12153021]
detached = [1026032, 1026957, 1433962, 1571511, 1725193,   1996679, 2010607, 2162635, 2162994, 2305372,   2305543, 2306740]
dtest = [2308957, 2309587, 2309719, 2437452, 2438070,   2440757, 2442084, 2445134, 2447893, 2556127,   2557430, 2576692]
semidet = [4947528, 4949770, 5077994, 5120793, 5211385,   5215999, 5218441, 5374999, 5471619, 5774375,   5785586, 5792093, 5809827]
sdtest = [5823121, 6283224, 6302051, 6353203, 6432059,   6606653, 6669809, 6692340, 6836140, 6852488,   6865626, 6962901, 7031714]
overcontact = [7821450, 7830460, 7835348, 7839027, 7871200,   7877062, 7878402, 7879404, 7881722, 7889628,   7950962, 7973882, 7977261]
octest = [8004839, 8035743, 8039225, 8053107, 8108785,   8111387, 8122124, 8143757, 8177958, 8190491,   8190613, 8192840, 8241252]
ellipsoid = [9848190, 9898401, 9909497, 9948201, 10028352,   10030943, 10032392, 10123627, 10135584, 10148799,   10155563, 10285770, 10288502, 10291683, 10351735,   10417135]
eltest = [10481912, 10600319, 10619506, 10855535, 11135978,   11336707, 11572643, 11714337, 11722816, 11751847,   11825204, 11875706, 12055421, 12059158, 12121738,   12166770]
uncertain = [9237533, 9347868, 9347955, 9456920, 9469350,   9480516, 9532591, 9596355, 9655187, 9713664,   9716456, 9724080]
utest = [9724220, 9832227, 9835416, 9874575, 9964422,   10086746, 10264744, 10350225, 10388897, 10556068,   10684673, 10799558]

quiet = [0]*100
qtest = [0]*100

qui=0
j=0
while 1:
    if (logg[j]>=(6.0-0.0004*teff[j]) or logg[j]>=4.0) and logdata[j,5]<=1 and \
logdata[j,15]<=1 and teff[j]<=6100:
        if qui<100: quiet[qui] = dataset[j,0]
        elif qui<200: qtest[qui-100] = dataset[j,0]
        qui = qui+1
    if qui>=200: break
    j = j+1

p1 = len(rrlyrae + instrip + detached + semidet + overcontact + ellipsoid + quiet)
p2 = p1 - len(quiet)
kidlist1 = [quiet, rrlyrae, instrip, detached, semidet, overcontact, ellipsoid]
testlist1 = [qtest, rtest, itest, dtest, sdtest, octest, eltest]

col=np.empty([2*p1,5],dtype='S10')
labels = np.empty([2*p1,5])

training = np.empty([p1,q])
sampletest = np.empty([p1,q])
pd = np.empty([p1,q])
pdtest = np.empty([p1,q])

h = 0
for i in kidlist1:
    for j in i:
        temp1 = testdata[np.where(dataset[:,0]==j)[0][0]]
        temp2 = plotdata[np.where(dataset[:,0]==j)[0][0]]
        for k in range(0,q):
            training[h,k] = temp1[k]
            pd[h,k] = temp2[k]
        h = h+1

h = 0
for i in testlist1:
    for j in i:
        temp1 = testdata[np.where(dataset[:,0]==j)[0][0]]
        temp2 = plotdata[np.where(dataset[:,0]==j)[0][0]]
        for k in range(0,q):
            sampletest[h,k] = temp1[k]
            pdtest[h,k] = temp2[k]
        h = h+1

training2 = training[100:]
sample2 = sampletest[100:]
pd2 = pd[100:]
pdtest2 = pdtest[100:]

h = 0
for i in (kidlist1 + testlist1):
    for j in i:
        #print g,h,j
        if i==quiet or i==qtest:            # col[:,0] entire set
            col[h] = ['white', 'black', 'white', 'black', 'white']
            labels[h] = [0, -1, 0, -1, 0]
        elif i==rrlyrae or i==rtest:        # col[:,1] variables only
            col[h] = ['magenta', 'magenta', 'magenta', 'magenta', 'green']
            labels[h] = [1, 1, 1, 1, 2]
        elif i==instrip or i==itest:        # col[:,2] combine eclipsing 
            col[h] = ['blue', 'blue', 'blue', 'blue', 'green']
            labels[h] = [3, 3, 3, 3, 2]
        elif i==detached or i==dtest:       # col[:,3] vars only, combine eclipsing
            col[h] = ['cyan', 'cyan', 'green', 'green', 'green']
            labels[h] = [4, 4, 2, 2, 2]
        elif i==semidet or i==sdtest:       # col[:,4] vars versus quiet
            col[h] = ['green', 'green', 'green', 'green', 'green']
            labels[h] = [2, 2, 2, 2, 2]
        elif i==overcontact or i==octest:
            col[h] = ['yellow', 'yellow', 'green', 'green', 'green']
            labels[h] = [5, 5, 2, 2, 2]
        elif i==ellipsoid or i==eltest:
            col[h] = ['orange', 'orange', 'green', 'green', 'green']
            labels[h] = [6, 6, 2, 2, 2]
        elif i==uncertain or i==utest:
            col[h] = ['red', 'red', 'green', 'green', 'green']
            labels[h] = [7, 7, 2, 2, 2]
        h = h+1

#sample = testdata[0:500]
#pdsample = plotdata[0:500]
print np.shape(sampletest)

#fig = pl.figure(1)
#pl.clf()

print "Gaussian Naive Bayes"
gnb = naive_bayes.GaussianNB()
for i in range(0,5):
    if i==1 or i==3:
        X_train = training2
        y_train = col[100:172,i]
        X_test = sample2
        y_test = col[272:,i]
    else:
        X_train = training
        y_train = col[:172,i]
        X_test = sampletest
        y_test = col[172:,i]

    gnb.fit(X_train, y_train)
    y_pred = gnb.predict(X_test)
    
    n=0
    for i in range(0,len(y_pred)):
        if y_pred[i] == y_test[i]:
            #print i, y_pred[i], y_test[i]
            n = n+1
    print '{:3d}/{:3d}, {:2.2%}'.format(n, len(y_test), n*1.0/len(y_test))

#samplecol = gnb.predict(X_test)
#posterior = gnb.predict_proba(X_test)
#for i in range(0,len(y_test)):
    #if y_test[i] != y_pred[i]:
        #print y_test[i], y_pred[i]
        #print posterior[i]

# multinomial naive bayes requires a non-negative training set

print "Bernoulli Naive Bayes"
bnb = naive_bayes.BernoulliNB()
for i in range(0,5):
    if i==1 or i==3:
        X_train = training2
        y_train = col[100:172,i]
        X_test = sample2
        y_test = col[272:,i]
    else:
        X_train = training
        y_train = col[:172,i]
        X_test = sampletest
        y_test = col[172:,i]

    bnb.fit(X_train, y_train)
    y_pred = bnb.predict(X_test)
    
    n=0
    for i in range(0,len(y_pred)):
        if y_pred[i] == y_test[i]:
            #print i, y_pred[i], y_test[i]
            n = n+1
    print '{:3d}/{:3d}, {:2.2%}'.format(n, len(y_test), n*1.0/len(y_test))

print "Random Forest"
# changing n_estimators will improve some classes at the expense of others
for i in range(0,5):
    if i==1 or i==3:
        X_train = training2
        y_train = labels[100:172,i]
        X_test = sample2
        y_test = labels[272:,i]
    else:
        X_train = training
        y_train = labels[:172,i]
        X_test = sampletest
        y_test = labels[172:,i]

    narray = np.zeros(100)
    for j in range(0,100):
        rfc = RandomForestClassifier(n_estimators=30, max_depth=20)
        rfc.fit(X_train, y_train)
        y_pred = rfc.predict(X_test)
    
        for i in range(0,len(y_pred)):
            if y_pred[i] == y_test[i]:
                #print i, y_pred[i], y_test[i]
                narray[j] = narray[j]+1
        #print n*100.0/len(y_test)
    print '{:3.0f}/{:3d}, {:2.2%}, n_estimators=30, max_depth=20'.format(np.mean(narray), len(y_test), np.mean(narray)*1.0/len(y_test))

print "Support Vector Machines"
# no effect from changing degree
for i in range(0,5):
    if i==1 or i==3:
        X_train = training2
        y_train = labels[100:172,i]
        X_test = sample2
        y_test = labels[272:,i]
    else:
        X_train = training
        y_train = labels[:172,i]
        X_test = sampletest
        y_test = labels[172:,i]

    deg = 0
    ncorrect = 0
    mysvm = svm.SVC()
    mysvm.fit(X_train, y_train)
    y_pred = mysvm.predict(X_test)
    
    n=0
    for i in range(0,len(y_pred)):
        if y_pred[i] == y_test[i]:
            #print i, y_pred[i], y_test[i]
            n = n+1
    print '{:3d}/{:3d}, {:2.2%}'.format(n, len(y_test), n*1.0/len(y_test))

print "Gaussian Mixture Models"
# changing n_components will improve so components at the expense of others
for i in range(0,5):
    if i==1 or i==3:
        X_train = training2
        y_train = labels[100:172,i]
        X_test = sample2
        y_test = labels[272:,i]
    else:
        X_train = training
        y_train = labels[:172,i]
        X_test = sampletest
        y_test = labels[172:,i]

    if i>=2: n=3
    else: n=6

    narray = np.zeros(100)
    for j in range(0,100):
        gmm = GMMBayes(n_components=n)
        gmm.fit(X_train, y_train)
        y_pred = gmm.predict(X_test)
    
        for k in range(0,len(y_pred)):
            if y_pred[k] == y_test[k]:
                #print i, y_pred[i], y_test[i]
                narray[j] = narray[j]+1
        #print n*100.0/len(y_test)
    print '{:3.0f}/{:3d}, {:2.2%}, n_components={:d}'.format(np.mean(narray), len(y_test), np.mean(narray)*1.0/len(y_test), n)

'''
def onpick(event):
    ind=event.ind
    s1 = ax1.scatter(X[ind,0],X[ind,1],c=col[ind],lw=1,s=36)
    s2 = ax2.scatter(pd[ind,0],pd[ind,1],c=col[ind],lw=1,s=36)
    s3 = ax3.scatter(pd[ind,4],pd[ind,5],c=col[ind],lw=1,s=36)
    s4 = ax4.scatter(pd[ind,6],pd[ind,7],c=col[ind],lw=1,s=36)
    pl.ion()
    pl.draw()
    s1.set_visible(False)
    s2.set_visible(False)
    s3.set_visible(False)
    s4.set_visible(False)
'''
'''
ax1 = pl.subplot(221,axisbg='black')
ax1.scatter(pd[:,0],pd[:,1],c=col[:,0],lw=0,s=7,picker=True)
pl.xlabel('T_eff')
pl.ylabel('log(g)')

ax2 = pl.subplot(222,axisbg='black')
ax2.scatter(pd[:,2],pd[:,3],c=col[:,0],lw=0,s=7,picker=True)
pl.xlabel('log-first peak height')
pl.ylabel('log-second peak height')

ax3 = pl.subplot(223,axisbg='black')
ax3.scatter(pd[:,4],pd[:,5],c=col[:,0],lw=0,s=7,picker=True)
pl.xlabel('log-first peak period (d)')
pl.ylabel('log-second peak period (d)')

ax4 = pl.subplot(224,axisbg='black')
ax4.scatter(pd[:,8],pd[:,9],c=col[:,0],lw=0,s=7,picker=True)
pl.xlabel('log-amplitude')
pl.ylabel('RMS deviation')

pl.show()
'''
