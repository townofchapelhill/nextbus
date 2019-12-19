import urllib.request
import xml.etree.ElementTree as ET
import csv
import datetime
from datetime import timedelta
import traceback
import os

now = datetime.datetime.now()
today = datetime.date.today()

# create an xml file in the open data unpublished folder
# //CHFS/Shared Documents/OpenData/datasets/staging/
bus_file = "//CHFS/Shared Documents/OpenData/datasets/staging/nextbuscount.xml"
# throw an error if a "/logs" directory doesn't exist
log_file = open('logs/nextbuscountlog.txt', 'w')
  
# Define function to combine the XML files at each url
def combine_routes(filename):

    # Retrieve a list of the route tags from nextbus
    list_of_routes = []
    route_url = "http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=chapel-hill"
    for route in ET.fromstring(urllib.request.urlopen(route_url).read().decode('utf-8')):
        list_of_routes.append(route.attrib['tag'])
        #print(route.attrib['tag'])

    for route in range(len(list_of_routes)):
        # Assign a variable to hold the route letter
        # This is updated with a new route each loop
        x = list_of_routes[route]
        # catches any error that arises while processing the url
        try:
            # Change the last letter of the url each loop based on the x value holding the route letter
            url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=vehicleLocations&a=chapel-hill&r=' + str(x) + '&t=0'
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
    bus_data_file = "//CHFS/Shared Documents/OpenData/datasets/staging/nextbuscount.csv"
    bus_data = open(bus_data_file, 'a')
    # log_file.write('CSV file created.\n')

    # Create the csv writer object
    csvwriter = csv.writer(bus_data)
    
    # Create empty list
    item_head = []

    # use boolean to determine header in loop
    if os.stat(bus_data_file).st_size == 0:
        header = True
    else:
        header = False

    # Create loop to convert file to csv
    for vehicle in root.findall('vehicle'):
        # create header for csv file
        if header:
            item_head.append('Id')
            item_head.append('Route')
            item_head.append('Lat')
            item_head.append('Long')
            item_head.append('reportTimestamp')
            item_head.append('Predictable')
            item_head.append('Heading')
            item_head.append('Speed MPH')
           
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
        if vehicle.attrib['id'] not in id_list:
            #print(vehicle.attrib['id'])
            
            # loop through each stop and add the header info to list
            for item in root.findall('vehicle'):
                if vehicle.attrib['id'] in id_list:
                    break
                else:
                    try:
                        bus_info = []
                        vehicleid = vehicle.attrib['id']
                        bus_info.append(vehicleid)
                        id_list.append(vehicleid)
                        route = vehicle.attrib['routeTag']
                        # print(route)
                        bus_info.append(route)
                        lat = vehicle.attrib['lat']
                        bus_info.append(lat)
                        lon = vehicle.attrib['lon']
                        bus_info.append(lon)
                        #secs = vehicle.attrib['secsSinceReport']
                        report_timestamp = datetime.datetime.now() - timedelta(seconds = int(vehicle.attrib['secsSinceReport']))
                        bus_info.append(report_timestamp.strftime('%Y-%m-%d %H:%M:%S'))
                        #bus_info.append(secs)
                        predictable = vehicle.attrib['predictable']
                        bus_info.append(predictable)
                        heading = vehicle.attrib['heading']
                        bus_info.append(heading)
                        speed = float(vehicle.attrib['speedKmHr']) * 0.622 # convert to MPH
                        bus_info.append(speed)
                    
                        # append the bus_info list onto the next row in csv file
                        csvwriter.writerow(bus_info)
                    except KeyError:
                        log_file.write("KeyError on Vehicle\n")
                        print(f'KeyError {vehicle.attrib}')
                
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
        log_file.write(traceback.format_exc() + "\n")

# print error to console - missing "source folder" directory
try:  
    main()
    log_file.write(str(now))
    log_file.close()
    print('done')
except:
    log_file.write('ERROR - source folder for xml and csv files not found.\n')
    log_file.write(traceback.format_exc() + "\n")
    print('error - no src')
    log_file.close()
