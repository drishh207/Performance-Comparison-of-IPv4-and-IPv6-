import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the CSV files into pandas dataframes
file1 = pd.read_csv('merged_file_ipv4.csv')
print(len(file1))
file2 = pd.read_csv('merged_file_ipv6.csv')
print(len(file2))
f1 = file1
f2 = file2

# Convert the date columns to datetime objects
file1['Date'] = pd.to_datetime(file1['Date'], format='%Y-%m-%dT%H:%M:%S.%fZ')
file2['Date'] = pd.to_datetime(file2['Date'], format='%Y-%m-%dT%H:%M:%S.%fZ')

# Extract unique websites from each file
unique_websites_file1 = set(file1['URL'])
unique_websites_file2 = set(file2['URL'])

# Find common websites for each day
common_websites_by_day = {}

# Iterate through each day in file1
for day in file1['Date'].dt.strftime('%Y%m%d').unique():
    # Get unique websites for the current day in each file
    websites_file1 = set(file1[file1['Date'].dt.strftime('%Y%m%d') == day]['URL'])
    websites_file2 = set(file2[file2['Date'].dt.strftime('%Y%m%d') == day]['URL'])
    
    # Find common websites for the current day
    common_websites = websites_file1.intersection(websites_file2)
    
    # Store the result in the dictionary
    common_websites_by_day[day] = common_websites

# Print or use the results as needed
print("Common websites by day:")
for day, websites in common_websites_by_day.items():
    print(f"Day {day}: {len(websites)}")
    
# Combine both files into one DataFrame based on common columns
merged_df = pd.concat([file1, file2], ignore_index=True)

merged_df.drop(2348, inplace=True)

# Filter rows for the specified date
merged_df = merged_df[(merged_df['Date'] == '20231115') & (merged_df['Network Service Provider'] == 'Reliance Jio Infocomm Limited')]

#print(merged_df)

# Filter columns of type IPv4.*.0 and convert nan values to 0
rtt_columns = [col for col in merged_df.columns if 'IPv4 RTT' in col and '.1' in col]
merged_df[rtt_columns] = merged_df[rtt_columns].replace({np.nan: 0})

# Calculate average RTT for each website
merged_df['AverageRTT'] = merged_df[rtt_columns].mean(axis=1)

# Filter rows for the specified websites
filtered_df = merged_df[merged_df['URL'].isin(websites)]

# Display the resulting DataFrame
print(filtered_df.shape)
#print(filtered_df.shape)

#Remove all those have AverageRTT = 0
filtered_df = filtered_df[filtered_df['AverageRTT'] != 0]
print(filtered_df.shape)


# Plot scatter plot
plt.figure(figsize=(50, 15))
plt.scatter(filtered_df['URL'],filtered_df['AverageRTT'], c='blue', alpha=0.5)  
plt.title('Scatter Plot of RTT for Websites')
plt.xlabel('Average RTT')
plt.ylabel('URLs')  # Replace with an actual label for the y-axis
plt.grid(True)
plt.show()

# Find optimal 100 websites based on Average RTT
optimal_websites = filtered_df.nlargest(100, 'AverageRTT')['URL']

# Display the list of optimal 100 websites
print("Optimal 100 Websites based on Average RTT:")
print(optimal_websites.shape)

#filtered_file1 = file1[file1['URL'].isin(optimal_websites)]
filtered_file1 = pd.read_csv('top_100_ipv4.csv')

# Filter rows for the specified websites from file2
#filtered_file2 = file2[file2['URL'].isin(optimal_websites)]
filtered_file2 = pd.read_csv('top_100_ipv6.csv')
filter_file1 = filtered_file1
filter_file2 = filtered_file2

# Save the filtered DataFrames to new CSV files
#filtered_file1.to_csv('top_100_ipv4.csv', index=False)
#filtered_file2.to_csv('top_100_ipv6.csv', index=False)

#Traceroute Hop Success

