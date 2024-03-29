import numpy as np
import copy

### DEFAULT FILENAMES
TRAINING_NAME = "hw4train.txt"
TEST_NAME = "hw4test.txt" 
DICTIONARY_NAME = "hw4dictionary.txt"

class Perceptron:

	#make sure everything is in numpy
	def __init__(sf):

		sf.input_data, sf.input_label = sf.read_data(TRAINING_NAME)

		sf.test_data, sf.test_label = sf.read_data(TEST_NAME)

		sf.dict = sf.read_data(DICTIONARY_NAME, True)

		#shape of input_data == 2000, 891
		#initialize to all 0's
		sf.weight_mat = np.zeros(sf.input_data.shape[1])

		#save weigth count and weights for voted and averaged perceptrons
		sf.weight_count = []
		sf.all_weight_mat = []

		#for averaged perceptron algo
		sf.running_avg = np.zeros(sf.weight_mat.shape)
		
		sf.train_err = []

		sf.test_err = []

	def read_data(sf, filename, isDict=None):
		#read test train and label data

		print("Loading %s ..." %filename)

		filehandle = open(filename, "r")
		line = filehandle.readline()
		data = []
		
		while line != "":
			line = line.split()
			data += [line]
			line = filehandle.readline()
		
		if(isDict == True):
			return data

		data = np.array(data)
		data = data.astype(float)

		print(filename,"loaded : Dim",data.shape)
		return data[:,:-1], data[:,-1]


	'''
	what are we classifying? what are we learning? what do these
	test and data points correspond to and labels to?
	'''

	'''

	intuitively and logically think why is it a problem to run all 1 labels
	first and run all -1 labels next --> how does this affect the updates 
	of the weight matrix -- why should you make sure to shuffle the data
	randomly before training the perceptron.

	'''

	def perceptron(sf, data, label, test_data, test_label, weight_mat):

		num_passes = 2

		#is the hyperplane getting updated every time
		#we compute a new weight vector?
		#such that the weigth vector is always normla to the 
		#hyperplane?

		#print "data.shape: ", data.shape
		#print "label.shape: ", label.shape

		print("Running Regular Perceptron!")

		for t in range(num_passes):         
			for i in range(data.shape[0]):
				
				dot_XW = np.dot(data[i], weight_mat)
				#print "dot prod: ", dot_XW
				#print "sign of dot prod: ", np.sign(dot_XW)
				if(label[i]*dot_XW <= 0):
					weight_mat = weight_mat + ( label[i]*data[i] )
					#print "i label[i]: ", i, ": ", label[i]

				#if (i == 0):
				#print "weights: ", weight_mat				

			sf.train_err += [sf.test_perceptron(data, label, weight_mat)] 
			print("train err after", t+1 ,"pass:", sf.train_err[-1])
			sf.test_err +=  [sf.test_perceptron(test_data, test_label, weight_mat)]
			print("test err after", t+1, "pass:", sf.test_err[-1])

	def test_perceptron(sf, data, label, weight_mat):
		#predict output for normal perceptron

		err = 0.0
		for i in range(data.shape[0]):
			dot_YW = np.dot(data[i], weight_mat)
			class_sign = np.sign(dot_YW)

			if(class_sign != label[i]):
				err += 1

		return err/data.shape[0]


	def voted_perceptron(sf, data, label, test_data, test_label):
		count = 1
		num_passes = 3

		weight_mat = np.zeros(sf.input_data.shape[1])

		print("Running Voted Perceptron!")

		for t in range(num_passes):        
			for i in range(len(data)):
				dot_XW = np.dot(data[i], weight_mat)
				#print "dot_XW: ", dot_XW
				if(label[i]*dot_XW <= 0):
					temp_weight_mat = weight_mat + (label[i]*data[i])
					
					#print "i label[i]: ", i, ": ", label[i]
					
					#append for the previous matrix
					sf.all_weight_mat.append(copy.copy(weight_mat))				
					
					sf.weight_count.append(count)

					weight_mat = temp_weight_mat 
					count = 1
					
				else:
					count += 1

			#print "sf.all_weight_mat.shape: ", len(sf.all_weight_mat)
			#print "sf.weight_count: ", len(sf.weight_count)
			#print "sf.weight_count: ", sf.weight_count
			#print "sf.all_weight_mat: ", sf.all_weight_mat
			
			sf.train_err += [sf.test_voted_perceptron(data, label)]
			print("train err after", t+1, "pass:", sf.train_err[-1])

			sf.test_err += [sf.test_voted_perceptron(test_data, test_label)]
			print("test err after", t+1, "pass:", sf.test_err[-1])

	def test_voted_perceptron(sf, data, label):

		sum_sign = 0.0
		err = 0.0
		for t in range(len(data)):
			sum_sign = 0.0
			#you can totally vectorize this loop
			for i in range(len(sf.all_weight_mat)):

				dot_WY = np.dot(sf.all_weight_mat[i],data[t])
				sum_sign += sf.weight_count[i]*np.sign(dot_WY)

				#final sign or class of test data t
			class_t = np.sign(sum_sign)

			if(class_t != label[t]):
				err += 1
				#print "sum_sign: ", sum_sign
		return err/data.shape[0]

	#think about why would voted and averaged perceptron give you the
	#same result?!

	def averaged_perceptron(sf, data, label, test_data, test_label, running_avg):
		
		print("Running Averaged Perceptron!")

		weight_mat = np.zeros(sf.input_data.shape[1])
		count = 1
		num_passes = 4
		for t in range(num_passes):         
			for i in range(len(data)):
				dot_XW = np.dot(data[i], weight_mat)
				if(label[i]*dot_XW <= 0):
					temp_weight_mat = weight_mat + (label[i]*data[i])
		
					#append for the previous matrix
					running_avg += weight_mat*count
					weight_mat = temp_weight_mat

					#print "i label[i]: ", i, ": ", label[i]

					count = 1        
				else:
					count += 1			

			sf.train_err += [sf.test_averaged_perceptron(data, label, running_avg)]
			print("train err after", t+1, "pass:", sf.train_err[-1])
			sf.test_err += [sf.test_averaged_perceptron( test_data, test_label, running_avg)]
			print("test err after", t+1, "pass:", sf.test_err[-1])

		####### CHANGE THIS TO 3 #############
		topK = 3
		sf.interpret_averaged_perceptron(topK)

	def test_averaged_perceptron(sf, data, label, running_avg):

		sum_sign = 0.0
		err = 0.0
		for t in range(len(data)):
			sum_sign = 0.0
			#you can totally vectorize this loop
			dot_WY = np.dot(running_avg,data[t])

			#final sign or class of test data t
			class_t = np.sign(dot_WY)

			if(class_t != label[t]):
				err += 1 
				#print err

		per = err/data.shape[0]
		
		return per

	'''
	
	what does it mean for every dim/axis to have a word associated with it?
	why would words correspond to certain coordinates?
	Three highest coordinates are those with ...strongly and 
	three lowest coordinates are those with ...strongly why so?

	'''
	def interpret_averaged_perceptron(sf, topK):

		sorted_weights_ind = np.argsort(sf.running_avg)

		#print sorted_weights_ind

		#3 lowest dimensions
		low_dim = []
		for x in range(topK):
			low_dim += [sorted_weights_ind[x]]

		#print low_dim

		#3 highest dimensions
		high_dim = []
		for x in range(topK):
			high_dim += [sorted_weights_ind[-1*(x+1)]]

		#print high_dim

		#3 words that represent positive class strongly
		for x in range(len(low_dim)):
			print(sf.dict[low_dim[x]][0])

		#3 words that represent negative class strongly
		for x in range(len(high_dim)):
			print(sf.dict[high_dim[x]][0])




	def classify_A_VS_B(sf, a, b=None):

		if(b != None):
			#train
			labels_ind_a =  np.where(sf.input_label == a)[0]
			labels_ind_b =  np.where(sf.input_label == b)[0]

			#test
			labels_ind_a_T =  np.where(sf.test_label == a)[0]
			labels_ind_b_T =  np.where(sf.test_label == b)[0]
		
		if(b == None):
			#train
			labels_ind_a =  np.where(sf.input_label == a)[0]
			labels_ind_b =  np.where(sf.input_label != a)[0]

			#test
			labels_ind_a_T =  np.where(sf.test_label == a)[0]
			labels_ind_b_T =  np.where(sf.test_label != b)[0]
		
		#print "labels_inx_1: ", labels_ind_1
		#print "labels_idx_2: ", labels_ind_2
		
		data = np.vstack((sf.input_data[labels_ind_a,:],sf.input_data[labels_ind_b,:]))

		#print "data[3]: ", data[3]
		label_a = sf.input_label[labels_ind_a].reshape(len(labels_ind_a),1)		
		label_a[:,0] = 1

		label_b = sf.input_label[labels_ind_b].reshape(len(labels_ind_b),1)
		label_b[:,0] = -1

		#print "labels_1[690]: ", label_1
		#print "labels_2[690], ", label_2

		label = np.vstack((label_a,label_b))

		#print "label[3]: ", label[3]

		train_data_label = np.hstack((data, label))

		np.random.shuffle(train_data_label)

		#print "data_label ", data_label
		data = train_data_label[:, :-1]
		#print "data ", data		
		label = train_data_label[:, -1]
		#print "label ", label
		
		data_test = np.vstack((sf.test_data[labels_ind_a_T,:],sf.test_data[labels_ind_b_T,:]))

		label_a = sf.test_label[labels_ind_a_T].reshape(len(labels_ind_a_T),1)
		label_a[:,0] = 1
		
		label_b = sf.test_label[labels_ind_b_T].reshape(len(labels_ind_b_T),1)		
		label_b[:,0] = -1

		label_test = np.vstack((label_a,label_b))

		return (data, label, data_test, label_test)

	def get_data_AvsB(sf, a, b=None):
		# a = 1
		# b = -1
		all_data = np.hstack((sf.input_data, sf.input_label.reshape((sf.input_label.shape[0],1))))
		all_test_data = np.hstack((sf.test_data, sf.test_label.reshape((sf.test_label.shape[0],1))))

		if b == None:
			# b is the rest of labels
			for i in range(all_data.shape[0]):
				if all_data[i,-1] == a:
					all_data[i,-1] = 1
				else:
					all_data[i,-1] = -1

			for i in range(all_test_data.shape[0]):
				if all_test_data[i,-1] == a:
					all_test_data[i,-1] = 1
				else:
					all_test_data[i,-1] = -1
		else:
			# b is a label
			rows_not_used = []
			for i in range(all_data.shape[0]):
				if all_data[i,-1] == a:
					all_data[i,-1] = 1
				elif all_data[i,-1] == b:
					all_data[i,-1] = -1
				else:
					rows_not_used += [i]
			all_data = np.delete(all_data,rows_not_used,0)

			rows_not_used = []
			for i in range(all_test_data.shape[0]):
				if all_test_data[i,-1] == a:
					all_test_data[i,-1] = 1
				elif all_test_data[i,-1] == b:
					all_test_data[i,-1] = -1
				else:
					rows_not_used += [i]
			all_test_data = np.delete(all_test_data, rows_not_used,0)

		return (all_data[:,:-1], all_data[:,-1], all_test_data[:,:-1], all_test_data[:,-1])



	def run_all_perceptron_algorithms(sf):
		
		####REMEMBER TO RESET VARIABLES######

		data, label, data_test, label_test = sf.get_data_AvsB(1, 2)
		
		sf.perceptron(data, label, data_test, label_test, sf.weight_mat)

		####REMEMBER TO RESET VARIABLES######
		
		sf.voted_perceptron(data, label, data_test, label_test)

		####REMEMBER TO RESET VARIABLES######

		sf.averaged_perceptron(data, label, data_test, label_test, sf.running_avg)
		
		


	def run_one_vs_all(sf):

		data1, label1, data_test1, label_test1 = sf.get_data_AvsB(1)
		weight_mat_1 = np.zeros(sf.input_data.shape[1])
		sf.perceptron(data, label, data_test, label_test, weight_mat_1)

		data2, label2, data_test2, label_test2 = sf.get_data_AvsB(2)
		weight_mat_2 = np.zeros(sf.input_data.shape[1])
		sf.perceptron(data, label, data_test, label_test, weight_mat_2)

		data3, label3, data_test3, label_test3 = sf.get_data_AvsB(3)
		weight_mat_3 = np.zeros(sf.input_data.shape[1])
		sf.perceptron(data, label, data_test, label_test, weight_mat_3)
		
		data4, label4, data_test4, label_test4 = sf.get_data_AvsB(4)		
		weight_mat_4 = np.zeros(sf.input_data.shape[1])
		sf.perceptron(data, label, data_test, label_test, weight_mat_4)

		data5, label5, data_test5, label_test5 = sf.get_data_AvsB(5)
		weight_mat_5 = np.zeros(sf.input_data.shape[1])
		sf.perceptron(data, label, data_test, label_test, weight_mat_5)
		
		data6, label6, data_test6, label_test6 = sf.get_data_AvsB(6)
		weight_mat_6 = np.zeros(sf.input_data.shape[1])
		sf.perceptron(data, label, data_test, label_test, weight_mat_6)



if __name__ == '__main__':

	ptrn = Perceptron()
	
	ptrn.run_all_perceptron_algorithms()
	#ptrn.run_one_vs_all()