import networkx as nx
import matplotlib.pyplot as plt
import community as cm

def init_doc():
    result = {'author_list': [],
              'publication_year': 0,
              'reference_list': [],
              'doi': '',
              'title': '',
              'keyword_list': []}
    return result

def split_field(line_string):
    field_string = ""
    value_string = ""
    index = 0
    while index < len(line_string):
        if index < 2:
            field_string += line_string[index]
        elif index > 2:
            value_string += line_string[index]
        index += 1
    return field_string, value_string

def load_doc_list(file_name):
    doc_list = []
    file_handle = open(file_name, 'r')
    if not file_handle:
        exit('load_doc_list')
    file_string = file_handle.read()
    file_lines = file_string.split('\n') #NOTE: windows: retirar '\r'
    keyword_string = ""
    line_index = 0
    doc = init_doc()
    for line_index in range(len(file_lines)):
        line_string = file_lines[line_index]
        line_field, line_value = split_field(line_string)
        if line_field == "  ":
            line_field = last_field
        if line_field == "FN" or line_field == "VR" or line_field == "":
            pass
        elif line_field == "PT":
            del doc
            doc = init_doc()
        elif line_field == "ER":
            keyword_list = keyword_string.split(";")
            for keyword in keyword_list:
                if len(keyword) > 1 and keyword[0] == " ":
                    keyword = keyword[:0] + keyword[1:]
                if keyword != "":
                    doc['keyword_list'].append(keyword)
            keyword_string = ""
            doc_list.append(doc)
        elif line_field == "CR":
	    temp_line_field = line_field
	    label = line_value
	    if ',' in  label and len(label.split(',')) > 1:
		 label = label.split(',')[0] + label.split(',')[1]
	    elif ' ' in  label and len(label.split(' ')) > 1:
		 label = label.split(' ')[0] + label.split(' ')[1]
	    elif len(label.split(','))==1:
		 label = label
	    else:
		label = temp_line_field
	    line_value = label
            doc['reference_list'].append(line_value)
        elif line_field == "UT":
            doc['doi'] = line_value
        elif line_field == "PY":
            doc['publication_year'] = int(line_value)
        elif line_field == "ID":
            keyword_string += (" " + line_value)
        elif line_field == "AU":
            doc['author_list'].append(line_value)
	elif line_field == "TI":
	    if len(doc['title']) == 0:
		doc['title'] = line_value
	    else:
		doc['title'] += ' ' + line_value
        else:
            pass
        last_field = line_field
    return doc_list

def gen_slices(slice_len, year_from, year_to, whole_period = False):
    result = []
    year = year_from
    while year <= year_to:
	slice_from = year
	slice_to = year + slice_len - 1
	if slice_to > year_to:
	    slice_to = year_to
	time_slice = (slice_from, slice_to)
	result.append(time_slice)
	year = slice_to + 1
    if whole_period:
	result.append((year_from, year_to))
    return result

