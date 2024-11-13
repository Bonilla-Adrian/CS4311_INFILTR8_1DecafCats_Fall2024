import os
import datetime

def countProjects(driver, username):
    query = "MATCH (p:Project)-[r:HAS_PROJECT]->(u:Analyst {username: $username}) RETURN count(p) as total"

    with driver.session() as session:
        numProject = session.run(query, username=username)
        return numProject.single()['total']

def projectParser(project):
    return {
        'projectId': project['projectId'],
        'projectName': project['projectName'],  # Corrected key name
        'ips': project['ips'],
        'exploits': project['exploits'],
        'file': project['file'],
        'fileSize': project['fileSize'],
        'user': project['user'],
        'creation': project['creation'],
        'status': project['status']
    }

def allProjectInfo(driver, username):
    query = """
        MATCH (p:Project)-[:HAS_PROJECT]->(a:Analyst {username: $username}) 
        RETURN 
            p.projectId AS projectId, 
            p.projectName AS projectName, 
            p.ips AS ips, 
            p.exploits AS exploits, 
            p.file AS file, 
            p.fileSize AS fileSize, 
            p.user AS user, 
            p.creation AS creation, 
            p.status AS status
    """
    with driver.session() as session:
        result = session.run(query, username=username)
        all_projects = [projectParser(record) for record in result]
        return all_projects


def getProjectInfomation(driver, username, projectId):
    query = "MATCH (p:Project {projectId: $projectId})-[r:HAS_PROJECT]->(u:Analyst {username: $username}) RETURN p as project"

    with driver.session() as session:
        result = session.run(query, projectId=projectId, username=username)
        project = result.single()["project"]
        return projectParser(project)

def createProject(driver, username, projectName, fileName, status, ips, exploits):

    fileSize = int(os.path.getsize(os.getcwd()+'/nessus-drop/'+fileName) / 1000)
    creation = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    query = (
        """
        MATCH (u:Analyst {username: $username})
        CREATE (p:Project {projectId: $projectId, projectName: $projectName, user: $username, status: $status, file: $fileName, fileSize: $fileSize, creation: $creation, ips: $ips, exploits: $exploits})-[:HAS_PROJECT]->(u)
        return p.projectId AS projectId
        """
        )

    projectId = countProjects(driver, username) + 1
    with driver.session() as session:
        result = session.run(query, projectId=projectId, username=username, user=username, status=status, projectName=projectName, fileName=fileName, fileSize=fileSize, creation=creation, ips=ips, exploits=exploits)
        projectId = result.single()["projectId"]
        return projectId

def updateProjectStatus(driver, projectId, username, status):
    query = """
    MATCH (p:Project {projectId: $projectId, user: $username})
    SET p.status = $status
    RETURN p.status AS updatedStatus
    """
    
    with driver.session() as session:
        result = session.run(query, projectId=projectId, username=username, status=status)
        return result.single()['updatedStatus']

def getAllProjectIds(driver, username):
    query = "MATCH (p:Project)-[:HAS_PROJECT]->(a:Analyst{username: $username}) RETURN p.projectId AS projectIds"
    with driver.session() as session:
        result = session.run(query, username=username)
        allIds = []
        for id in result:
            allIds.append(id["projectIds"])
        print(allIds)
        return allIds
