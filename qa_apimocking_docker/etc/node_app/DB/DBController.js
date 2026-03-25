const fs = require('fs');
const cassandra = require('cassandra-driver');
const { stringify } = require('querystring');
const { response } = require('express');
constructor()
{
    try 
    {
        this.client = new cassandra.Client(
        {
            contactPoints: ['cassandradb:9042'],
            localDataCenter: 'datacenter1',
            keyspace: 'servicevirtualization'
        });
        console.log('DataBase connected');
    } 
    catch (error) 
    {
        throw new Error('Error trying to connect to the Data Base');
    }
}
const GetResquestID = async (service, resource) =>
{
    const getAllResourcesQuery = "SELECT resource FROM Request WHERE service = ? ALLOW FILTERING;";
    const getRequestIDQuery = "SELECT id FROM Request WHERE resource = ? ALLOW FILTERING;";
    const changeLastAccessQuery = "UPDATE Request SET last_access = toTimestamp(now()) WHERE id = ?;";
    const getAllResourcesResult = await this.client.execute(getAllResourcesQuery, [service]);
    let savedResource = '';
    getAllResourcesResult.rows.forEach(function (element)
    {
        var actualResource = element.resource
        if (resource.includes(actualResource))
        {
            savedResource = actualResource;
        }
    });
    const getRequestIDResult = await this.client.execute(getRequestIDQuery, [savedResource]);
    await this.client.execute(changeLastAccessQuery, [getRequestIDResult.rows[0].id])
    return getRequestIDResult.rows[0].id.toString().replace('-', '');
}
const GetResponsesUsingRequestID = async (requestID) =>
{
    var responses = [];
    const getResponsesUsingRequestIDQuery = "SELECT id, status_code, payload, is_valid FROM Response WHERE request_id = ? ALLOW FILTERING;";
    const changeLastAccessQuery = "UPDATE Response SET last_access = toTimestamp(now()) WHERE id = ?;";
    const getResponsesUsingRequestIDResult = await this.client.execute(getResponsesUsingRequestIDQuery, [requestID]);
    getResponsesUsingRequestIDResult.rows.forEach(Iterate = async (element, client = this.client) =>
    {
        responses.push
        (
            {
                id: element.id,
                status_code: element.status_code,
                payload:element.payload,
                is_valid:element.is_valid
            }
        )
        try
        {
            await this.client.execute(changeLastAccessQuery, [element.id])
        } catch (e)
        {
            console.log('Error changing date')
        }
        
    });
    return responses;
}
const AcceptResponseUsingResponseID = async (responseID) =>
{
    const changeIsValidUsingResponseIDQuery = "UPDATE Response SET is_valid = true, last_update = toTimestamp(now()) WHERE id = ?;";
    try
    {
        await this.client.execute(changeIsValidUsingResponseIDQuery, [responseID]);
        return true;
    } catch (e) {
        console.log('Error Changing Response')
        return false;
    }
}
const RejectResponseUsingResponseID = async (responseID) =>
{
    const changeIsValidUsingResponseIDQuery = "UPDATE Response SET is_valid = false, last_update = toTimestamp(now()) WHERE id = ?;";
    try
    {
        await this.client.execute(changeIsValidUsingResponseIDQuery, [responseID]);
        return true;
    } catch (e)
    {
        console.log('Error Changing Response')
        return false;
    }
}
const SaveResponse = async (requestID, response) =>
{
    const headers = await JSON.stringify(response.headers)
    const payload = await JSON.stringify(response.data)
    const insertResponseQuery = "INSERT INTO Response(id, request_id, status_code, headers, payload, is_valid, date_created, " +
        "last_update, last_access) VALUES (uuid(), ?, ?, ?, ?, ?, toTimestamp(now()), toTimestamp(now()), toTimestamp(now())); ";
    try
    {
        await this.client.execute(insertResponseQuery, [requestID, `${response.status}`, headers, payload, false]);
    } catch (e)
    {
        console.log('Error Saving Response')
    }
}
const GetResponse = async (requestID) =>
{
    const getResponseQuery = "SELECT payload, status_code, id FROM Response WHERE request_id=? AND is_valid=true ALLOW FILTERING;";
    const changeLastAccessQuery = "UPDATE Response SET last_access = toTimestamp(now()) WHERE id = ?;";
    const getResponseResult = await this.client.execute(getResponseQuery, [requestID]);
    if (getResponseResult.rowLength == 0)
    {
        return null;
    }
    const data = JSON.parse(getResponseResult.rows[getResponseResult.rowLength - 1].payload);
    const status = JSON.parse(getResponseResult.rows[getResponseResult.rowLength - 1].status_code);
    await this.client.execute(changeLastAccessQuery, [getResponseResult.rows[getResponseResult.rowLength - 1].id]);
    return { data, status };
}
const ReadAPIMode = () =>
{
    const APIModeFile = './DB/APIMode.txt'
    if(!fs.existsSync(APIModeFile))
    {
        return null;
    }
    const info = fs.readFileSync(APIModeFile, {encoding: 'utf-8'});
    const apiMode = parseInt(info);
    return apiMode;
}
module.exports =
{

    SaveResponse,
    GetResponse,
    GetResquestID,
    ReadAPIMode,
    GetResponsesUsingRequestID,
    AcceptResponseUsingResponseID,
    RejectResponseUsingResponseID
}