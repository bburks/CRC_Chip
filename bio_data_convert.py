import csv
import os


def extract_data():

    inputPath = 'input_files/bio_data'
    outputPath = 'output_files/bio_data/'
    conditions = []
    uniqueConditions = []
    labels = ['epithelial', 'endothelial']
    times = [0, 2, 4, 6]


    with open(inputPath + '.csv', newline='') as data:
        reader = csv.reader(data, delimiter=',', quotechar='"')
        next(reader)
        for row in reader:
            [exp, chip, condition] = row[0:3]
            epithelialData = row[3:7]
            endothelialData = row[7:11]
            dataList = [epithelialData, endothelialData]

            conditions.append(condition)
            expNum = conditions.count(condition)
            print(expNum)
            currentPath = outputPath + condition


            if expNum == 1:
                uniqueConditions.append(condition)
                os.mkdir(currentPath)



            with open(currentPath + '/' + str(expNum) +'.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['time'] + times



                )
                for i in range(2):
                    writer.writerow([labels[i]] + dataList[i])



    with open(outputPath + 'condition names.csv', 'w', newline = '') as labels:
                            labelWriter = csv.writer(labels)
                            labelWriter.writerow(uniqueConditions)

if __name__ == "__main__":
    extract_data()
