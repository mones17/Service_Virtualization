const axios = require('axios');

const SendAPICall = async (req) =>
{
    const method = req.method;
    var realAPIResponse;
    const axiosInstance = await axios.create();
    try
    {
        axiosInstance.defaults.headers.common['Authorization'] = req.header('Authorization');
    }
    catch (e) {
    }
    const url = `https://${req.headers.host}${req.url}`;
    switch (method)
    {
        case "POST":
            realAPIResponse = await axiosInstance.post(url, req.body);
            break;
        case "GET":
            realAPIResponse = await axiosInstance.get(url, req.body);
            break;
        case "OPTIONS":
            realAPIResponse = await axiosInstance.options(url, req.body);
            break;
    }
    return realAPIResponse;
}

module.exports =
{
    SendAPICall
}