#import csv
import dynamic
#import crc_models as cm
#import numpy as np
#from scipy.linalg import expm, inv, logm
# main function





def test():
    def multiply(x, y):
        return x * y

    multiply = dynamic.Dynamic(multiply)

    list = []
    for i, j in zip([1, 2, 1, 1, 2, 1], [2, 1, 2, 1, 2, 1]):
        list.append(multiply(i, j))
        print(i, j)
    print(list)
    print(multiply.saved)

    



if __name__ == '__main__':
    test()
