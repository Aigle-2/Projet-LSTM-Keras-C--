"""
A function to check a CSV file containing multiple products into files handling indiduals products

...

Attributes
----------

inputPath : str
    the name of the input file
prefixInput : str
    the prefix of the output files

Return
----------
void

Example
----------
python /home/esteban/Documents/Optimix/Projet_LSTM_Keras_C++/tools/Supply_shortage_manager.py "/home/esteban/Documents/Optimix/Projet_LSTM_Keras_C++/Data" "correctedsupplyProduct"
"""
import csv
import sys
import os
import re
import shutil
import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset

def supply_shortage_manager(inputPath, prefixInput): 
    filesList = getFiles(inputPath, prefixInput)
    if (len(filesList)==0):
        print("No file found.")
        return
    fields = ['Time', 'salesqty']
    for file in filesList:
        print(file)
        df = pd.read_csv(os.path.abspath(inputPath) + '/' + file, header=0, index_col=0, usecols=fields)
        # print(df)
        newdf = generateShortagesAxis(df)
        newdf.to_csv(os.path.abspath(inputPath) + '/' + file)
    #     if (analysisResult[3] != 0):
    #         # print(df.iloc[0])
    #         # if (analysisResult[2] == 1):
    #         #     df.drop(index=df.index[-1],axis=0,inplace=True)
    #         numberOfProblematicFiles += 1
    #         print ('ERROR : ', file, " supposed_daterange size: ", analysisResult[0].size, " actual size : ", df.size, " Number of missing values : ", analysisResult[1].size, " Number of excessive values : ", analysisResult[2].size)
    #         # print(analysisResult[0])
    #         if (analysisResult[3] > 0 and analysisResult[3]< 0.08*df.size):
    #             # print(analysisResult[0])
    #             df = removeExcessiveValuesFromDataFrame(df,analysisResult[2])
    #             # print("analysisResult = ", analysisResult)
    #             # print('test')
    #             if (isExtrapolationPossible(analysisResult[1], 1)):
    #                 newdf = fixDataByExtrapolation(df, analysisResult[0], analysisResult[1])
    #                 # print(type(newdf.index))
    #                 # print("index : ",newdf.index)
    #                 newdf.index = pd.to_datetime(newdf.index)
    #                 # print(type(newdf.index))
    #                 print("index : ",newdf.index)
    #                 newdf.to_csv(os.path.abspath(inputPath) + '/corrected' + file) # exporte en csv le df
    #         elif (analysisResult[3] < 0):
    #             print(df.index.difference(analysisResult[0]))
    #         else :
    #             print(file, ' UNSUITABLE FOR DATA ANALYSIS')

    # print (round(numberOfProblematicFiles/len(filesList),4)*100, "% of files have timestamps issues")
    return

def getFiles(dire, prefix):
    folder =  os.path.abspath(dire)
    filesList = []
    for filename in os.listdir(folder):
        if filename.startswith(prefix):
            # print('filename', filename)
            filesList.append(filename)
    # print (filesList)
    return filesList

def generateShortagesAxis(df):
    average = df["salesqty"].mean()
    dateList = df.salesqty[df.salesqty < average/4].index.tolist()
    print("Index of shortages data points = ",dateList)
    df.loc[dateList,'salesqty'] = average
    dateList2 = df.salesqty[df.salesqty <= average/4].index.tolist()
    print("Index of shortages data points after fixing attempt = ",dateList2)
    return df
    # print(df)

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    supply_shortage_manager(*sys.argv[1:])


#86465 86466 86888 92244