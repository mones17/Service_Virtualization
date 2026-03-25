const cassandra = require('cassandra-driver');
const DataBaseConection = async () =>
{
    try 
    {
        const client = new cassandra.Client(
        {
            contactPoints: ['127.0.0.1:9042'],
            localDataCenter: 'datacenter1',
            keyspace: 'TMT'
        });
        console.log('DataBase connected');
    } 
    catch (error) 
    {
        throw new Error('Error trying to connect to the Data Base');
    }
}

module.exports =
{
    DataBaseConection
}