const { response, request } = require("express");
const { GetResquestID,
    GetResponsesUsingRequestID,
    AcceptResponseUsingResponseID,
    RejectResponseUsingResponseID} = require('../DB/DBController');

const AddEndpoint = async (req, res = response) =>
{
    await exec('docker restart qa_apimocking_docker_nginx_1');
}

const GetResponses = async (req, res = response) =>
{
    const service = req.query.service;
    const resource = req.query.resource;
    const requestID = await GetResquestID(service, resource)
    const savedResponses = await GetResponsesUsingRequestID(requestID)
    res.status(200).send(savedResponses)
}
const AcceptResponse = async (req, res = response) =>
{
    const responseID = req.query.responseID;
    const wasChangeMade = await AcceptResponseUsingResponseID(responseID)
    if (wasChangeMade)
        res.status(200).send('OK')
    else
        res.status(500).send('Error Changing Response')
}
const RejectResponse = async (req, res = response) =>
{
    const responseID = req.query.responseID;
    const wasChangeMade = await RejectResponseUsingResponseID(responseID)
    if (wasChangeMade)
        res.status(200).send('OK')
    else
        res.status(500).send('Error Changing Response')
}
module.exports =
{
    AddEndpoint,
    GetResponses,
    AcceptResponse,
    RejectResponse
}