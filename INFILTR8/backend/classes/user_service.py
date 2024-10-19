from neo4j import GraphDatabase
import bcrypt


def create_user(tx, username, first_name, last_name, hashed_password):
    query = (
        """
        MERGE (a:Analyst {username: $username})
        ON CREATE SET a.first_name = $first_name, a.last_name = $last_name, a.password = $hashed_password
        MERGE (u:User)
        CREATE (a)-[:IS_A]->(u)
        """
        )
    
    tx.run(query, first_name=first_name, last_name=last_name, username=username, hashed_password=hashed_password)

def find_user_by_username(tx, username):
    query = "MATCH (a:Analyst {username: $username}) RETURN a"
    result = tx.run(query, username=username)
    return result.single()

def login_user(driver, username, password):
    with driver.session() as session:
        user_record = session.read_transaction(find_user_by_username, username)
        if user_record:
            user = user_record["a"]
            hashed_password = user["password"]
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                return True
        return False