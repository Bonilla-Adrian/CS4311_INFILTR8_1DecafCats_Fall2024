import csv
import os

def processAndUpload(driver, username, projectId):
    output_base_dir = os.getcwd()+'/output/'
    
    ranked = fileRead(output_base_dir+'ranked_entry_points.csv')
    mostInfo = fileRead(output_base_dir+'entrypoint_most_info.csv')
    query = """
    MATCH (p:Project {projectId: $projectId})-[r:HAS_PROJECT]->(u:Analyst {username: $username}) 
    WITH p
    CREATE (r:Report {name: $reportName, contents: $upload})
    CREATE (r)-[:HAS_FILE]->(p)
    RETURN count(r) as total
    """
    
    with driver.session() as session:
        numProject = session.run(query, username=username, projectId=projectId, reportName='rankedList',upload=ranked)
        numProject = session.run(query, username=username, projectId=projectId, reportName='mostInfo',upload=mostInfo)
        return numProject.single()['total']

def fileRead(filepath):
    wholeCsv = []
    with open(filepath, mode = 'r') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            stringLine = ''
            for part in lines:
                stringLine = stringLine + ' ' + part
            wholeCsv.append(stringLine)
        return wholeCsv