# change lines 10 and 13 to match your desired paths

import os
import xml.etree.ElementTree as ET
import pandas as pd
import category_encoders as ce
from sklearn.preprocessing import MinMaxScaler

# Path to the Nessus XML file, change line 10 to match path where your NESSUS file is
nessus_file = '/Users/tomas/CS4311_INFILTR8_Team1_DecafCats_Fall2024/INFILTR8/backend/nessus-drop/Nessus_scan_file1.nessus'

# Base directory for output CSV files, change line 13 to where you want output CSVs to go
output_base_dir = '/Users/tomas/CS4311_INFILTR8_Team1_DecafCats_Fall2024/INFILTR8/backend/output'

# Construct paths for output CSV files
data_with_exploits_path = os.path.join(output_base_dir, 'data_with_exploits.csv')
ranked_entry_points_path = os.path.join(output_base_dir, 'ranked_entry_points.csv')
entrypoint_most_info_path = os.path.join(output_base_dir, 'entrypoint_most_info.csv')
port_0_entries_path = os.path.join(output_base_dir, 'port_0_entries.csv')

# Initialize an empty DataFrame
df = pd.DataFrame(columns=[])
column_names = ['file', 'name', 'ip', 'port', 'viable_exploit', 'archetype']
have_names = False  # Flag to check if column names have been added

# Parse XML file using ElementTree
main_tree = ET.parse(nessus_file)

# Function to map plugin names and families to archetypes
def map_to_archetype(plugin_name, plugin_family):
    archetypes = {
        'Unauthenticated port bypass': ['Port Bypass', 'Network'],
        'default credentials': ['Default Credentials', 'Authentication'],
        'unpatched software exploits': ['Vulnerability', 'Exploitable'],
        'missing encryption protocols': ['Encryption', 'SSL'],
        'weak passwords (brute force)': ['Weak Password', 'Brute Force'],
        'Zeroize': ['Zeroize']
    }
    for archetype, keywords in archetypes.items():
        for keyword in keywords:
            if keyword.lower() in plugin_name.lower() or keyword.lower() in plugin_family.lower():
                return archetype
    return 'Other'

# Iterate through each ReportHost element in the XML
for host in main_tree.findall('.//ReportHost'):
    host_name = host.get('name')  # Extract host name
    host_ip = host.find('.//HostProperties/tag[@name="host-ip"]').text  # Extract host IP
    
    # Iterate through each child element of ReportHost
    for child in host:
        if not child.tag == 'ReportItem':
            continue
        if not have_names:
            have_names = True
            # Add all attributes of the ReportItem to column_names if not already present
            for key in child.attrib:
                if key not in column_names:
                    column_names.append(key)
            # Initialize DataFrame with updated column names
            df = pd.DataFrame(columns=column_names)
        
        # Add a new row to DataFrame for each ReportItem
        ind = len(df.index)
        df.loc[ind] = ''
        df.at[ind, 'name'] = host_name
        df.at[ind, 'file'] = os.path.basename(nessus_file)
        df.at[ind, 'ip'] = host_ip
        df.at[ind, 'port'] = child.attrib.get('port')

        # Check for viable exploit indicators
        severity = int(child.attrib.get('severity', '0'))
        exploit_available = child.find('.//exploit_available')
        exploitability_ease = child.find('.//exploitability_ease')
        cvss_base_score = float(child.attrib.get('cvss_base_score', '0.0'))

        viable_exploit = (exploit_available is not None) or (exploitability_ease is not None and exploitability_ease.text in ['Exploitable', 'Easy'])

        df.at[ind, 'viable_exploit'] = viable_exploit

        # Add attributes of ReportItem to respective columns in DataFrame
        for key in child.attrib:
            df.at[ind, key] = child.attrib.get(key)

        # Map pluginName and pluginFamily to archetypes
        plugin_name = child.attrib.get('pluginName', '')
        plugin_family = child.attrib.get('pluginFamily', '')
        archetype = map_to_archetype(plugin_name, plugin_family)
        df.at[ind, 'archetype'] = archetype

