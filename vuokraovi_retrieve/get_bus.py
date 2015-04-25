import requests, csv, yaml, json

csv_path = '/Users/young/datahackathon/vuokraovi_retrieve/data_bus_stop.csv'
new_path = '/Users/young/datahackathon/vuokraovi_retrieve/data_bus_stop_full.csv'
DIAMETER = 500    # The unit is Meter
total = 0
no_bus_stop = 0
MOCK_UP = [{'code':'0', 'dist':'0'}]
total_rows = []
'''
!!!ATTENTION!!!
HSL system doesn't wgs84 coordinate system by default but can interpret it.
Their default is espg.
Add "epsg_in=wgs84&epsg_out=wgs84" to your query.
example request
http://api.reittiopas.fi/hsl/prod/?request=stops_area&center_coordinate=24.815548,60.187078&diameter=500&epsg_in=wgs84&epsg_out=wgs84&user=chendurkumar&pass=manimangai

Result:
lines: [
"1075 1:Puistolan asema",
"1075A 2:Siltamäki",
"1076B 2:Puistola"
],
There are four buses at the stop.
Save only the first number before the whitespace

http://api.reittiopas.fi/hsl/prod/?request=stops_area&center_coordinate=24.945793,60.1907603&diameter=500&epsg_in=wgs84&epsg_out=wgs84&user=chendurkumar&pass=manimangai
'''

def get_csv(name):
	with open(name) as f:
		d = [i for i in csv.reader(f)]
	return d


def write_to_text(url, e):
	with open('output2.txt', 'a') as f:
		f.write(url)
		f.write("\n(%d) Agency name missing: %s\n" % (agency_missing, e))

def unicode_to_str(response):
	dump = json.dumps(response.json())
	return yaml.safe_load(dump)


def get_bus_stop(lng, lat):
	'''
	Search in the radius of 500 meters.
	'''
	global no_bus_stop
	#print "lng: %s, lat: %s" % (lng, lat)

	api_prefix = 'http://api.reittiopas.fi/hsl/prod/?request=stops_area&center_coordinate='
	coord = lng + ',' + lat
	api_suffix = '&diameter=' + str(DIAMETER) + '&epsg_in=wgs84&epsg_out=wgs84&user=chendurkumar&pass=manimangai'
	api = api_prefix + coord + api_suffix
	r = requests.get(api)
	try:
		r.json()
	except ValueError as e:
		no_bus_stop += 1
		print "(%d) There is no bus stop with in %d meters of diameter at %s, %s" % (no_bus_stop, DIAMETER, lng, lat)
		return MOCK_UP
	else:
		bus_stops = unicode_to_str(r)
		return bus_stops

def scrape(row, path):
	
	lng = row[6]
	lat = row[5]
	id = row[0]
	bus_stops = get_bus_stop(lng, lat)
	
	## Duplicate the row as many as the number of bus stops
	new = [row[:] for __ in range(len(bus_stops))]
	
	for index, stop in enumerate(bus_stops):
		new[index][-2] = stop['code']
		new[index][-1] = stop['dist']
	return new


def write_csv(data, path):
	with open(path, 'w') as f:
		writer = csv.writer(f)
		writer.writerows(data)
	print "!!!DONE!!!"


def take_csv(file):
	global total, rows
	
	for i in range(len(file)):
		row = file[i]
		if row[-1] == "None":    # dist
			print "go scraping"
			row = scrape(row, new_path)
		else:
			row = [row]
		for i in row:
			total_rows.append(i)
		
		total += 1
		if total % 10 == 0:
			print "(%d) Done." % total
	
	write_csv(total_rows, new_path)


with open(csv_path) as f:
	d = [i for i in csv.reader(f)]
	take_csv(d)



