# Filter rows where the URL is NaN
#nan_url_counts = opt_df[opt_df['IPv4 Address'].isna()].groupby(['Network Service Provider', 'Date']).size().reset_index(name='Count')
url_counts_ipv4 = filtered_file1.groupby(['Date', 'Network Service Provider'])['IPv4 Address'].agg(nan_count=lambda x: x.isna().sum(), not_nan_count=lambda x: x.notna().sum()).reset_index()

url_counts_ipv6 = filtered_file2.groupby(['Date', 'Network Service Provider'])['IPv6 Address'].agg(nan_count=lambda x: x.isna().sum(), not_nan_count=lambda x: x.notna().sum()).reset_index()


# Print or use the resulting counts
#print(url_counts_ipv4)
#print(url_counts_ipv6)


fig, ax = plt.subplots(figsize=(12, 6))

# Plot bar for IPv4 NaN counts
ax.bar(url_counts_ipv4.index - 0.2, url_counts_ipv4['nan_count'], width=0.4, label='IPv4 Traceroute Success', color='blue')

# Plot bar for IPv4 non-NaN counts
ax.bar(url_counts_ipv4.index + 0.2, url_counts_ipv4['not_nan_count'], width=0.4, label='IPv4 Traceroute NoSuccess', color='red')

# Plot bar for IPv6 NaN counts
ax.bar(url_counts_ipv6.index - 0.2, url_counts_ipv6['nan_count'], width=0.4, label='IPv6 Traceroute Success', alpha=0.5, color='green')

# Plot bar for IPv6 non-NaN counts
ax.bar(url_counts_ipv6.index + 0.2, url_counts_ipv6['not_nan_count'], width=0.4, label='IPv6 Traceroute NoSuccess', alpha=0.5, color='purple')

ax.set_xticks(url_counts_ipv4.index)
ax.set_xticklabels([f"{date}\n{isp}" for date, isp in zip(url_counts_ipv4['Date'], url_counts_ipv4['Network Service Provider'])], rotation=45, ha='right')
ax.set_xlabel('Date and ISP')
ax.set_ylabel('Traceroute Hop Counts')
ax.legend()
plt.title('Comparison of Traceroute Hop Counts for IPv4 and IPv6')
plt.tight_layout()
plt.show()


#Traceroute Number of Hops
# Define the columns related to IPv6 hops
ipv4_hop_columns = [col for col in filtered_file1.columns if 'hop_number' in col]
ipv6_hop_columns = [col for col in filtered_file2.columns if 'hop_number' in col]

# Define the columns related to IPv4 hops and IPv4 Address
filtered_df1 = filtered_file1[filtered_file1['IPv4 Address'].notna()]
filtered_df2 = filtered_file2[filtered_file2['IPv6 Address'].notna()]
print(filtered_df1)

# Count the number of non-NaN values for each website, day, and network service provider

#non_nan_counts_4 = filtered_df1[ipv4_hop_columns].notna().sum(axis=1).reset_index(name='Total_Non_NaN_Count')
non_nan_counts_4 = filtered_df1.apply(lambda row: np.sum(~pd.isna(row[ipv4_hop_columns])), axis=1)
filtered_df1['Hop Count'] = non_nan_counts_4
#non_nan_counts_4 = filtered_df[ipv4_hop_columns].notna().sum(axis=1).reset_index(name='Total_Non_NaN_Count')

#non_nan_counts_6 = filtered_df2[ipv6_hop_columns].notna().sum(axis=1).reset_index(name='Total_Non_NaN_Count')
non_nan_counts_6 = filtered_df2.apply(lambda row: np.sum(~pd.isna(row[ipv6_hop_columns])), axis=1)
filtered_df2['Hop Count'] = non_nan_counts_6

#print(filtered_df1)
#print(filtered_df2)

average_counts_4 = filtered_df1.groupby(['Date'])['Hop Count'].mean().reset_index()
average_counts_6 = filtered_df2.groupby(['Date'])['Hop Count'].mean().reset_index()

# Display the resulting DataFrame with average counts
print(average_counts_4)
print(average_counts_6)


fig, ax = plt.subplots(figsize=(12, 6))

