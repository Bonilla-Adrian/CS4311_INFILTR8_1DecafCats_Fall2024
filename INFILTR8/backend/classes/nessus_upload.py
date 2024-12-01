import csv
import os

def fileRead(filepath):
    wholeCsv = []
    try:
        with open(filepath, mode='r') as file:
            csvFile = csv.reader(file)
            for lines in csvFile:
                stringLine = ''
                for part in lines:
                    if " " in part:
                        part = part.replace(" ", "-")
                    stringLine = stringLine + ' ' + part
                wholeCsv.append(stringLine)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")  # Debugging message
    return wholeCsv

def turnIntoCsv(contents):
    result = []
    for line in contents:
        result.append(line.split())
    return result

def getDataExploits(driver, username, projectId):
    query = """
    MATCH (f:Report {name: "dataExploits"})-[h:HAS_FILE]->(p:Project {projectId: $projectId})-[r:HAS_PROJECT]->(u:Analyst {username: $username}) 
    RETURN f.contents as content
    """
    with driver.session() as session:
        resultCount = session.run(query, username=username, projectId=projectId)
        try:
            return turnIntoCsv(resultCount.single()['content'])
        except TypeError:
            return []

def countResults(driver, username, projectId):
    query = """
    MATCH (f:Report)-[h:HAS_FILE]->(p:Project {projectId: $projectId})-[r:HAS_PROJECT]->(u:Analyst {username: $username}) 
    RETURN count(f) as reportCount
    """
    with driver.session() as session:
        resultCount = session.run(query, username=username, projectId=projectId)
        return resultCount.single()['reportCount']
    
def deleteResults(driver, username, projectId):
    query = """
    MATCH (f:Report)-[h:HAS_FILE]->(p:Project {projectId: $projectId})-[r:HAS_PROJECT]->(u:Analyst {username: $username}) 
    DETACH DELETE f
    """
    with driver.session() as session:
        session.run(query, username=username, projectId=projectId)

def processAndUpload(driver, username, projectId, filePaths):
    output_base_dir = os.path.join(os.getcwd(), 'output')
    filePathsList = filePaths.split(',')  # Split the file paths into a list
    filePathsList = [file_path.strip() for file_path in filePathsList]  # Remove whitespace

    # Debugging: Print the processed file paths
    print(f"Processing file paths: {filePathsList}")

    # Check if the output directory exists
    if not os.path.exists(output_base_dir):
        print(f"Output directory does not exist: {output_base_dir}")
        return

    # Delete existing results if they exist
    if countResults(driver, username, projectId) != 0:
        deleteResults(driver, username, projectId)

    # Process each Nessus file
    for file_path in filePathsList:
        file_path = file_path.strip()  # Ensure no trailing spaces
        if not os.path.exists(file_path):  # Validate file existence
            print(f"File not found: {file_path}")
            continue

        # Assuming required output files are already generated
        ranked = fileRead(os.path.join(output_base_dir, 'ranked_entry_points.csv'))
        mostInfo = fileRead(os.path.join(output_base_dir, 'entrypoint_most_info.csv'))
        dataExploits = fileRead(os.path.join(output_base_dir, 'data_with_exploits.csv'))
        portZero = fileRead(os.path.join(output_base_dir, 'port_0_entries.csv'))

        query = """
        MATCH (p:Project {projectId: $projectId})-[r:HAS_PROJECT]->(u:Analyst {username: $username}) 
        CREATE (r:Report {name: $reportName, contents: $upload})
        CREATE (r)-[:HAS_FILE]->(p)
        """

        with driver.session() as session:
            try:
                base_file_name = os.path.basename(file_path)
                session.run(query, username=username, projectId=projectId, reportName=f'{base_file_name}_rankedEntry', upload=ranked)
                session.run(query, username=username, projectId=projectId, reportName=f'{base_file_name}_mostInfo', upload=mostInfo)
                session.run(query, username=username, projectId=projectId, reportName=f'{base_file_name}_dataExploits', upload=dataExploits)
                session.run(query, username=username, projectId=projectId, reportName=f'{base_file_name}_portZero', upload=portZero)
            except Exception as e:
                print(f"Error inserting data for file {base_file_name}: {e}")
