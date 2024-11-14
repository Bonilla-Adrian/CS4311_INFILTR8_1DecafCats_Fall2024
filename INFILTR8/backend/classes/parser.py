# change lines 10 and 13 to match your desired paths
import os
import xml.etree.ElementTree as ET
import pandas as pd
import category_encoders as ce
from sklearn.preprocessing import MinMaxScaler

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

def parserFile(fileName):
    currentPath = os.getcwd()
    nessus_file = currentPath+'/nessus-drop/'+fileName
    output_base_dir = currentPath+'/output/'
    
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
    
    return unique_ips