# Plot bar for IPv4 NaN counts
ax.bar(average_counts_4.index - 0.2, average_counts_4['Hop Count'], width=0.4, label='IPv4 Avg Hop Count', color='blue')

# Plot bar for IPv4 non-NaN counts
ax.bar(average_counts_6.index + 0.2, average_counts_6['Hop Count'], width=0.4, label='IPv6 Avg Hop Count', color='red')

ax.set_xticks(average_counts_4.index)
ax.set_xticklabels([f"{date}" for date in average_counts_4['Date']], rotation=45, ha='right')
ax.set_xlabel('Date')
ax.set_ylabel('Hop Counts')
ax.legend()
plt.title('Comparison of Hop Counts for IPv4 and IPv6')
plt.tight_layout()
plt.show()

# Calculate average of all values in non_nan_counts_4 and non_nan_counts_6
avg_count_4 = non_nan_counts_4.mean()
avg_count_6 = non_nan_counts_6.mean()

print(f'Average of non_nan_counts_4: {avg_count_4}')
print(f'Average of non_nan_counts_6: {avg_count_6}')


#Latency
# IPv4
columns_to_average = filtered_file1.filter(regex='IPv4 RTT\..*\.1', axis=1)

# Calculate the average for each row (skip NaN values)
average_values = columns_to_average.mean(axis=1, skipna=True)

# Add the average values to the original DataFrame
filtered_file1['Average RTT'] = average_values

columns_to_average_6 = filtered_file2.filter(regex='IPv6 RTT\..*\.1', axis=1)

# Calculate the average for each row (skip NaN values)
average_values_6 = columns_to_average_6.mean(axis=1, skipna=True)

# Add the average values to the original DataFrame
filtered_file2['Average RTT'] = average_values_6
# Display the resulting DataFrame
#print(filtered_file1)

grouped_df_4 = filtered_file1.groupby(['Network Service Provider','Date'])['Average RTT'].mean().reset_index()
grouped_df_6 = filtered_file2.groupby(['Network Service Provider', 'Date'])['Average RTT'].mean().reset_index()

print(grouped_df_4)
print(grouped_df_6)

fig, ax = plt.subplots(figsize=(12, 6))

# Plot bar for IPv4 NaN counts
ax.bar(grouped_df_4.index - 0.2, grouped_df_4['Average RTT'], width=0.4, label='IPv4 Avg RTT', color='green')

# Plot bar for IPv4 non-NaN counts
ax.bar(grouped_df_6.index + 0.2, grouped_df_6['Average RTT'], width=0.4, label='IPv6 Avg RTT', color='purple')

ax.set_xticks(grouped_df_4.index)
ax.set_xticklabels([f"{date}\n{isp}" for date, isp in zip(grouped_df_4['Date'], grouped_df_4['Network Service Provider'])], rotation=45, ha='right')
ax.set_xlabel('Date and ISP')
ax.set_ylabel('Avg RTT (ms)')
ax.legend()
plt.title('Comparison of Avg RTT for IPv4 and IPv6')
plt.tight_layout()
plt.show()

# Calculate average of all values
avg_count_4 = grouped_df_4['Average RTT'].mean()
avg_count_6 = grouped_df_6['Average RTT'].mean()

print(f'Average RTT IPv4: {avg_count_4}')
print(f'Average RTT IPv6: {avg_count_6}')

#Variance of each Max RTT - Stability
# Select columns that match the pattern 'IPv4 RTT.*.0'
filter_file1 = filter_file1.iloc[:filter_file2.shape[0], :]
columns_ipv4_rtt_0 = filter_file1.filter(regex='IPv4 RTT\..*\.0', axis=1)
columns_ipv4_rtt_0 = columns_ipv4_rtt_0.fillna(0)

# Select columns that match the pattern 'IPv6 RTT.*.0'
columns_ipv6_rtt_0 = filter_file2.filter(regex='IPv6 RTT\..*\.0', axis=1)
columns_ipv6_rtt_0 = columns_ipv6_rtt_0.fillna(0)

