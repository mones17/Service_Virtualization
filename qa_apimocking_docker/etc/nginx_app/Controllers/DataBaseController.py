from getpass import getuser
from http.client import responses
import uuid
from cassandra.cluster import Cluster
cluster = Cluster(contact_points=['cassandradb'])
session = cluster.connect('servicevirtualization')

def get_trafficAnalyzer_status(host):
    getTrafficAnalyzerStatusQuery = session.prepare('SELECT is_trafficanalyzer FROM service WHERE host = ? ALLOW FILTERING')
    getTrafficAnalyzerStatusResult = session.execute(getTrafficAnalyzerStatusQuery, [host])
    return getTrafficAnalyzerStatusResult[0].is_trafficanalyzer