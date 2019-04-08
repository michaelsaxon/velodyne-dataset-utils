import numpy as np
import dove_dataset
import matplotlib.pyplot as plt

d = dove_dataset.DOVeDataset('.')

azumithcounts = []
n = len(d)
for ci in range(n):
	clip = d[ci]
	for frame in range(len(clip)):
		azumithcounts.append(clip[frame]['azumiths'].shape[0])
	print("{}/{}".format(ci,n))
		
plt.hist(azumithcounts,bins='auto')
plt.set_xlabel('N detections')
plt.set_ylabel('N frames')
plt.set_title('Detections per Frame for Velodyne HDL32E')
plt.show()
