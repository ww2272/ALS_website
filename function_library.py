import string
import random
import numpy, scipy
import scipy.cluster.hierarchy as hier
import scipy.spatial.distance as dist

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

#find the common genes among the study arrary
def intersection_gene (study_array):
	common_genes = []
	once = True
	for each_study in study_array:
		upgenes = each_study['up_genes']
		dngenes = each_study['down_genes']
		upgenes = [x[0] for x in upgenes]
		dngenes = [x[0] for x in dngenes]
		study_genes = upgenes+dngenes
		while once:
			common_genes += study_genes
			once = False			
		common_genes = list(set(common_genes) & set(study_genes))
	return common_genes

#find all the genes ever occurred in the study arrays
def union_gene (study_array):
	union_genes = []
	for each_study in study_array:
		upgenes = each_study['up_genes']
		dngenes = each_study['down_genes']
		upgenes = [x[0] for x in upgenes]
		dngenes = [x[0] for x in dngenes]
		study_genes = upgenes+dngenes				
		union_genes = list(set(union_genes) | set(study_genes))
	return union_genes

#count the number of appearance of each gene in the union genes, 
#if the count is greather than the set threshold, then keep the gene in the consensus gene array
def get_consensus_genes (study_array, upordown, union_gene, threshold):
	#threshold is the number of occurance of the gene across all studies
	#upordown takes a string that's either 'up_genes' or 'down_genes'
	#union_gene takes a list
	consensus_gene_array = []
	for each_gene1 in union_gene:
		count = 0
		for each_study in study_array:
			upordown_genes = each_study[upordown]
			if upordown_genes != 'platform not supported':
				study_upordown_list = [each_gene[0] for each_gene in upordown_genes]
				if each_gene1 in study_upordown_list:
					count += 1
		if count >= threshold :
			consensus_gene_array.append(each_gene1)
	#print len(consensus_gene_array)
	return consensus_gene_array

def get_intersection_genes (studyarray, upordown, intersection_gene):
	#upordown takes a string that's either 'up_genes' or 'down_genes'
	#intersection_gene takes in an arrary of genes in string format
	intersection_gene_array = []
	for each_study in studyarray:
		upordown_genes_array = []
		upordown_genes = each_study[upordown]
		for each_gene in upordown_genes:
			if each_gene[0] in intersection_gene:
				upordown_genes_array.append(each_gene[0])
		intersection_gene_array = list(set(intersection_gene_array)|set(upordown_genes_array))
	return intersection_gene_array

def makeMatrix (studyarray, consensusGene):
	#takes the studyarray and makes a datamatrix, columnHeader [{GSE, description, index, tissuetype}], and a rowHeader[gene1, gene2, gene3]
	dataMatrix = []
	#make dataMatrix
	for eachGene in consensusGene:
		rowExpressionArray = []
		for eachStudy in studyarray:
			presenceCheck = False
			upGeneArray = eachStudy['up_genes']
			dnGeneArray = eachStudy['down_genes']
			studyGeneArray = upGeneArray + dnGeneArray
			for eachStudyGene in studyGeneArray:
				if eachStudyGene[0] == eachGene:
					rowExpressionArray.append(eachStudyGene[1])
					presenceCheck = True
			if presenceCheck != True:
				rowExpressionArray.append(0)
		dataMatrix.append(rowExpressionArray)
	#make columHeader
	columnHeaderDic = []
	for eachStudy in studyarray:
		columnInfo = {"GSE": eachStudy['GSENum'], "tissueType": eachStudy['tissueType'], 
			"Description": eachStudy['studyDescript'], "Perturbation": eachStudy['perturbation'],
			"Index": eachStudy['studyIndex']}
		columnHeaderDic.append(columnInfo)
	#make rowHeader
	rowHeader = [x for x in consensusGene]
	# print len(dataMatrix), len(consensusGene), len(rowHeader), len(columnHeaderDic), len(studyarray)
	return dataMatrix, columnHeaderDic, rowHeader


