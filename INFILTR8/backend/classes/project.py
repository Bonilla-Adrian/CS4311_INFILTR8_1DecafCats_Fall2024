import os
import datetime
from classes import nessus_upload 

def getIdFromName(driver, username, projectName):
    query = "MATCH (p:Project {projectName: $projectName})-[r:HAS_PROJECT]->(a:Analyst {username: $username}) RETURN p.projectId as id"
    
    with driver.session() as session:
        id = session.run(query, projectName=projectName, username=username)
        return id.single()['id']

def countProjects(driver, username):
    query = "MATCH (p:Project)-[r:HAS_PROJECT]->(u:Analyst {username: $username}) RETURN count(p) as total"

    with driver.session() as session:
        numProject = session.run(query, username=username)
        return numProject.single()['total']
    
def countFiles(driver, username, projectId):
    query = "MATCH (f:File)-[r:NESSUS_FILE]->(p:Project {user: $user, projectId: $projectId}) RETURN count(f) as total"
    with driver.session() as session:
        numProject = session.run(query, user=username, projectId=projectId)
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
    
def fileParser(file):
    return {
        'projectName': file['projectName'],
        'fileId': file['fileId'],
        'ips': file['ips'],
        'exploits': file['exploits'],
        'file': file['file'],
        'fileSize': file['fileSize'],
        'creation': file['creation'],
        'status': file['status']
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
    
def allProjectInfoMany(driver, username):
    query = """
        MATCH (f:File)-[r1:NESSUS_FILE]->(p:Project)-[:HAS_PROJECT]->(a:Analyst {username: $username}) 
        RETURN 
            f.fileId AS fileId, 
            f.projectName AS projectName, 
            f.ips AS ips, 
            f.exploits AS exploits, 
            f.file AS file, 
            f.fileSize AS fileSize, 
            f.creation AS creation, 
            f.status AS status
    """
    with driver.session() as session:
        result = session.run(query, username=username)
        all_projects = [fileParser(record) for record in result]
        return all_projects


def getProjectInfomation(driver, username, projectId):
    query = "MATCH (p:Project {projectId: $projectId})-[r:HAS_PROJECT]->(u:Analyst {username: $username}) RETURN p as project"

    with driver.session() as session:
        result = session.run(query, projectId=projectId, username=username)
        project = result.single()["project"]
        return projectParser(project)
    
def getProjectInfomationManyTest(driver, username, projectId, fileId):
    query = "MATCH (f:File {fileId: $fileId})-[r1:NESSUS_FILE]->(p:Project {projectId: $projectId})-[r:HAS_PROJECT]->(u:Analyst {username: $username}) RETURN f as file"

    with driver.session() as session:
        result = session.run(query, fileId=fileId, projectId=projectId, username=username)
        file = result.single()["file"]
        return fileParser(file)

def createProject(driver, username, projectName, fileName, status, ips, exploits):

    filePath = os.path.join(os.getcwd(), 'nessus-drop', fileName)
    fileSize = int(os.path.getsize(filePath) / 1000)
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

def testCreateProjectMany(driver, username, projectName, fileName, status, ips, exploits):
    # filePath = os.path.join(os.getcwd(), 'nessus-drop', fileName)
    # fileSize = int(os.path.getsize(filePath) / 1000)
    creation = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    query = (
        """
        MATCH (u:Analyst {username: $username})
        CREATE (p:Project {projectId: $projectId, projectName: $projectName, user: $user})-[:HAS_PROJECT]->(u)
        return p.projectId AS projectId
        """
        )
    
    query2 = """
    MATCH (p:Project{projectId: $projectId, projectName: $projectName, user: $user}) 
    CREATE (f:File{fileId: $fileId, status: $status, file: $fileName, fileSize: $fileSize, creation: $creation, ips: $ips, exploits: $exploits, projectName: $projectName})-[:NESSUS_FILE]->(p) 
    return f.id AS id
    """
    
    projectId = countProjects(driver, username) + 1
    # fileId = countFiles(driver, username, projectId) + 1
    with driver.session() as session:
        result = session.run(query, projectId=projectId, username=username, projectName=projectName, user=username)
        projectId = result.single()["projectId"]
        for i in range(len(fileName)):
            filePath = os.path.join(os.getcwd(), 'nessus-drop', fileName[i])
            fileSize = int(os.path.getsize(filePath) / 1000)
            fileId = countFiles(driver, username, projectId) + 1
            result2 = session.run(query2, projectId=projectId, projectName=projectName, user=username, fileId=fileId, status=status, fileName=fileName[i], fileSize=fileSize, creation=creation, ips=ips[i], exploits=exploits[i])
            id = result2.single()["id"]
            nessus_upload.uploadDataExAndPortZero(driver, username, projectId, fileId, fileName[i])
            
        return projectId

def updateProjectStatus(driver, projectId, username, status, fileId):
    query = """
    MATCH (f:File {fileId: $fileId})-[r1:NESSUS_FILE]->(p:Project {projectId: $projectId, user: $username})
    SET f.status = $status
    RETURN f.status AS updatedStatus
    """
    
    with driver.session() as session:
        result = session.run(query, fileId=fileId, projectId=projectId, username=username, status=status)
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

def deleteCurrentProject(driver, username, projectId):
    deleteReport = """
    MATCH (n:Project{projectId: $projectId, user: $username})<-[HAS_FILE]-(f:File)<-[r]-(node) 
    DETACH DELETE node
    """
    deleteAnalysis = """
    MATCH (n:Project{projectId: $projectId, user: $username})<-[r]-(node) 
    DETACH DELETE node
    """
    deleteProject = """
    MATCH (n:Project{projectId: $projectId, user: $username}) 
    DETACH DELETE n
    """
    
    with driver.session() as session:
        session.run(deleteReport, username=username, projectId=projectId)
        session.run(deleteAnalysis, username=username, projectId=projectId)
        session.run(deleteProject, username=username, projectId=projectId)
    