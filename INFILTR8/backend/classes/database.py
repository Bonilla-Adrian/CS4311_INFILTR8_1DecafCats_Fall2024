from neo4j import GraphDatabase

class DataBase:
    
    def __init__(self,URI, AUTH):
        self.URI = URI
        self.AUTH = AUTH
    
    def driver_make(self):
        return GraphDatabase.driver(self.URI, auth=self.AUTH)
    
    def run_query(self, query):
        driver = self.driver_make()
        records, summary, keys = driver.execute_query(query, database_="neo4j")
        driver.close()
        return records

