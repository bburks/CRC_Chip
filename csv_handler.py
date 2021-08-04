import csv



# writes a csv containing times, labels, dataList at the given path

def export_to_csv(times, labels, dataList, path):
    with open(path + '.csv', 'w', newline = '') as file:
        writer = csv.writer(file)

        writer.writerow([labels[0]] + times)

        for i, row in enumerate(dataList):
            writer.writerow([labels[i + 1]] + row)

# inputs a CSV and outputs [times, labels, dataList]
# dataList is a list of lists.

def extract_from_csv(path):
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
                times.append(float(data))

        for i, nextRow in enumerate(reader):
            dataList.append([])
            for j, data in enumerate(nextRow):
                if j == 0:
                    labels.append(data)
                else:
                    dataList[i].append(float(data))


    return [times, labels, dataList]

# writes a one-line csv

def export_line_to_csv(labels, path):
    with open(path + '.csv', 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(labels)

# pulls info from a one-line csv

def extract_line_from_csv(path):
    with open(path +'.csv', newline = '') as file:
        reader = csv.reader(file)
        firstRow = next(reader)
    return firstRow
