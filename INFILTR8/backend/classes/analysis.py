import os
import xml.etree.ElementTree as ET
import pandas as pd
import category_encoders as ce
from sklearn.preprocessing import MinMaxScaler


# Path to the Nessus XML file, change line 10 to match path where your NESSUS file is
nessus_file = '../output/data_with_exploits.csv'

# Base directory for output CSV files, change line 13 to where you want output CSVs to go
output_base_dir = '../output'

# Disallowed IPS
disallowed_ips = None

# Construct paths for output CSV files
data_with_exploits_path = os.path.join(output_base_dir, 'data_with_exploits.csv')
ranked_entry_points_path = os.path.join(output_base_dir, 'ranked_entry_points.csv')
entrypoint_most_info_path = os.path.join(output_base_dir, 'entrypoint_most_info.csv')
port_0_entries_path = os.path.join(output_base_dir, 'port_0_entries.csv')

def analyze_nessus_file():
    # Initialize an empty DataFrame
    df = pd.read_csv(nessus_file)

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
