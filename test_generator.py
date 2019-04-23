import dove_dataset

d1,d2,d3 = dove_dataset.CreateDOVeDatasets('.', raw=True)

print("{}, {}, {}, sum: {}".format(len(d1),len(d2),len(d3),sum([len(d1),len(d2),len(d3)])))

i = 0
j = -1
d = 0

print("Starting train set")
for c in d1:
	print(i)
	i += 1
	if len(c) != 10:
		j = i
		print("Short one in d1")
		d = 1

print("Starting validation set")
for c in d2:
	print(i)
	i += 1	
	if len(c) != 10:
		j = i
		print("Short one in d2")
		d = 2

print("Starting test set")
for c in d3:	
	print(i)
	i += 1
	if len(c) != 10:
		j = i
		print("Short one in d3")
		d = 3

print("Done, short one in d{}, number {} accessed".format(d, j))