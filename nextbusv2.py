try: 
	import urllib.request
	import xml.etree.ElementTree as ET
	import csv
	import datetime
	import traceback
except: 
	print(traceback.format_exc())

now = datetime.datetime.now()
today = datetime.date.today()

# create an xml file in the open data unpublished folder
bus_file = "//CHFS/Shared Documents/OpenData/datasets/staging/nextbusroutes.xml"

# throw an error if a "/logs" directory doesn't exist
try:
    log_file = open('logs/' + str(today) + '-nextbuslog.txt', 'w')
except:
    error_file = open('error.txt', 'w')
    error_file.write('ERROR - "logs" directory not found\n')
    error_file.close()
    
# Define function to combine the XML files at each url
def combine_routes(filename):

    # Create a list of the route tags
    # This can be easily edited in the future to remove or add tags
    list_of_routes = \
        ['A','CCX','CL','CM','CPX','CW','D','DEX','DM','F','FCX','FG','G','HS','HU','HX','J','JFX','JN','N','NS',
         'NU','RU','S','SRG','SRJ','SRT','T','TWkend','U','V']

    # Constrain the for loop to be within the list_of_routes created
    for route in range(len(list_of_routes)):
        # Assign a variable to hold the route letter
        # This is updated with a new route each loop
        x = list_of_routes[route]
        # catches any error that arises while processing the url
        try:
            # Change the last letter of the url each loop based on the x value holding the route letter
            url = ('http://webservices.nextbus.com/service/publicXMLFeed?command=schedule&a=chapel-hill&r='+str(x))
            # Create a list to hold each XML file
            blank_list = []
            # Read and decode the XML file found at each url
            decoded_route = urllib.request.urlopen(url).read().decode('utf-8')
            log_file.write(x + " route URL successfully accessed and decoded.\n")
        except:
            log_file.write("ERROR - URL access or decoding error\n")
        # Add each line of the XML file to the empty list
        for line in decoded_route:
            blank_list.append(line)
        # Create a new list that strips the decoded_route data of repeating doctypes and body tags
        # Slice the list to remove the repeating phrases: this should be the same for every nextbus route xml url
        stripped_route_list = decoded_route[105:-8]
        # Write the XML file of each URL to one file: this filename will be passed into combine_routes via main()
        filename.write(stripped_route_list)
        # Print success statement for each route loaded
        # This is done because the process to complete all files is long, and it allows the user to know something is happening
        log_file.write("The " + str(x)+"-"+"Route XML data has been appended to nextbusroutes.xml file.")
        log_file.write('\n\n')
            

# Create function to pass a write file to combine_routes
def pass_file():
    # Create the variable to hold the desired write file
    routes = open(bus_file, "w")
    # Create variables to hold the phrases we want to add to the beginning and end of new XML file
    doc_type = '<?xml version="1.0" encoding="utf-8" ?>\n'
    body_tag = '<body copyright = "All data copyright Chapel Hill Transit 2017.">\n'
    body = '</body>\n'
    # Write the necessary statements to beginning of XML doc
    routes.write(doc_type)
    routes.write(body_tag)
    # Call combine_routes to fill the body of the new XML doc
    combine_routes(routes)
    # Write the end statements desired and close the file
    routes.write(body)
    routes.close()


# Define function to convert the XML files to CSV
# Written by Steven
def convert_to_csv():
    # Parse the XML file createdin pass_file and combine_routes
    tree = ET.parse(bus_file)
    root = tree.getroot()

    # Create a CSV file in the open data unpublished folder for writing
    bus_data = open("//CHFS/Shared Documents/OpenData/datasets/staging/nextbusroutes.csv", 'w')
    log_file.write('CSV file created.\n')

    # Create the csv writer object
    csvwriter = csv.writer(bus_data)
    
    # Create empty list
    item_head = []

    # use boolean to determine header in loop
    header = True

    # Create loop to convert file to csv
    for route in root.findall('route'):
        # create header for csv file
        if header:
            item_head.append('Bus')
            item_head.append('Title')
            item_head.append('Schedule Class')
            item_head.append('Days')
            item_head.append('Direction')
            item_head.append('blockID')
            item_head.append('Stop Name')
            item_head.append('Stop Times')
            for i in range(30):
                item_head.append(' ')
            # Write back to csvwriter
            csvwriter.writerow(item_head)
            header = False
            try:
                log_file.write("CSV header created, adding XML data to CSV file now...\n")
            except:
                print('ERROR - missing "logs" directory\n')        

        # save a list of id's to know if they are already added in
        id_list = []
        # loop through each <tr> in the routes
        for tr in route.findall('tr'):
            if tr.attrib['blockID'] not in id_list:
                # loop through each stop and add the header info to list
                for stop in tr.findall('stop'):
                    bus_info = []
                    bus = route.attrib['tag']
                    bus_info.append(bus)
                    title = route.attrib['title']
                    bus_info.append(title)
                    schedule = route.attrib['scheduleClass']
                    bus_info.append(schedule)
                    days = route.attrib['serviceClass']
                    bus_info.append(days)
                    direction = route.attrib['direction']
                    bus_info.append(direction)
                    blockID = tr.attrib['blockID']
                    bus_info.append(blockID)
                    id_list.append(blockID)
                    stop_n = stop.attrib['tag']
                    bus_info.append(stop_n)
                    
                    # loop allows for stop times to be in the correct order and row
                    for second_tr in route.findall('tr'):
                        if second_tr.attrib['blockID'] == tr.attrib['blockID']:
                            for second_stop in second_tr.findall('stop'):
                                if second_stop.attrib['tag'] == stop.attrib['tag']:
                                    bus_info.append(second_stop.text)
                    
                    # add '--' for every blank space in csv
                    for i in range(30):
                        bus_info.append('--')
                        
                    # append the bus_info list onto the next row in csv file
                    csvwriter.writerow(bus_info)
                
    # Close file once written to
    bus_data.close()


# Main function
def main():
    # Call the pass file function
    pass_file()
    # catch any errors in the conversion process
    try:
        # Call the conversion function
        convert_to_csv()
        # Print success statement
        log_file.write("All routes from XML successfully written to a CSV file - nextbusroutes.csv\n\n")
    except:
        log_file.write("ERROR - there was an error in the conversion process of the xml file.\n")

# print error to console - missing "source folder" directory
try:  
    main()
    log_file.write(str(now))
    log_file.close()
    print('done')
except:
    log_file.write('ERROR - source folder for xml and csv files not found.\n')
    print('error - no src')
    log_file.close()