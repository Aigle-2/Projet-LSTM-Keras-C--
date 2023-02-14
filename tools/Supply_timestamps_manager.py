"""
A function to check a CSV file containing multiple products into files handling indiduals products

...

Attributes
----------

inputPath : str
    the path of the folder
prefixInput : str
    the prefix of the input files
freq : str
    the frequency of the daterange

Return
----------
void

Example
----------
python "/home/esteban/Documents/Optimix/Projet_LSTM_Keras_C++/tools/Supply_timestamps_manager.py" "/home/esteban/Documents/Optimix/Projet_LSTM_Keras_C++/Data/" "supplyProduct_"
"""
import csv
import sys
import os
import re
import shutil
import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset

def supply_timestamps_manager(inputPath, prefixInput, freq='W'): 
    filesList = getFiles(inputPath, prefixInput)
    fields = ['startdate', 'salesqty']
    numberOfProblematicFiles = 0
    for file in filesList:
        print(file)
        try : 
            df = loadDataAndCreateDataframe(inputPath,file,fields)
            analysisResult = generateTimestampsAxis(df,freq)
            if (analysisResult[3] != 0):
                # print(df.iloc[0])
                # if (analysisResult[2] == 1):
                #     df.drop(index=df.index[-1],axis=0,inplace=True)
                numberOfProblematicFiles += 1
                print ('ERROR : ', file, " supposed_daterange size: ", analysisResult[0].size, " actual size : ", df.size, " Number of missing values : ", analysisResult[1].size, " Number of excessive values : ", analysisResult[2].size)
                # print(analysisResult[0])
                if (analysisResult[3] > 0 and analysisResult[3]< 0.08*df.size):
                    # print(analysisResult[0])
                    df = removeExcessiveValuesFromDataFrame(df,analysisResult[2])
                    # print("analysisResult = ", analysisResult)
                    # print('test')
                    if (isExtrapolationPossible(analysisResult[1], 1, freq)):
                        newdf = fixDataByExtrapolation(df, analysisResult[0], analysisResult[1])
                        # print(type(newdf.index))
                        # print("index : ",newdf.index)
                        newdf.index = pd.to_datetime(newdf.index)
                        # print(type(newdf.index))
                        # print("new index : ",newdf.index)
                        exportCSV(newdf,inputPath,file)
                elif (analysisResult[3] < 0):
                    print(df.index.difference(analysisResult[0]))
                else :
                    print(file, ' UNSUITABLE FOR DATA ANALYSIS')
                print("\n")
            else:
                exportCSV(df,inputPath,file)
        except:
            print("ERROR")

    print (round(numberOfProblematicFiles/len(filesList),4)*100, "% of files have timestamps issues")
    return

def loadDataAndCreateDataframe(inputPath,file,fields):
    # print(os.path.abspath(inputPath) + '/' + file)
    df = pd.read_csv(os.path.abspath(inputPath) + '/' + file, header=0, index_col=0, usecols=fields)
    # print(df)
    df = df.reset_index(drop=False)
    df = df.rename(columns={"startdate":"Time"})
    df = df.sort_values(by="Time",ascending=True)
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')
    # df.index = pd.to_datetime(df.index)
    # print(type(df.index))
    return df

def exportCSV(df,inputPath,file):
    # print(len(df.index))
    if (len(df.index)>=156):
        df.to_csv(os.path.abspath(inputPath) + '/corrected' + file) # exporte en csv le df
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

def removeExcessiveValuesFromDataFrame(df,index):
    # print(index, type(index))
    df = df.drop(index)
    return df

