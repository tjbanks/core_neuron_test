import h5py
import matplotlib.pyplot as plt
import numpy as np

first_col = np.loadtxt("voltage_reports/voltage_report_gid_1.txt")[:, 0]
second_col = np.loadtxt("voltage_reports/voltage_report_gid_1.txt")[:, 1]

plt.plot(first_col, second_col)
plt.savefig('voltage_test.png')
