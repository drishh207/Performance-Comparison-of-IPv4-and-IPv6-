# Performance-Comparison-of-IPv4-and-IPv6-

**Aim**: In this study, we are comparing the performance of IPv4 and IPv6 for around 100 websites, by sending regular ping commands to the respective IP addresses for a week from different ISPs (Jio, Airtel, VI) and then analysing the data to get insights

## Procedure:

### Phase I - Data Collection: 
1. Top 100 working websites were chosen - Highest Rated Websites by Alexa + Indian Government websites.
2. An automated script was created using multi-threading to capture the following details for each website, each day, for both IPv4 and IPv6:
   - Get the ISP name using [whatismyisp.com](https://whatismyisp.com)
   - Ping each website 40 times with a packet size of 10 and collect the RTTs for each ping.
   - Collect the geolocation of the IP address using [ipinfo.io](https://ipinfo.io)
   - Send a traceroute request to the IP address and collect the data.
   - Use multithreading to send ping requests to 10 websites simultaneously to reduce collection time.
   - Data is stored in Mongo DB in json format.
     
### Phase II - Data Preprocessing:
1. **Initial Data Processing**
   - All CSV files were merged together for both IPv4 and IPv6.
   - Empty values were replaced by `NaN`.
   - The date column was formatted to `YYYY-MM-DD`.

2. **Data Cleaning**
   - Websites that were common in both IPv4 and IPv6 for all days and all ISPs were identified.
   - Websites whose ping didn’t work even once were removed from both files.
     
3. **Selecting Top 100 Optimal Websites**
   - i. **Calculate Average MAX RTTs**: 
     - For each website, the average of the maximum Round-Trip Times (RTTs) was calculated for both IPv4 and IPv6 combined.
   - ii. **Create Scatter Plot**: 
     - A scatter plot was created to identify outliers in the data.
   - iii. **Choose Optimal Websites**: 
     - Websites within the optimal range on the scatter plot were selected.

### Phase III - Data Analysis:

#### 1. Latency Comparison

- **Overall Comparison**: There is no clear distinction between the latencies of IPv4 and IPv6.
  
- **By ISP**:
  - **Airtel**: IPv6 generally has more or similar latency compared to IPv4.
  - **VI**: IPv6 shows slightly higher or similar latency compared to IPv4.
  - **Jio (5G)**: IPv6 has higher latency compared to IPv4.

- **Variance Distribution**:
  - The scatter plots indicate that the variance distribution of IPv4 and IPv6 latencies is nearly identical.
  - Observing the plot from 0 to 200 ms, IPv6 shows slightly more variability than IPv4.

- **Correlation**:
  - The scatter plots suggest that IPv4 and IPv6 latencies are negatively correlated.

**Inference**: In terms of latency, IPv6 is slightly less or almost as efficient as IPv4.

#### 2. Number of Hops

- **Traceroute Success**: 
  - IPv4 shows more successful traceroute completions compared to IPv6 across all ISPs.
  - For unsuccessful traceroutes, both IPv4 and IPv6 perform similarly.

- **Hop Counts**:
  - IPv6 generally has more or at least as many hops as IPv4.

**Inference**: The slightly higher latency observed in IPv6 is attributed to its higher hop counts compared to IPv4. Additionally, IPv4 is slightly more reliable in terms of receiving responses from the server.


#### 3. Geolocation

- **Geolocation Accuracy**:
  - IPv6 has significantly lower geolocation accuracy compared to IPv4.

- **Hop Counts by Location**:
  - **Singapore** has the highest average number of hops.

- **Reliability**:
  - Across almost all countries, IPv4 is more reliable than IPv6.

**Inference**: IPv6 exhibits lower geolocation accuracy than IPv4. Singapore stands out with the highest average hop counts, and generally, IPv4 is more reliable than IPv6 in terms of geolocation-based measurements.

### Conclusion:
We conclude our analysis by stating that IPv6 has almost the same or slightly more latency than IPv4. IPv6 is slightly less reliable than IPv4 in terms of getting a response from the server and for various geolocations. Since IPv6 is still in the building phase, we can say that it is also a good option to use IPv6. 

For plots and more details, find the ppt and report in the repository





