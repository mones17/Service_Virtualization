const { response } = require("express");

const { GetResquestID,
        ReadAPIMode,
        SaveResponse,
        GetResponse } = require('../DB/DBController');
const { SendAPICall } = require('../API/APIController');

const ProcessRequest = async(req, res = response) =>
{
    const method = req.method;
    if (method == 'OPTIONS')
    {
        res.status(204).send()
    }
    else
    {
        const APIMODE = ReadAPIMode();
        const requestID = await GetResquestID(req.headers.host, req.url)
        switch (APIMODE) {
            case 1:
                // APIMODE = 1 => Recording Mode.
                try {
                    const apiResponse = await SendAPICall(req)
                    res.status(apiResponse.status).send(apiResponse.data)
                    await SaveResponse(requestID, apiResponse)
                } catch (error) {
                    console.log(error)
                    res.status(500).send()
                }
                break;
            case 2:
                // APIMODE = 2 => Mocking Mode.
                try {
                    var savedResponse = await GetResponse(requestID)
                    if (savedResponse == null)
                    {
                        savedResponse = await SendAPICall(req)
                        await SaveResponse(requestID, savedResponse)
                    }
                    else
                        await new Promise(resolve => setTimeout(resolve, 2000));
                    res.status(savedResponse.status).send(savedResponse.data);
                } catch (e) {
                    console.log(e)
                    res.status(500).send()
                }

                break;
            default:
                res.status(500).send();
                break;
        }
    }
}
const RedirectRequest = async (req, res = response) =>
{
    res.status(200).send('Good');
}

module.exports = 
{
    ProcessRequest,
    RedirectRequest
}