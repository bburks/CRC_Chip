import crc_models as cm
import matplotlib.pyplot as plt


#creates a simple model, runs it, then plots the results.


crc = cm.SimplestModel(1.1, 1, 0.1, 0.1, 100, 0, 0)

crc.run(30)

crc.make_history_graph()
crc.show_history_graph()