def getHeatmapMatrix (dataMatrix=None, columHeader=None, rowHeader=None,  
					row_pdist='cosine', col_pdist='cosine', row_linkage='average', 
					col_linkage='average'):
	'''
	this function returns a json dataset that can be used for the d3 heatmap
	dataMatrix: a python array
	columHeader: a list of strings corresponding to column labels in data, usually study names or conditions
	rowHeader: a list of strings corresponding to column labels in data, usually gene symbols
	row_linkage: linkage method used for rows
	col_linkage: linkage method used for columns 
		options = ['average','single','complete','weighted','centroid','median','ward']
	row_pdist: pdist metric used for rows
	col_pdist: pdist metric used for columns
		options = ['euclidean','minkowski','cityblock','seuclidean','sqeuclidean',
		'cosine','correlation','hamming','jaccard','chebyshev','canberra','braycurtis',
		'mahalanobis','wminkowski']	
	'''
	#convert native python array into a numpy array
	dataMatrix = numpy.array(dataMatrix)

	# compute pdist for rows:
	distanceMatrix_row = dist.pdist(dataMatrix, metric=row_pdist)
	distanceSquareMatrix_row = dist.squareform(distanceMatrix_row)

	#calculate linkage matrix
	linkageMatrix_row = hier.linkage(distanceSquareMatrix_row, method=row_linkage, metric=row_pdist)

	#get the order of the dendrogram leaves
	heatmapOrder_row = hier.leaves_list(linkageMatrix_row)

	# compute pdist for columns:
	distanceMatrix_col = dist.pdist(dataMatrix.T, metric=col_pdist)
	distanceSquareMatrix_col = dist.squareform(distanceMatrix_col)

	#calculate linkage matrix
	linkageMatrix_col = hier.linkage(distanceSquareMatrix_col, method=col_linkage, metric=col_pdist)
	
	#get the order of the dendrogram leaves
	heatmapOrder_col = hier.leaves_list(linkageMatrix_col)

	#reorder the data matrix and row/column headers according to leaves
	orderedDataMatrix = dataMatrix[heatmapOrder_row,:] #first order according to the rows
	orderedDataMatrix = dataMatrix[:, heatmapOrder_col]#then order according to the columns
	rowHeaders = numpy.array(rowHeader)
	orderedRowHeaders = rowHeaders[heatmapOrder_row]
	colHeaders = numpy.array(columHeader)
	orderedColumHeaders = colHeaders[heatmapOrder_col]

	#convert numpy array to list
	orderedRowHeaders = orderedRowHeaders.tolist()
	orderedColumHeaders = orderedColumHeaders.tolist()
	#make the row_nodes json for d3	
	row_nodes = []	
	for eachGene in orderedRowHeaders:
		sort = orderedRowHeaders.index(eachGene)
		row_node = {"sort": sort, "name": eachGene}
		row_nodes.append(row_node)
	
	col_nodes = []
	for eachStudy in orderedColumHeaders:
		sort = orderedColumHeaders.index(eachStudy)
		col_node = {"sort": sort, "name": eachStudy}
		col_nodes.append(col_node)

	links = []
	#loop through the index of the orderedDataMatrix
	for x in range(orderedDataMatrix.shape[0]):
		for y in range(orderedDataMatrix.shape[1]):
			source = x
			target = y
			expressionValue = orderedDataMatrix[x, y]
			each_link = {"source": x, "target": y, "value": expressionValue}
			links.append(each_link)
	#make the final json file for d3 heatmap		
	d3_heatmap_json = {"row_nodes": row_nodes, "col_nodes": col_nodes, "links": links}
	return d3_heatmap_json

 
def get_d3_json (dataMatrix=None, columHeader=None, rowHeader=None):
	#this function is to get d3_json_data without calculating distance matrix, e.g. if only 1 study selected
	dataMatrix = numpy.array(dataMatrix)
	row_nodes = []	
	for eachGene in rowHeader:
		sort = rowHeader.index(eachGene)
		row_node = {"sort": sort, "name": eachGene}
		row_nodes.append(row_node)
	
	col_nodes = []
	for eachStudy in columHeader:
		sort = columHeader.index(eachStudy)
		col_node = {"sort": sort, "name": eachStudy}
		col_nodes.append(col_node)

	links = []
	#loop through the index of the orderedDataMatrix
	for x in range(dataMatrix.shape[0]):
		for y in range(dataMatrix.shape[1]):
			source = x
			target = y
			expressionValue = dataMatrix[x, y]
			each_link = {"source": x, "target": y, "value": expressionValue}
			links.append(each_link)
	#make the final json file for d3 heatmap		
	d3_heatmap_json = {"row_nodes": row_nodes, "col_nodes": col_nodes, "links": links}
	return d3_heatmap_json

















	
