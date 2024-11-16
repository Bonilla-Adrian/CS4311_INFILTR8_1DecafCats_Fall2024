import csv
import os

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

def processAndUpload(driver, username, projectId):
    output_base_dir = os.getcwd()+'/output/'
    
    ranked = fileRead(output_base_dir+'ranked_entry_points.csv')
    mostInfo = fileRead(output_base_dir+'entrypoint_most_info.csv')
    dataExploits = fileRead(output_base_dir+'data_with_exploits.csv')
    portZero = fileRead(output_base_dir+'port_0_entries.csv')
    
    if countResults(driver, username, projectId) != 0:
        deleteResults(driver, username, projectId)
    
    query = """
    MATCH (p:Project {projectId: $projectId})-[r:HAS_PROJECT]->(u:Analyst {username: $username}) 
    WITH p
    CREATE (r:Report {name: $reportName, contents: $upload})
    CREATE (r)-[:HAS_FILE]->(p)
    """
    
    with driver.session() as session:
        session.run(query, username=username, projectId=projectId, reportName='rankedEntry',upload=ranked)
        session.run(query, username=username, projectId=projectId, reportName='mostInfo',upload=mostInfo)
        session.run(query, username=username, projectId=projectId, reportName='dataExploits',upload=dataExploits)
        session.run(query, username=username, projectId=projectId, reportName='portZero',upload=portZero)