def make_network(doc_list, tag, exclusion_list = [],
		 min_node_weight = 0, min_edge_weight = 0,
		 filter_giant_component = True):
    node_dict = {}
    edge_dict = {}
    node_label_table = {}

    if tag == 'cc':
	correlation_type = 'reference_list'
    elif tag == 'kw':
	correlation_type = 'keyword_list'
    else:
	exit('E: make_network')

    for doc in doc_list:
	doc_node_list = doc[correlation_type]
	for label in doc_node_list:
	    try:
		node_index = node_label_table[label]
		node_dict[node_index]['count'] += 1
	    except KeyError:
		node_index = len(node_dict)
		node_label_table[label] = node_index
		node_dict[node_index] = {}
		node_dict[node_index]['label'] = label
		node_dict[node_index]['count'] = 1
		node_dict[node_index]['color'] = '#000000'

    for doc in doc_list:
	doc_node_list = doc[correlation_type]

	for i in xrange(len(doc_node_list)):
    	    label_i = doc_node_list[i]
	    for j in xrange(i + 1, len(doc_node_list)):
		label_j = doc_node_list[j]
		index_i = node_label_table[label_i]
		index_j = node_label_table[label_j]
		indices = (min(index_i, index_j), max(index_i, index_j))
		try:
		    edge_dict[indices]['count'] += 1
		except KeyError:
		    edge_dict[indices] = {}
		    edge_dict[indices]['count'] = 1

    G = nx.Graph()

    for node in node_dict:
	if node_dict[node]['count'] > min_node_weight:
	    G.add_node(node, weight=node_dict[node]['count'])
    for edge in edge_dict:
	if edge_dict[edge]['count'] > min_edge_weight:
	    G.add_edge(edge[0], edge[1], weight=edge_dict[edge]['count'])

    print 'rawG: %d nodes, %d edges' % (len(G.nodes()), len(G.edges()))

    if filter_giant_component == True:
	H = max(nx.connected_component_subgraphs(G), key=len)
    else:
	H = G

    network_attr = {}
    network_attr['node_bc'] = nx.betweenness_centrality(H, normalized = True)
    network_attr['node_size'] = []
    network_attr['node_color'] = []
    network_attr['node_label'] = {}
    network_attr['node_partition'] = cm.best_partition(H)
    network_attr['edge_width'] = []
    network_attr['label_bc'] = []
    network_attr['graph'] = H
    network_attr['node_pos'] = nx.spring_layout(H)

    min_edge_weight = min([edge_dict[edge]['count'] for edge in edge_dict])
    max_edge_weight = max([edge_dict[edge]['count'] for edge in edge_dict])

    edge_width_list = []
    for edge in H.edges():
	w = float(H[edge[0]][edge[1]]['weight'])
	edge_width = map_to(min_edge_weight, max_edge_weight, 0.1, 0.5, w)
	edge_width_list.append(edge_width)
    network_attr['edge_width'] = edge_width_list

    min_node_bc = min([bc for bc in network_attr['node_bc'].values()])
    max_node_bc = max([bc for bc in network_attr['node_bc'].values()])

    for node in network_attr['node_bc']:
	old_bc = network_attr['node_bc'][node]
	new_bc = map_to(min_node_bc, max_node_bc, 0.0, 100.0, old_bc)
	if new_bc >= 0.0:
	    network_attr['node_label'][node] = node_dict[node]['label']
	else:
	    network_attr['node_label'][node] = ''

	node_size = new_bc + 30.0
	network_attr['node_size'].append(node_size)
	node_partition = network_attr['node_partition'][node]
	network_attr['node_color'].append(find_partition_color(node_partition))

    print 'filG: %d nodes, %d edges' % (len(H.nodes()), len(H.edges()))

    label_bc_list = []
    for node in network_attr['node_bc']:
	entry = (node_dict[node]['label'], network_attr['node_bc'][node])
	label_bc_list.append(entry)
    label_bc_list = sorted(label_bc_list, key=lambda tup: -tup[1])
    network_attr['label_bc'] = label_bc_list

    return network_attr

def draw_network(network_attr, draw_labels = False, show_plot = True, save_path = ''):

    nx.draw_networkx_nodes(G = network_attr['graph'],
			   pos = network_attr['node_pos'],
			   node_color = network_attr['node_color'],
			   node_size = network_attr['node_size'])

    nx.draw_networkx_edges(G = network_attr['graph'],
			   pos = network_attr['node_pos'],
			   edge_color = '#101010',
			   width = network_attr['edge_width'])

    if draw_labels == True:
	nx.draw_networkx_labels(G = network_attr['graph'],
				pos = network_attr['node_pos'],
				labels = network_attr['node_label'],
				font_color = '#000000',
				font_size = 9)
    if show_plot:
	plt.show()

    if save_path:
	pass
	#plt.savefig(save_path)


def map_to(x0, x1, y0, y1, x): #NOTE: x -> (x0,x1) => y -> (y0,y1)
    y = 0.0
    try:
	y = y0 + (x - x0)*(y1-y0)/(x1-x0)
    except:
	y = 0.0
	print x0, x1, y0, y1, x
	print 'E: map_to'
    return y

