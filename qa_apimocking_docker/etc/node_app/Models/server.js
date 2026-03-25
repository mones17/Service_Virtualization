const express = require('express');
const { ProcessRequest } = require('../controllers/ApiCall')
const { GetResponses,
    AcceptResponse,
    RejectResponse} = require('../controllers/AdminCall');

class Server
{
    constructor()
    {
        this.app = express();
        this.app.use(express.json()) // For parsing application/json
        this.port = 8080;
        this.routes();
    }

    async routes()
    {
        this.app.get('/sv/admin/getResponses', GetResponses)
        this.app.post('/sv/admin/acceptResponse', AcceptResponse)
        this.app.post('/sv/admin/rejectResponse', RejectResponse)
        this.app.all('*', ProcessRequest);
    }

    listen()
    {
        this.app.listen(this.port, () => 
        {
            console.log('Server running on port: ', this.port)
        });
    }
}
module.exports = Server;