# Export DataFrame to CSV file
df.to_csv(data_with_exploits_path, index=False)

unique_ips = df['ip'].unique()

# Debugging: Print DataFrame shape and head to verify final output
print(f"DataFrame shape: {df.shape}")
print(df.head())

# Encode categorical variables
plugin_family = pd.get_dummies(df['pluginFamily'])
protocol = pd.get_dummies(df['protocol'])
svc = pd.get_dummies(df['svc_name'])
port = pd.get_dummies(df['port'])

# Apply binary encoding to 'pluginID' column using category_encoders
encoder = ce.BinaryEncoder(cols=['pluginID'])
encoded_data = encoder.fit_transform(df)

# Encode 'archetype' column
archetype_encoded = pd.get_dummies(df['archetype'])

# Drop unnecessary columns and concatenate encoded categorical variables
encoded_data = encoded_data.drop(['pluginFamily', 'file', 'name', 'ip', 'port', 'svc_name', 'pluginName', 'protocol'], axis=1)
encoded_data = pd.concat([encoded_data, protocol, svc, port, plugin_family, archetype_encoded], axis=1)

# Include 'viable_exploit' in the dataset
viable_exploit = df['viable_exploit'].astype(int)
encoded_data = pd.concat([encoded_data, viable_exploit], axis=1)

# Debugging: Print the encoded DataFrame
print('\nBelow is the encoded data\n')
print(encoded_data.head())

# Analyze entry points
# Filter out entries with "Port 0" for entry points analysis
filtered_df = df[df['port'] != '0']

# Ensure severity is numeric
filtered_df['severity'] = pd.to_numeric(filtered_df['severity'], errors='coerce')

# Group the data by IP and port, and count the number of unique attributes/data points for each entry point
entry_point_info = filtered_df.groupby(['ip', 'port']).agg({
    'severity': 'mean',
    'viable_exploit': 'sum',
    'pluginID': 'nunique'
}).reset_index()

entry_point_info.columns = ['ip', 'port', 'severity_score', 'exploit_score', 'distinct_vulnerabilities']

# Normalize the scores
scaler = MinMaxScaler()
entry_point_info[['severity_score', 'exploit_score', 'distinct_vulnerabilities']] = scaler.fit_transform(entry_point_info[['severity_score', 'exploit_score', 'distinct_vulnerabilities']])

# Calculate the combined score with specified weights
entry_point_info['combined_score'] = (
    0.5 * entry_point_info['severity_score'] +
    0.3 * entry_point_info['exploit_score'] +
    0.2 * entry_point_info['distinct_vulnerabilities']
)

# Sort by the combined score
ranked_entry_points = entry_point_info.sort_values(by='combined_score', ascending=False)
print(type(ranked_entry_points))

# Display the ranked entry points
print("\nRanked entry points based on combined score:")
print(ranked_entry_points.head(10))

# Save the result to a CSV file
ranked_entry_points.to_csv(ranked_entry_points_path, index=False)
print(f"\nRanked entry points saved to {ranked_entry_points_path}")

# Save the entry points with most information
entry_point_info_sorted = filtered_df.groupby(['ip', 'port']).size().reset_index(name='vulnerability_count').sort_values(by='vulnerability_count', ascending=False)
entry_point_info_sorted.to_csv(entrypoint_most_info_path, index=False)
print(f"\nTop entry points saved to {entrypoint_most_info_path}")

# Filter entries with Port 0 from the data_with_exploits.csv
port_0_entries = df[df['port'] == '0']


# Print out or save the filtered entries
print("\nEntries mapped to Port 0:\n")
print(port_0_entries)

# Save to a separate CSV for review
port_0_entries.to_csv(port_0_entries_path, index=False)
print(f"\nPort 0 entries saved to {port_0_entries_path}")
