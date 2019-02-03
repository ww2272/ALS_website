from flask import Flask, jsonify, request, render_template, send_from_directory, redirect, url_for, json, jsonify
from function_library import id_generator, intersection_gene, union_gene, get_consensus_genes, get_intersection_genes, makeMatrix, getHeatmapMatrix, get_d3_json
import json
import requests
import numpy, scipy
import scipy.cluster.hierarchy as hier
import scipy.spatial.distance as dist
 
app = Flask(__name__)      
 
'''
This handler is intended to make the server serve statically, so when putting a file path to the browser,
the browser interpretes the html file directly, instead of letting flask renders the html first. But
I found that flask can serve statically, so this function is unnecessary. But I'm not entirely sure. 
Uncomment this function when anything goes run.
'''
'''  
@app.route('/<path:path>')
def templates_folder(path):
	return send_from_directory('', path)
	'''


#post the gene sets to L1000CDS website to look for drugs that reverse the signature
@app.route('/L1000CDS', methods=['POST'])
def getShareId ():
	payload = request.json
	url = 'http://amp.pharm.mssm.edu/L1000CDS2/query'
	headers = {'content-type':'application/json'}
	r = requests.post(url,data=json.dumps(payload),headers=headers)
	resGeneSet = r.json()
	shareId = resGeneSet['shareId']
	return shareId