def find_label(index, nodes):
    for label in nodes:
	if nodes[label]['index'] == index:
	    return label
    return 'NOT FOUND'

def find_partition_color(partition):
    colors = ['#EE0000', '#00EE00', '#0000EE', '#EEEE00',
	      '#00EEEE', '#EE00EE', '#880000', '#008800',
	      '#000088', '#880088', '#888800', '#008888',
	      '#440000', '#004400', '#000044', '#440044',
	      '#444400', '#004444', '#220000', '#002200',
	      '#000022', '#220022', '#222200', '#002222']
    try:
	return colors[partition]
    except:
	return '#000000'

def count_occurance_in_doc_list(doc_list, tag, label):
    result = 0
    for doc in doc_list:
	if tag == 'cc':
	    list_type = 'reference_list'
	elif tag == 'kw':
	    list_type = 'keyword_list'
	else:
	    exit('E: count_occ_in_doc_list')
	if label in doc[list_type]:
	    result += 1
    return result

def filter_doc(doc_list, min_year = -1, max_year = -1, top_number = -1):
    result = []

    if min_year == -1:
	min_year = min(doc_list, key = lambda year : int(year['publication_year']))['publication_year']
    if max_year == -1:
	max_year = max(doc_list, key = lambda year : int(year['publication_year']))['publication_year']
    if top_number == -1:
	top_number = len(doc_list)

    for index in xrange(len(doc_list)):
	doc = doc_list[index]
	if doc['publication_year'] >= min_year and doc['publication_year'] <= max_year:
	    result.append(doc)
	if len(result) == top_number:
	    break

    return result

def main():
    #file_folder = '/home/alberto/Code/WoS/'
    #input_file = 'input/physics.txt'
    #input_file = 'input/xray.txt'
    input_file = 'se_2014.txt'

    input_file_path = input_file#file_folder + input_file
    min_node_weight = 0
    min_edge_weight = 1
    tag = 'cc' #NOTE: cc-> co-citation; kw -> keyword
    doc_list = load_doc_list(input_file_path)

    print '\n---------'
    print 'input:', input_file_path
    print 'tag:', tag
    print 'docs:', len(doc_list)
    print 'min_edge_weight:', min_edge_weight
    print 'min_node_weight:', min_node_weight
    print '---------\n'

    docs_per_slice = 70
    slice_len = 3
    year_from = 1992
    year_to = 2014
    time_slices = gen_slices(slice_len = slice_len,
			     year_from = year_from,
			     year_to = year_to,
			     whole_period = False)

    for slice in time_slices:
	min_year = slice[0]
	max_year = slice[1]

	slice_doc_list = filter_doc(doc_list,
				    min_year,
				    max_year,
				    top_number = docs_per_slice)

	network = make_network(doc_list = slice_doc_list,
		    	       tag = tag,
			       min_node_weight = min_node_weight,
			       min_edge_weight = min_edge_weight,
			       filter_giant_component = True)

	bc_list = network['label_bc']
	for n in xrange(16):
	    try:
		print bc_list[n]
	    except:
		pass

	print 'slice: (%d, %d), %d docs\n' % (min_year, max_year,
				              len(slice_doc_list))
	draw_network(network, draw_labels = False, show_plot = True)
	draw_network(network, draw_labels = True, show_plot = True)


#   O periodo em estudo e dividido em fatias.
#
#   De cada fatia e feita uma rede, onde se observa quais
#   sao os principais nos mediadores (PNMs).
#
#   Esses PNMs sao adicionados a uma lista global.
#
#   Sao feitas fatias de tres anos que se interpolam (ou nao)
#   de onde sao retirados os graus de mediacao de cada PNM
#   da lista global.
#
#   Tambem sao contadas as ocorrencias de cada PNM ao longo
#   dos anos.
#
#   E feito um grafico do numero de ocorrencias e grau de
#   intermediacao ao longo dos anos.
#
#   PS: Talvez, em vez do ano para o qual sera calculado o GI de
#   um no ser o ano central da fatia, ele pode ser o ultimo.

main()
