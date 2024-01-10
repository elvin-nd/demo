from pymongo import MongoClient


class DB:
    """
    Create a new connections for the database
    """

    def __init__(self):
        self.client = MongoClient(
            "mongodb://dheeraj:zo6W~CTi0N1J@demo-cluster.cluster-c1aicywskjyq.ap-south-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&tlsAllowInvalidHostnames=true"
        )
        self.db = self.client.pa.settings
        self.log = self.client.pa.log

    def get_db(self):
        """
        Returns the db instance
        """
        return self.db

    def get_log(self):
        return self.log


db = DB()