def generateTimestampsAxis(df, freq):
    # supposed_daterange = pd.date_range(*(pd.to_datetime([df.index.min(), df.index.max()])), freq=pd.infer_freq(df.index))
    supposed_daterange = pd.date_range(*(pd.to_datetime([df.index.min(), df.index.max()])), freq=freq).strftime('%Y-%m-%d')
    # print("supposed_daterange = ", supposed_daterange, supposed_daterange.size)
    # print("min = ", df.index.min(), type(df.index.min()))
    # print("max = ", df.index.max(), type(df.index.max()))
    # print("calc min = ", supposed_daterange[0], type(supposed_daterange[0]))
    days_offset =  pd.Timestamp(df.index.min()) - pd.Timestamp(supposed_daterange[0])
    # print(days_offset, type(days_offset))
    supposed_daterange_corrected = (pd.date_range(*(pd.to_datetime([df.index.min(), df.index.max()])), freq=freq) + days_offset).strftime('%Y-%m-%d')
    if (supposed_daterange_corrected[-1] != df.index.max()):
        supposed_daterange_corrected = supposed_daterange_corrected.append(pd.Index([df.index.max()]))
        # print("\n\n",supposed_daterange_corrected[-1],df.index.max())
    # print(supposed_daterange_corrected, days_offset, df.index.max(), type(supposed_daterange_corrected), supposed_daterange_corrected.size)
    # print(df.index)
    missing_values = supposed_daterange_corrected.difference(df.index)
    excessive_values = df.index.difference(supposed_daterange_corrected)
    theoritical_data_variation = missing_values.size - excessive_values.size
    # print(excessive_values)
    # print(theoritical_data_variation)
    return [supposed_daterange_corrected,missing_values,excessive_values,theoritical_data_variation]

def isExtrapolationPossible(missingValues, maxConsecutiveMissingValuesAllowed = 0, freq='W'):
    previousValue = ""
    maxConsecutiveMissingValuesDetected = 0
    currentConsecutiveMissingValuesDetected = 0
    for index, value in enumerate(missingValues):
        if (index != 0):
            days_offset = pd.Timestamp(value) - pd.Timestamp(previousValue)
            # print(days_offset)
            if ((days_offset.days == 7 and freq == 'W') or (days_offset.days == 1 and freq == 'D')):
                currentConsecutiveMissingValuesDetected += 1
            else:
                if maxConsecutiveMissingValuesDetected < currentConsecutiveMissingValuesDetected:
                    maxConsecutiveMissingValuesDetected = currentConsecutiveMissingValuesDetected
        previousValue = value
    # print(maxConsecutiveMissingValuesDetected, currentConsecutiveMissingValuesDetected)
    if maxConsecutiveMissingValuesDetected <= currentConsecutiveMissingValuesDetected:
        maxConsecutiveMissingValuesDetected = currentConsecutiveMissingValuesDetected
    # print(missingValues, maxConsecutiveMissingValuesDetected)
    print("missingValues = ", missingValues, "maxConsecutiveMissingValuesDetected = ", maxConsecutiveMissingValuesDetected)
    if (maxConsecutiveMissingValuesAllowed >= maxConsecutiveMissingValuesDetected ):
        # print("maxConsecutiveMissingValuesDetected = ", maxConsecutiveMissingValuesDetected)
        return True
    return False

