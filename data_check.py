import h5py
import matplotlib.pyplot as plt

F = h5py.File('output/v_report.h5')
plt.plot(F['report']['biophysical']['data'][:])
plt.savefig('bmtk_test.png')