@app.route('/results', methods=['POST'])
#handle submit request
#calculate consensus genes, construct matrix, perform distance calculation
def render_results():	
	study_array = request.json 
	num_study = len(study_array)

	if num_study < 3:
		#when number of studies is fewer than 3, take intersection of genes as consensus genes													
		intersection_genes = intersection_gene(study_array)
		up_intersection_genes = get_intersection_genes(study_array, "up_genes", intersection_genes)
		dn_intersection_genes = get_intersection_genes(study_array, "down_genes", intersection_genes)
		union_genes = union_gene (study_array)
		threshold = num_study
		print "study number is fewer than 3"
		#contructs the data to be sent to the html template
		statsArray = [{"#Study Selected":str(num_study)}, {"#Up Genes": str(len(up_intersection_genes))}, {"#Down Genes": str(len(dn_intersection_genes))}, 
		{"#Common Genes": str(len(intersection_genes))}, {"#Union Genes": str(len(union_genes))}, {"Threshold": str(threshold) + " times occurance"}]
		#get heatmap processed data 
		dataMatrix, columnHeaderDic, rowHeader = makeMatrix(study_array, intersection_genes)
		columnHeader = []
		for eachStudy in columnHeaderDic:
			columnTitle = eachStudy["GSE"] + ',' + str(eachStudy['Index'])
			columnHeader.append(columnTitle)
		if num_study == 1: #when only 1 study selected, cannot perform heatmap matrix
			d3_json_data = get_d3_json(dataMatrix=dataMatrix, columHeader=columnHeader, rowHeader=rowHeader)
		
		else:	
			d3_json_data = getHeatmapMatrix(dataMatrix=dataMatrix, columHeader=columnHeader, rowHeader=rowHeader,  
						row_pdist='cosine', col_pdist='cosine', row_linkage='average', 
						col_linkage='average')
		#send the up and down genes, stats of the selected study, the heatmap matrix data for constructing d3 graph
		#to the layout.html template and renders it into a new html and then save the new html
		new_html = render_template('layout.html', study_array_up = up_intersection_genes, 
					study_array_dn = dn_intersection_genes, statsArray = statsArray, d3_json_data = d3_json_data)
		
		random_id = id_generator(6)
		with open ('/Users/weiqingwangair/Documents/ALS_website/app/static/layout%s.html' %random_id, 'w+') as new_html_file:
		# with open ('/Users/weiqingwang/Documents/als_website/als_flask/app/static/layout%s.html' %random_id, 'w+') as new_html_file:
			new_html_file.write(new_html)
		return 'http://127.0.0.1:5050/static/layout%s.html' %random_id
	else:
		#test to see whether intersection gene is greater than 50, if greater than 50, then plot the heatmap using these
		#intersection genes
		union_genes = union_gene(study_array)
		intersection_genes = intersection_gene (study_array)		
		if len(intersection_genes) >= 50:
			print "intersection gene is greater than 50"
			threshold = num_study
			up_intersection_genes = get_intersection_genes(study_array, "up_genes", intersection_genes)
			dn_intersection_genes = get_intersection_genes(study_array, "down_genes", intersection_genes)
			statsArray = [{"#Study Selected":str(num_study)}, {"#Up Genes": str(len(up_intersection_genes))}, {"#Down Genes": str(len(dn_intersection_genes))}, 
			{"#Common Genes": str(len(intersection_genes))}, {"#Union Genes": str(len(union_genes))}, {"Threshold": str(threshold) + " times occurance"}]
			dataMatrix, columnHeaderDic, rowHeader = makeMatrix(study_array, intersection_genes)
			columnHeader = []
			for eachStudy in columnHeaderDic:
				columnTitle = eachStudy["GSE"] + ',' + str(eachStudy['Index'])
				columnHeader.append(columnTitle)
			d3_json_data = getHeatmapMatrix(dataMatrix=dataMatrix, columHeader=columnHeader, rowHeader=rowHeader,  
						row_pdist='cosine', col_pdist='cosine', row_linkage='average', 
						col_linkage='average')
			new_html = render_template('layout.html', study_array_up = up_intersection_genes, 
					study_array_dn = dn_intersection_genes, statsArray = statsArray, d3_json_data = d3_json_data)

			random_id = id_generator(6)
			with open ('/Users/weiqingwangair/Documents/ALS_website/app/static/layout%s.html' %random_id, 'w+') as new_html_file:
			# with open ('/Users/weiqingwang/Documents/als_website/als_flask/app/static/layout%s.html' %random_id, 'w+') as new_html_file:
				new_html_file.write(new_html)
			return 'http://127.0.0.1:5050/static/layout%s.html' %random_id

		#if the intersection gene is fewer than 50, then find genes that appear more frequently across the studies	
		else:
			num_union_genes = len(union_genes)
			threshold = round(num_study*0.55)
			up_consensus_genes = get_consensus_genes(study_array, "up_genes", union_genes, threshold)
			dn_consensus_genes = get_consensus_genes(study_array, "down_genes", union_genes, threshold)
			
			print "not enough common genes found, initial parameters"
			print num_study, threshold, len(up_consensus_genes), len(dn_consensus_genes), num_union_genes
			whileloop_check = False
			#check to see if enought consensus genes are found
			#this algorithm is arbitrary, needs to be adjusted according to the situation
			while (len(up_consensus_genes) + len(dn_consensus_genes))/(num_union_genes*0.1) < 0.7:
				whileloop_check = True
				#if the consensus gene is too low, lower the threshold. But check first to see if the threshold is too low
				#if the threshold is too low compared to the numstudy, then do not lower the threshold.
				#this algorithm is arbitrary, needs to be adjusted to the situation
				if (threshold > 3 and num_study >= 8) or (threshold/num_study > 0.5 and threshold > 3): #makesure that the threshold is not too low
					threshold -= 1
					up_consensus_genes = get_consensus_genes(study_array, "up_genes", union_genes, threshold)
					dn_consensus_genes = get_consensus_genes(study_array, "down_genes", union_genes, threshold)
				else:
					print "couldn't find enough consensus genes"
					print num_study, threshold, len(up_consensus_genes), len(dn_consensus_genes), num_union_genes
					statsArray = [{"#Study Selected":str(num_study)}, {"#Up Genes": str(len(up_consensus_genes))}, {"#Down Genes": str(len(dn_consensus_genes))}, 
					{"#Common Genes": str(len(intersection_genes))}, {"#Union Genes": str(len(union_genes))}, {"Threshold": str(threshold) + " times occurance"}]					
					consensus_genes = list(set(up_consensus_genes+dn_consensus_genes))
					dataMatrix, columnHeaderDic, rowHeader = makeMatrix(study_array, consensus_genes)
					columnHeader = []
					for eachStudy in columnHeaderDic:
						columnTitle = eachStudy["GSE"] + ',' + str(eachStudy['Index'])
						columnHeader.append(columnTitle)
					d3_json_data = getHeatmapMatrix(dataMatrix=dataMatrix, columHeader=columnHeader, rowHeader=rowHeader,  
								row_pdist='cosine', col_pdist='cosine', row_linkage='average', col_linkage='average')
					new_html = render_template('layout.html', study_array_up = up_consensus_genes, study_array_dn = dn_consensus_genes, 
					statsArray = statsArray, d3_json_data = d3_json_data)
					random_id = id_generator(6)
					with open ('/Users/weiqingwangair/Documents/ALS_website/app/static/layout%s.html' %random_id, 'w+') as new_html_file:
					# with open ('/Users/weiqingwang/Documents/als_website/als_flask/app/static/layout%s.html' %random_id, 'w+') as new_html_file:
						new_html_file.write(new_html)
					return 'http://127.0.0.1:5050/static/layout%s.html' %random_id
			if whileloop_check: #check to see if it went through while loop or not
				print "threshold is lowered"
				print num_study, threshold, len(up_consensus_genes), len(dn_consensus_genes), num_union_genes							
			statsArray = [{"#Study Selected":str(num_study)}, {"#Up Genes": str(len(up_consensus_genes))}, {"#Down Genes": str(len(dn_consensus_genes))}, 
			{"#Common Genes": str(len(intersection_genes))}, {"#Union Genes": str(len(union_genes))}, {"Threshold": str(threshold) + " times occurance"}]
			consensus_genes = list(set(up_consensus_genes+dn_consensus_genes))
			dataMatrix, columnHeaderDic, rowHeader = makeMatrix(study_array, consensus_genes)
			columnHeader = []
			for eachStudy in columnHeaderDic:
				columnTitle = eachStudy["GSE"] + ',' + str(eachStudy['Index'])
				columnHeader.append(columnTitle)
			d3_json_data = getHeatmapMatrix(dataMatrix=dataMatrix, columHeader=columnHeader, rowHeader=rowHeader,  
						row_pdist='cosine', col_pdist='cosine', row_linkage='average', 
						col_linkage='average')
			new_html = render_template('layout.html', study_array_up = up_consensus_genes, study_array_dn = dn_consensus_genes, 
			statsArray = statsArray, d3_json_data=d3_json_data)
			random_id = id_generator(6)
			with open ('/Users/weiqingwangair/Documents/ALS_website/app/static/layout%s.html' %random_id, 'w+') as new_html_file:
			# with open ('/Users/weiqingwang/Documents/als_website/als_flask/app/static/layout%s.html' %random_id, 'w+') as new_html_file:		
				new_html_file.write(new_html)
			return 'http://127.0.0.1:5050/static/layout%s.html' %random_id					

# dir(new_html)
# inspect()

 
if __name__ == '__main__':
  app.run(debug=True, port=5050)