# Calculate the variance for each row (skip NaN values)
filter_file1['Variance_4'] = columns_ipv4_rtt_0.var(axis=1)
filter_file2['Variance_6'] = columns_ipv6_rtt_0.var(axis=1)

print(filter_file1.shape)
print(filter_file2.shape)


colors_ipv4 = np.where(filter_file1['Variance_4'].notna(), 'red', 'blue')
colors_ipv6 = np.where(filter_file2['Variance_6'].notna(), 'blue', 'red')

# Plot scatter plot for both IPv4 and IPv6 on the same graph
plt.figure(figsize=(8, 6))
plt.scatter(filter_file1['Variance_4'], filter_file2['Variance_6'], c=colors_ipv4, label='IPv4 and IPv6 RTT Variance', cmap='coolwarm')
plt.title('Scatter Plot for IPv4 and IPv6 RTT Variance')
plt.xlabel('Variance IPv4 RTT')
plt.ylabel('Variance IPv6 RTT')
plt.legend()
plt.xlim(0, 1000)
plt.ylim(0, 10000)
plt.show()

# Plot scatter plot for both IPv4 and IPv6 on the same graph
plt.figure(figsize=(8, 6))
plt.scatter(filter_file2['Variance_6'], filter_file1['Variance_4'], c=colors_ipv6, label='IPv6 and IPv6 #RTT Variance', cmap='coolwarm')
plt.title('Scatter Plot for IPv4 and IPv6 RTT Variance')
plt.xlabel('Variance IPv6')
plt.ylabel('Variance IPv4')
plt.legend()
plt.xlim(0, 1000)
plt.ylim(0, 10000)
plt.show()


print(file1)
#Comparing ISPs
#On Raw Data
print("Per ISP No ping data found")
isp_data = pd.concat([filtered_file1,filtered_file2], ignore_index = True)
isp_data_df = pd.DataFrame(isp_data, columns=['Network Service Provider', 'IPv4 RTT.0.0'])
print(isp_data_df)
# Group by "Network Service Provider" and count NaN values in the "IPv4 RTT.0.0" column
nan_counts_per_isp = isp_data_df.groupby('Network Service Provider')['IPv4 RTT.0.0'].apply(lambda x: x.isna().sum()).reset_index(name='NaN_Counts')

# Print the result
print(nan_counts_per_isp)


#Gelocation
# Assuming isp_data is a tuple containing data
# Convert it to a DataFrame
geo_df_4 = pd.DataFrame(filtered_file1, columns=['IPv4 County'])
geo_df_6 = pd.DataFrame(filtered_file2, columns=['IPv6 County'])
print(geo_df_4)

nan_geo_4 = geo_df_4['IPv4 County'].isna().sum()
nan_geo_6 = geo_df_6['IPv6 County'].isna().sum()

# Print the result
print(f"IPv4 Location: {nan_geo_4}")
print(f"IPv6 Location: {nan_geo_6}")

#Unique counteries
# Extract unique countries from the 'IPv4 Country' column
unique_countries = geo_df_4['IPv4 County'].unique()
print(unique_countries)

# Count occurrences of each country
country_counts = geo_df_4['IPv4 County'].value_counts()

# Plot a pie chart
plt.figure(figsize=(8, 8))
plt.pie(country_counts, labels=country_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('Distribution of Countries (IPv4 Geolocation)')
plt.show()


#Number of Hops per Geolocation
# Group by 'IPv4 Country' and calculate the average hop count for each country
average_hop_count_by_country = filtered_df1.groupby('IPv4 County')['Hop Count'].mean().reset_index()

# Sort the DataFrame by average hop count in descending order for better visualization
average_hop_count_by_country = average_hop_count_by_country.sort_values(by='Hop Count', ascending=False)

# Plot a bar chart for average hop count by country
plt.figure(figsize=(12, 6))
plt.bar(average_hop_count_by_country['IPv4 County'], average_hop_count_by_country['Hop Count'], color='skyblue')
plt.title('Average Hop Count by Country')
plt.xlabel('Country')
plt.ylabel('Average Hop Count')
plt.xticks(rotation=45, ha='right')
plt.show()









