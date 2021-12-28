"""Writes and reads csv files so you dont have to. Just stick to the supported
formats or add your own.


Argument order could be made more intuitive, i.e.
times, labels, dataList -> labels, times, dataList.
lots to refactor here and elsewhere if you do this.
"""


import csv

# writes a csv containing times, labels, dataList at the given path
# left column is labels, top row (not including corner) is times, the rest
# is dataList (matrix)
# yes, order should be labels, times dataList
def export(times, labels, dataList, path):

    timeCount = len(times)
    labelCount = len(labels)
    dataListHeight = len(dataList)


    assert labelCount == dataListHeight + 1, "wrong number of labels"


    for i, row in enumerate(dataList):
        assert timeCount == len(row), "wrong number of elements in row " + str(i)


    with open(path + '.csv', 'w', newline = '') as file:
        writer = csv.writer(file)

        writer.writerow([labels[0]] + times)

        for i, row in enumerate(dataList):
            writer.writerow([labels[i + 1]] + row)

# inputs a CSV and outputs [times, labels, dataList]

def extract(path):
    dataList = []
    labels = []
    times = []


    with open(path +'.csv', newline = '') as file:
        reader = csv.reader(file)

        firstRow = next(reader)

        for i, data in enumerate(firstRow):
            if i == 0:
                labels.append(data)
            else:
                times.append(data)

        for i, nextRow in enumerate(reader):
            dataList.append([])
            for j, data in enumerate(nextRow):
                if j == 0:
                    labels.append(data)
                else:
                    dataList[i].append(data)


    return [times, labels, dataList]

# writes a one-line csv

def export_line(labels, path):
    with open(path + '.csv', 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(labels)

# pulls info from a one-line csv

def extract_line(path):
    with open(path +'.csv', newline = '') as file:
        reader = csv.reader(file)
        firstRow = next(reader)
    return firstRow
