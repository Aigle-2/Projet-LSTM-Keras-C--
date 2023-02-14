"""
A function to split a CSV file containing multiple products into files handling indiduals products

...

Attributes
----------

inputPath : str
    the name of the input file
prefixOutput : str
    the prefix of the output files

Return
----------
void

Example
----------
python /home/esteban/Documents/Optimix/Projet_LSTM_Keras_C++/tools/Supply_CSV_Splitter.py "/home/esteban/Documents/Optimix/Projet_LSTM_Keras_C++/Data/data.csv" "supplyProduct_"
"""
import csv
import sys
import os

def supplyCSVSplitter(inputPath, prefixOutput): 
    arrayOfProductLists = []
    arrayOfListNames = []
    with open(inputPath) as csv_file:
        csv_reader = csv.reader(csv_file)
        columns = next(csv_reader)
        type_col = columns.index("productid")
        filePath = os.path.dirname(inputPath)
        for row in csv_reader:
            # print(row)
            if not(row[type_col] in arrayOfListNames):
                # print("debug = ",row[type_col])
                arrayOfListNames.append(row[type_col])
                arrayOfProductLists.append([])
                # print(arrayOfListNames)
            index = arrayOfListNames.index(row[type_col])
                # print(value)
            arrayOfProductLists[index].append(row)
            # print(arrayOfProductLists)
        for list in arrayOfProductLists:
            # print(arrayOfProductLists[0])
            # print(list)
            if os.path.exists(filePath + '/' + prefixOutput + str(list[0][0]) + '.csv'):
             os.remove(filePath + '/' + prefixOutput + str(list[0][0]) + '.csv')
            with open(filePath + '/' + prefixOutput + str(list[0][0]) + '.csv', 'w', encoding='UTF8') as f:
                writer = csv.writer(f)
                # write the header
                writer.writerow(columns)
                # write the data
                for line in list:
                    print(line)
                    writer.writerow(line)
    return

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    supplyCSVSplitter(*sys.argv[1:])