import requests, re, numpy, json
from matplotlib import pyplot

########################################
# Define vehicle search parameters, check AutoTrader URL in browser to find make and model tags
make="TOYOTA"
model="4RUN"
minyear="2010"
maxyear="2020"
minmiles="0"
maxmiles="200000"
zip="46208"
distance="300"
filters=""
########################################

# Various lists needed for accumulating and calculating values
year_db = []
miles_db = []
price_db = []
curve_x = []
curve_y = []

# Tell web server we're a Chrome browser
request_headers = { 'User-Agent': 'Chrome/87.0.4280.141' }

# Defaults needed for iterating through listings
num_results=1200
current_offset=0

# Main loop. AutoTrader only allows pulling 100 results at a time, need to iterate through pages. 
# AutoTrader only seems to allow retrieval of the first 1100 listings, best to tune search criteria to fit within that limit.
while (current_offset < num_results):
	response = requests.get("https://www.autotrader.com/rest/searchresults/base?zip=" + zip + "&makeCodeList=" + make + "&modelCodeList=" + model + "&listingTypes=USED&isNewSearch=true&startYear=" + minyear + "&endYear=" + maxyear + "&searchRadius=" + distance + "&minMileage=" + minmiles + "&maxMileage=" + maxmiles + "&numRecords=100&firstRecord=" + str(current_offset) + filters , headers = request_headers )
	current_offset=current_offset+100
	page = json.loads(response.text)
	num_results = page.get('totalResultCount')
	cars = page.get('listings')

	# For each vehicle listing, extract Year, Milage, and Price
	for car in cars:
		# Sometimes sellers don't format fields correctly. If we can't parse data for a partular vehicle, just throw it out.
		try:
			year=int(car.get('year'))
			miles=int(re.sub(r',', '', car.get('specifications').get('mileage').get('value')))
			price=int(car.get('pricingDetail').get('primary'))
			year_db.append(year)
			miles_db.append(miles)
			price_db.append(price)
		except:
			pass


# Define graph boundaries
# Snap miles axis to 50k intervals
x_min=min(miles_db) - (min(miles_db) % 50000)
x_max=max(miles_db) - (max(miles_db) % 50000) + 50000

# Snap price axis to $5k intervals
y_min=min(price_db) - (min(price_db) % 5000)
y_max=max(price_db) - (max(price_db) % 5000) + 5000

# Perform curve fit on collected data
curve = numpy.polynomial.polynomial.polyfit(miles_db, price_db, 2)

# Using curve coefficients, calculate list of data points
for i in range(int(x_max/1000)):
	curve_x.append(i*1000)
	curve_y.append(curve[0]+i*1000*curve[1]+i*1000*i*1000*curve[2])

# Setup PyPlot
pyplot.axis([x_min, x_max, y_min, y_max])
pyplot.xlabel("Miles")
pyplot.ylabel("Price")
pyplot.title(minyear + "-" + maxyear + " " + make + " " + model + " " + "Market Value\nCalculated from " + str(len(year_db)) + " search results\nValue = " + str(int(curve[0])) + " + m*" + str(round(curve[1], 3)) + " + (m^2)*" + str(round(curve[2], 8)) + " (where m=miles)")

# Scatter plot search results
pyplot.plot(miles_db, price_db, 'ro')

# Plot avg price curve	
pyplot.plot(curve_x, curve_y, 'b-')	

# Display the plot
pyplot.show()