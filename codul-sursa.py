# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 14:52:40 2020
ProgArabi: Impreuna creem o lume mai buna ( Algoritm prezicere DDI-uri)

Creat pentru Hackathlon-ul EduHack 2020 - partea EduHealth

"""

import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV
from sklearn import svm
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.decomposition import PCA
from sklearn import metrics
import math
from numpy import linalg as LA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from keras.layers.merge import concatenate
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import precision_recall_curve
import gzip
import pandas as pd
import pdb
import random
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from keras import optimizers
from random import randint
import scipy.io
from keras.models import Sequential
from keras.layers.core import Dropout, Activation, Flatten
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import PReLU
from keras.utils import np_utils, generic_utils
from keras.optimizers import SGD, RMSprop, Adadelta, Adagrad, Adam
from keras.layers import normalization
from keras.layers.recurrent import LSTM
from keras.layers.embeddings import Embedding
from keras import regularizers
from keras.constraints import maxnorm
from keras.layers import  normalization
from keras import regularizers
from sklearn.metrics.pairwise import euclidean_distances
from keras.layers import merge
import sklearn
from operator import itemgetter
from heapq import nlargest
from scipy.spatial.distance import pdist, squareform
from keras.constraints import maxnorm
from keras.layers import Input,Dense,Add
from sklearn.metrics import f1_score

#--------------------------------------------------
#Algoritm Prezicere biochimica Eduhack2020 - functii


def prepare_data(seperate=False):
    drug_fea = np.loadtxt("offsideeffect_Jacarrd_sim.csv",dtype=float,delimiter=",") ##Importare Data
    interaction = np.loadtxt("drug_drug_matrix.csv",dtype=int,delimiter=",") ## Importare Matrice
    train = []
    label = []
    tmp_fea=[]
    drug_fea_tmp = []
    for i in range(0, interaction.shape[0]):
        for j in range(0, interaction.shape[1]):
            label.append(interaction[i,j])
            drug_fea_tmp = list(drug_fea[i])
            if seperate:
        
                 tmp_fea = (drug_fea_tmp,drug_fea_tmp)

            else:
                 tmp_fea = drug_fea_tmp + drug_fea_tmp
            train.append(tmp_fea)

    return np.array(train), label
#--------------------------------------------------------------
def calculate_performace(test_num, pred_y,  labels): ## functie calculare performanta
    tp =0 ##True Pozitives
    fp = 0 ## False Pozitives
    tn = 0 ## T Negative
    fn = 0 ## F Negative
    for index in range(test_num): ## Incrementam fiecare punct si-l clasam in una din ele (True pozitive/False Pozitive, True Negative/False Negative)
        if labels[index] ==1:
            if labels[index] == pred_y[index]:
                tp = tp +1
            else:
                fn = fn + 1
        else:
            if labels[index] == pred_y[index]:
                tn = tn +1
            else:
                fp = fp + 1 
    acc = float(tp + tn)/test_num
    if tp == 0 and fp == 0: # Daca este 0 inseamna ca nu avem o predictie inseamna ca pot avea sau nu efecte adverse
        precision = 0
        MCC = 0
        sensitivity = float(tp)/ (tp+fn)
        specificity = float(tn)/(tn + fp)
    else:
        precision = float(tp)/(tp+ fp)
        sensitivity = float(tp)/ (tp+fn)
        specificity = float(tn)/(tn + fp)
        MCC = float(tp*tn-fp*fn)/(np.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)))
    return acc, precision, sensitivity, specificity, MCC ##Intoarcem precision,acc,sensivi,specifity
#-----------------------------------------------------
def transfer_array_format(data): ##Appenduim matricile
    formated_matrix1 = []
    formated_matrix2 = []
    for val in data:
        formated_matrix1.append(val[0])
        formated_matrix2.append(val[1])
    return np.array(formated_matrix1), np.array(formated_matrix2)
#-------------------------------------------------------
def preprocess_labels(labels, encoder=None, categorical=True):
    if not encoder:
        encoder = LabelEncoder()
        encoder.fit(labels)
        y = encoder.transform(labels).astype(np.int32)
    if categorical:
        y = np_utils.to_categorical(y)
        print(y)
    return y, encoder
#------------------------------------------------------
def preprocess_names(labels, encoder=None, categorical=True): ##Encodare
    if not encoder:
        encoder = LabelEncoder()
        encoder.fit(labels)
    if categorical:
        labels = np_utils.to_categorical(labels)
    return labels, encoder
#------------------------------------------------------
def Prezicere(input_dim): ##Functia Noastra
    model = Sequential()
    model.add(Dense(input_dim=input_dim, output_dim=400,init='glorot_normal'))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(input_dim=400, output_dim=300,init='glorot_normal'))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(input_dim=300, output_dim=2,init='glorot_normal'))
    model.add(Activation('sigmoid'))
    sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='binary_crossentropy', optimizer=sgd)                  
    return model
#--------------------------------------------------
    #SNF Methods
    

def FindDominantSet(W,K): ##Ce Matrice este cea mai ok
	m,n = W.shape
	DS = np.zeros((m,n))
	for i in range(m):
		index =  np.argsort(W[i,:])[-K:] # Cel mai apropiat K Vecin
		DS[i,index] = W[i,index] # pastreaza doar vecinii apropiati

	#normalizam in functie de suma
	B = np.sum(DS,axis=1)
	B = B.reshape(len(B),1)
	DS = DS/B
	return DS



def normalized(W,ALPHA): #Subprogram de normalizare
	m,n = W.shape
	W = W+ALPHA*np.identity(m)
	return (W+np.transpose(W))/2







def SNF(Wall,K,t,ALPHA=1):
	C = len(Wall)
	m,n = Wall[0].shape

	for i in range(C):
		B = np.sum(Wall[i],axis=1)
		len_b = len(B)
		B = B.reshape(len_b,1)
		Wall[i] = Wall[i]/B
		Wall[i] = (Wall[i]+np.transpose(Wall[i]))/2



	newW = []
	

	for i in range(C):
		newW.append(FindDominantSet(Wall[i],K))
		

	Wsum = np.zeros((m,n))
	for i in range(C):
		Wsum += Wall[i]


	for iteration in range(t):
		Wall0 = []
		for i in range(C):
			temp = np.dot(np.dot(newW[i], (Wsum - Wall[i])),np.transpose(newW[i]))/(C-1)
			Wall0.append(temp)

		for i in range(C):
			Wall[i] = normalized(Wall0[i],ALPHA)

		Wsum = np.zeros((m,n))
		for i in range (C):
			Wsum+=Wall[i]

	W = Wsum/C
	B = np.sum(W,axis=1)
	B = B.reshape(len(B),1)
	W/=B
	W = (W+np.transpose(W)+np.identity(m))/2
	return W

#-----------------------------
    #Similarity Selection
def read_Sim_Calc_Entropy(fname,cutoff):
        entropy_exclude_zero_sumRow=[]
        max_entropy=0.0
        cutoff=float(cutoff)
        entropy=[]
        small_number= 1*pow(10,-16)
        arr = np.loadtxt(fname, delimiter=',')
        np.fill_diagonal(arr,0)
        row,col = arr.shape
        aIndices_nonZero=[]
        max_entropy = float(math.log(row,2))

        for i in range(row):
                for j in range(col):
                        if arr[i][j]<cutoff:
                                arr[i][j]=0
        
        for i in range(len(arr)):
                row_sum =arr[i].sum() 
                row_entropy=0

                if row_sum == 0:
                        entropy.append(0)
                        
                if row_sum > 0:
                        aIndices_nonZero.append(i)
                        arr[i] +=small_number 
                        row_sum = arr[i].sum()
        for j in range(len(arr[i])):
                                v= arr[i][j]
                                cell_edited = (v)/row_sum
                                #print 'cell_edited',cell_edited
                                row_entropy= row_entropy+(cell_edited * math.log(cell_edited,2))
                                 #print 'row_entropy',row_entropy
                                row_entropy =row_entropy*-1
                                entropy.append(row_entropy)

        for x in aIndices_nonZero:            
                entropy_exclude_zero_sumRow.append(entropy[x])
        
        return np.mean(entropy),np.mean(entropy_exclude_zero_sumRow),round(max_entropy,2)
#---------------------------------------------------------------------------------------------------
def removeRedundancy(ranked_entropy_simType,all_euclideanDist_Sim):
        flT = 0.6
        m = 0
        iMEnd = len(ranked_entropy_simType)
        while m < iMEnd:
                A_simType = ranked_entropy_simType[m]
                n = m+1
                iNEnd = len(ranked_entropy_simType)
                while n < iNEnd:
                        B_simType = ranked_entropy_simType[n]

                        if A_simType+','+B_simType in all_euclideanDist_Sim:
                                key=A_simType+','+B_simType
                        if B_simType+','+A_simType in all_euclideanDist_Sim:
                                key=B_simType+','+A_simType

                        flMax = all_euclideanDist_Sim[key]
                        if flMax > flT:
                                #oMC.deleteMotif(sMotB)
                                del ranked_entropy_simType[n]
                        else:
                                n += 1
                        iNEnd = len(ranked_entropy_simType)
                m += 1
                iMEnd = len(ranked_entropy_simType)
        print('ranked_entropy_simType', ranked_entropy_simType)

        return ranked_entropy_simType
#--------------------------------------------------------------------------------