def fixDataByExtrapolation (df, supposed_daterange_corrected, missing_values):
    # print(df)
    # print(supposed_daterange_corrected)
    # print(missing_values)
    newdf = pd.DataFrame([])
    # print(newdf)
    fixed_values = 0
    fixed_values_countdown = 0
    for index, value in enumerate(supposed_daterange_corrected):
        # if (pd.to_datetime(value).year < 2020):
        if (True):
            if (fixed_values_countdown == 0):
                gapSize = 0
                for index_missing_values, missing_value in enumerate(missing_values):
                    # print(missing_values[index_missing_values])
                    # print(supposed_daterange_corrected[index])
                    while(missing_value == value and gapSize + index <= (supposed_daterange_corrected.size-1) and gapSize + index_missing_values <= (missing_values.size-1) and supposed_daterange_corrected[gapSize+index] == missing_values[gapSize+index_missing_values]):
                        # print(gapSize+index_missing_values)
                        # print("missing_values", missing_values, missing_values.size)
                        # print(supposed_daterange_corrected[gapSize+index], missing_values[gapSize+index_missing_values])
                        gapSize += 1
                    # print("gapSize", gapSize)
                    # missing_values.drop(missing_value)
                # print("gapSize", gapSize)
                # print("current df index : ",index-fixed_values," current sdc idx : ", index, " current fixed value offset : ", fixed_values, "sdc len : ", supposed_daterange_corrected.size, "df len : ", df.size)
                # print("salesqty : ",df.iloc[index-fixed_values,0])
                if(gapSize == 2 and (index < supposed_daterange_corrected.size-2) and index != 0):
                    # print(supposed_daterange_corrected[index])
                    # print(df.loc[index-1])
                    # print("idx ", index, fixed_values)
                    # print(supposed_daterange_corrected.size, df.size)
                    # print(supposed_daterange_corrected[index])
                    # print("value",df.loc[supposed_daterange_corrected[index]])
                    interpolatedvalue1 = int((df.iloc[index+1-fixed_values,0] - df.iloc[index-1-fixed_values,0])*0.33+df.iloc[index-1-fixed_values,0])
                    interpolatedvalue2 = int((df.iloc[index+1-fixed_values,0] - df.iloc[index-1-fixed_values,0])*0.66+df.iloc[index-1-fixed_values,0])
                    # print("interpolatedvalues", df.iloc[index-1,0], interpolatedvalue1, interpolatedvalue2, df.iloc[index+1,0])
                    linedf = pd.DataFrame([interpolatedvalue1,interpolatedvalue2], columns=["salesqty"], index = [supposed_daterange_corrected[index], supposed_daterange_corrected[index+1]])
                    fixed_values += 2
                    fixed_values_countdown += 1
                elif(gapSize == 1 and (index < supposed_daterange_corrected.size-1) and index != 0):
                    # print(supposed_daterange_corrected[index])
                    # print(df.loc[index-1])
                    # print("idx ", index, fixed_values)
                    # print(supposed_daterange_corrected.size, df.size)
                    # print(supposed_daterange_corrected[index])
                    # print("value",df.loc[supposed_daterange_corrected[index]])
                    interpolatedvalue = int((df.iloc[index-1-fixed_values,0] + df.iloc[index-fixed_values,0]) / 2)
                    # print(interpolatedvalue, df.iloc[index-1,0], df.iloc[index+1,0])
                    linedf = pd.DataFrame([interpolatedvalue], columns=["salesqty"], index = [supposed_daterange_corrected[index]])
                    fixed_values += 1 
                    fixed_values_countdown += 0
                elif(gapSize == 0):
                    # print("value",df.loc[supposed_daterange_corrected[index]])
                    linedf = pd.DataFrame([df.loc[supposed_daterange_corrected[index]]], columns=["salesqty"], index = [supposed_daterange_corrected[index]])
                # else:
                #     print(gapSize)
                #     a = 125 + 'sts'
                # if (pd.to_datetime(value).year < 2020):
                #     print(pd.to_datetime(value).year)
                #     print(linedf)
                #     newdf = pd.concat([newdf,linedf])
                # print(newdf.size)
                # print(linedf)
                newdf = pd.concat([newdf,linedf])
            else:
                fixed_values_countdown -= 1
    newdf.index.name = 'Time'
    return newdf

# def getDataHoleWidth(indexDataRange, datarange , missing_values, current_count = 0):
#     nextValueIsPresent = True
#     for index, date in enumerate(datarange):
#         for 
#     if(nextValueIsPresent):
#         return current_count
#     else :
#         return getDataHoleWidth(indexDataRange, missing_values, (current_count + 1))
if __name__ == '__main__':
    # Map command line arguments to function arguments.
    supply_timestamps_manager(*sys.argv[1:])


#86465 86466 86888 92244