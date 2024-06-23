from pymongo import MongoClient
import subprocess
import requests
import json
from bs4 import BeautifulSoup
import datetime
import re
import threading

def ping_host_v4(host, collection_info, current_date_format, provider_name):
    rtt = []
    for _ in range(40):
        try:
            command = f"ping -4 -c 5 -W 0.6 {host}"  # Send 1 packet for each ping
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = process.communicate()

            print(output)

            # Extract IP address from the ping response
            ip_match = re.search(r"\((\d+\.\d+\.\d+\.\d+)\)", output.decode())
            if ip_match:
                ip_address = ip_match.group(1)
                #print(ip_address)
            else:
                print("IP address not found in the ping response.")
                ip_address = "N/A"

            # Extract RTT values from the ping response
            rtts = re.findall(r'time=([\d.]+) ms', output.decode())
            rtts = [float(rtt) for rtt in rtts]

            if not rtts:
                print("No valid RTT values found.")
                avg_rtt = "N/A"
                min_rtt = "N/A"
                max_rtt = "N/A"
                

            # Calculate average, maximum, and minimum RTT
            else:
                avg_rtt = sum(rtts) / len(rtts)
                max_rtt = max(rtts)
                min_rtt = min(rtts)

            rtt_test = [min_rtt, avg_rtt, max_rtt]
            rtt.append(rtt_test)

            print(f"URL: {host}")
            print(f"IP Address V4: {ip_address}")
            print(f"Avg RTT: {avg_rtt} seconds")
            print(f"Max RTT: {max_rtt} seconds")
            print(f"Min RTT: {min_rtt} seconds")

        except subprocess.CalledProcessError as e:
            ip_address = "N/A"
            min_rtt = "N/A"
            avg_rtt = "N/A"
            max_rtt = "N/A"
            print(f"Error running ping command for {url}: {e}")
        
    if ip_address != "N/A":
        geolocation_url = f"https://ipinfo.io/{ip_address}/json"
        response = requests.get(geolocation_url)
        print(response.status_code)
        print(geolocation_url)
        if response.status_code == 200:
            data = json.loads(response.text)
            ip = data["ip"]
            city = data.get("city", "N/A")
            country = data.get("country", "N/A")
            org = data.get("org", "N/A")

            print(f"IP Address V6: {ip}")
            print(f"City: {city}")
            print(f"Country: {country}")
            print(f"Organisation: {org}")
        else:
            print("IPv6 - Unable to retrieve geolocation data.")
            data = "N/A"
            ip = "N/A"
            city = "N/A"
            org = "N/A"
            country = "N/A"

    else:
        ip = "N/A"
        city = "N/A"
        country = "N/A"
        org = "N/A"
        
    try:
        result_tr = subprocess.check_output(['traceroute', ip_address], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        result_tr = "Error: {e}"

    parsed_data = []
    if "Error" not in result_tr:
        lines_tr = result_tr.split('\n')
        print(lines_tr)

        if lines_tr[0].startswith("traceroute"):
            lines_tr = lines_tr[1:]

    	# Extract relevant information from each line
        for line in lines_tr:
            if line:
                parts = line.split()
                hop_number = int(parts[0])
                # Check if the line contains IP address information
                if '(' in line and ')' in line:
                    ip_address = line.split('(')[-1].split(')')[0]
                else:
                    ip_address = "Unknown"

                # Extract round-trip times, filtering out '*' values
                round_trip_times = ' '.join(parts[i] for i in range(3, len(parts)) if parts[i] != '*' and parts[i - 1] != '*')
                
                round_trip_times = re.sub(r'\([^)]*\)', '', round_trip_times)
                
                round_trip_times = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '', round_trip_times)
                
                round_trip_times = re.sub(r'\bpo\d+\.\w+\.\w+\.\w+\.\w+\.net\b', '', round_trip_times)
                
                parsed_data.append({
                    'hop_number': hop_number,
                    'ip_address': ip_address,
                    'round_trip_times': round_trip_times
                })

    json_obj = {"Date" : current_date_format, "Network Service Provider" : provider_name,"URL" : host, "IPv4 Address" : ip_address, "IPv4 City" : city, "IPv4 County" : country, "IPv4 Organisation" : org, "IPv4 RTT" : rtt, "Traceroute Data IPv4" : parsed_data}
    #rows.append(json_obj)
    
    print(json_obj)

    result = collection_info.insert_one(json_obj)

    print("Rows Inserted", result.inserted_id)            
        
def main():
    # Get the current date and time
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()
    
    #one_day_before_date = current_date - datetime.timedelta(days=1)

    current_date_format = datetime.datetime(current_date.year, current_date.month, current_date.day)

    print(current_date_format)

    connection_string = "mongodb://localhost:27017/wireless"

    client = MongoClient(connection_string)

    # Access your MongoDB database
    db = client.wireless

    # Access a collection within the database
    collection_master = db.master_websites
    collection_info = db.ipv4_data

    #Read websites from DB
    #Query the collection to retrieve the URLs
    #url_cursor = collection_master.find({}, {"url": 1})  # Assuming "url" is the field containing the URLs

    # The URL of the whatismyisp.com website
    url_isp = "https://www.whatismyisp.com/"

    # Send an HTTP GET request to the website
    response_isp = requests.get(url_isp)

    # Check if the request was successful (status code 200)
    if response_isp.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response_isp.text, "html.parser")

        # Find the HTML element containing the network provider information
        provider_element = soup.find("span", {"class": "block text-4xl"})
        provider_name = ""
        if provider_element:
            # Extract and print the network provider name
            provider_name = provider_element.text.strip()
            print(f"Network Provider: {provider_name}")
            #provider_name = input("Please enter Network Provider name: ")
            #input(provider_name)
            #print(f"Network Provider: {provider_name}")
        else:
            print("Network provider information not found on the page.")
            provider_name = input("Please enter Network Provider name: ")
            #input(provider_name)
    else:
        print(f"Failed to retrieve the web page. Status code: {response_isp.status_code}")
        provider_name = input("Please enter Network Provider name: ")
        #input(provider_name)
    
    start_id = 1
    end_id = 10
    while end_id <= 131:
        # Create a list of IDs in the range
        id_range = list(range(start_id, end_id + 1))

        # Use $in operator in the query to retrieve documents with IDs in the specified range
        url_cursor = collection_master.find({"id": {"$in": id_range}}, {"url": 1})
        
        #print(url_cursor)
        url = []
        # Iterate through the cursor to access the results
        for document in url_cursor:
            url.append(document["url"])
        print(url)

        start_id = end_id + 1
        end_id = end_id + 10
        threads = [threading.Thread(target=ping_host_v4, args=(host,collection_info, current_date_format, provider_name)) for host in url]

        # Start the threads
        for thread in threads:
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

if __name__ == "__main__":
    main()


