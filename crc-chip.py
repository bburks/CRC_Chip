import simplest_models as sm
import matplotlib.pyplot as plt

crc = sm.SimplestModelAlternate(1.03, 1, 0.1, 0.1, 100, 0, 0)

crc.run(100)






growFigure, Ax = plt.subplots()
Ax.plot(crc.get_history()[0], crc.get_history()[1], label='grow')
Ax.plot(crc.get_history()[0], crc.get_history()[2], label='go')
Ax.plot(crc.get_history()[0], crc.get_history()[3], label='gone')

#growFigure.show()
plt.legend()
plt.show()
