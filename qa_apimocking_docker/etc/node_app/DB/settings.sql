CREATE KEYSPACE IF NOT EXISTS TMT WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : '1' };
CREATE TABLE IF NOT EXISTS TMT.Pend (
deal_id uuid PRIMARY KEY,
VIN text,
response_body text
);

INSERT INTO TMT.Pend
(deal_id, VIN, response_body)
VALUES (uuid(), '985588858876', '{ "\"myKey\"": 0, "value": 0}');

SELECT * FROM Pend WHERE VIN='3N1AB7AP4JL623325' ALLOW FILTERING;

-- **************** SSV DATABASE SETUP ****************
CREATE KEYSPACE IF NOT EXISTS ServiceVirtualization WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : '1' };

CREATE TABLE IF NOT EXISTS ServiceVirtualization.Service (
id uuid PRIMARY KEY,
host varchar,
actual_ip varchar,
port varchar,
date_created timestamp,
last_update timestamp,
last_access timestamp,
name text,
is_trafficAnalyzer boolean
);
CREATE TABLE IF NOT EXISTS ServiceVirtualization.Request (
id uuid PRIMARY KEY,
service varchar,
resource varchar,
method varchar,
name varchar,
api_mode int,
date_created timestamp,
last_update timestamp,
last_access timestamp,
is_recorded boolean
);
CREATE TABLE IF NOT EXISTS ServiceVirtualization.Response (
id uuid PRIMARY KEY,
request_id text,
status_code text,
headers text,
payload text,
is_valid boolean,
date_created timestamp,
last_update timestamp,
last_access timestamp
);
CREATE TABLE IF NOT EXISTS ServiceVirtualization.User (
id uuid PRIMARY KEY,
email text,
role text,
name text,
password text,
date_created timestamp,
last_update timestamp,
last_access timestamp
);
CREATE TABLE IF NOT EXISTS ServiceVirtualization.UserService (
id uuid PRIMARY KEY,
user varchar,
service varchar,
date_created timestamp,
last_update timestamp,
last_access timestamp
);
CREATE TABLE IF NOT EXISTS ServiceVirtualization.Products (
id uuid PRIMARY KEY,
name text
);
CREATE TABLE IF NOT EXISTS ServiceVirtualization.Logs (
id uuid PRIMARY KEY,
message varchar,
level_affected text,
service_id text,
request_id text,
response_id text,
date_created timestamp,
user varchar,
is_error boolean
);
CREATE TABLE IF NOT EXISTS ServiceVirtualization.LogMessages (
id varchar PRIMARY KEY,
message text
);
CREATE TABLE IF NOT EXISTS ServiceVirtualization.LastResourcesTransactions (
id uuid PRIMARY KEY,
service varchar,
resource varchar,
mocking int,
recording int,
transparent int,
transaction_date date
);

CREATE TABLE IF NOT EXISTS ServiceVirtualization.LastResponses (
id uuid PRIMARY KEY,
service varchar,
resource varchar,
accepted int,
rejected int,
not_validated int,
transaction_date date
);

-- **************** INSERTIONS ****************
-- LastResourcesTransactions inserts
INSERT INTO LastResourcesTransactions (id, service, resource, mocking, recording, transparent, transaction_date)
VALUES (uuid(), 'dbdf04a8-73b9-42da-b4fd-b96ea09d0884', 'e0bfdad3-32a7-40c8-bcaf-ab9560540414', 10, 3, 6, '2024-09-25');

INSERT INTO LastResourcesTransactions (id, service, resource, mocking, recording, transparent, transaction_date)
VALUES (uuid(), 'dbdf04a8-73b9-42da-b4fd-b96ea09d0884', '5e901d83-0605-4b31-b9d2-b3c7b2f9a725', 1, 3, 2, '2024-09-25');

INSERT INTO LastResourcesTransactions (id, service, resource, mocking, recording, transparent, transaction_date)
VALUES (uuid(), 'dbdf04a8-73b9-42da-b4fd-b96ea09d0884', '38008d8c-7824-4669-98b2-2e1ff00e38ce', 4, 7, 1, '2024-09-25');

INSERT INTO LastResourcesTransactions (id, service, resource, mocking, recording, transparent, transaction_date)
VALUES (uuid(), 'dbdf04a8-73b9-42da-b4fd-b96ea09d0884', '5bfe1282-2fc0-4e2f-bd24-88916a70bfc2', 9, 12, 10, '2024-09-25');

-- Request insrets
INSERT INTO ServiceVirtualization.Request 
(id, service, resource, method, date_created, last_update, last_access) 
VALUES (uuid(), 'solera-titling-ui-deals.tkg-crm-qae.usdc01.solera.farm', 
'StateTrans/Finalize', 'POST', 
toTimestamp(now()), toTimestamp(now()), toTimestamp(now()));

-- Logs inserts
INSERT INTO logs(id, date_created, message, affected, user, is_error)
VALUES (uuid(), toTimestamp(now()), 'DSR, EDB', '3bb64298-f36b-4d46-8fc7-ec6df3c020ec', 'mones17', True); 

-- Service inserts
INSERT INTO ServiceVirtualization.Service 
(id, host, name, region, portfolio, port, actual_ip, date_created, last_update, last_access) 
VALUES (uuid(), 'solera-titling-ui-deals.tkg-crm-qae.usdc01.solera.farm', 'TitleTec PA', 'North America', 'Vehicle Solutions', '443', '10.132.76.16', 
toTimestamp(now()), toTimestamp(now()), toTimestamp(now())); 

-- Response inserts
INSERT INTO ServiceVirtualization.Response 
(id, request_id, status_code, headers, payload, is_valid, date_created, last_update, last_access) 
VALUES (uuid(), 'ab92314c-fce6-4711-bf06-e2777b38fd4f', '200', '{ "Host": "example.com", "Content-Type": "application/json", "Authorization": "Bearer your_token", "User-Agent": "YourUserAgent", "Accept": "application/json" }', '{ "PlateType": "Transfer"}', false, 
toTimestamp(now()), toTimestamp(now()), toTimestamp(now()));

INSERT INTO ServiceVirtualization.Response
(id, request_id, status_code, headers, payload, is_valid, date_created, last_update, last_access)
VALUES (uuid(), 'ab92314c-fce6-4711-bf06-e2777b38fd4f', '200', '{ "Host": "example.com", "Content-Type": "application
/json", "Authorization
": "Bearer')

-- User inserts (Password- Testing1234*)
INSERT INTO ServiceVirtualization.User
(id, email, role, name, password, date_created, last_update, last_access)
VALUES (uuid(), 'test.user@test.com', 'admin', 'Test User', '$2a$12$Z9hO2WDBS9XBOk9K1y6GW.zUz07.bpTa/1w2Hn2vi.wfbvKQAlh/W', toTimestamp(now()), toTimestamp(now()), toTimestamp(now()));

INSERT INTO ServiceVirtualization.User
(id, email, role, name, password, date_created, last_update, last_access)
VALUES (uuid(), 'test2.user@test.com', 'user', 'Test User2', '$2a$12$Z9hO2WDBS9XBOk9K1y6GW.zUz07.bpTa/1w2Hn2vi.wfbvKQAlh/W', toTimestamp(now()), toTimestamp(now()), toTimestamp(now()));

INSERT INTO ServiceVirtualization.User
(id, email, role, name, password, date_created, last_update, last_access)
VALUES (uuid(), 'luis.banderas@solera.com', 'admin', 'luis.banderas', '$2b$12$l74O9iZwDb.DXbKkBuGA9.2IazyDdGX80wwWTyoAOh8lAsNcjKxMK', toTimestamp(now()), toTimestamp(now()), toTimestamp(now()));

-- LogMessages inserts
INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('ACR', 'Accept Response');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('RJR', 'Reject Response');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('ART', 'Add Route');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('ASR', 'Add Service');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('ESR', 'Edit Service');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('ERT', 'Edit Route');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('DSR', 'Delete Service');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('DRT', 'Delete Route');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('ACM', 'Add Comment');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('CAMT', 'Change API Mode to Transparent');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('CAMR', 'Change API Mode to Recording');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('CAMM', 'Change API Mode to Mocking');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('DRS', 'Delete Response');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('ENX', 'Action Failed on NGINX');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('EDB', 'Action Failed on DataBase');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('GRS', 'Get Responses');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('GRT', 'Get Requests');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('GPL', 'Get Product List');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('UAMT', 'Usage API Mode Transparent');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('UAMR', 'Usage API Mode Recording');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('UAMM', 'Usage API Mode Mocking');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('STA', 'Set Traffic Analyzer');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('ERS', 'Edit Response');

INSERT INTO ServiceVirtualization.LogMessages
(id, message) 
VALUES ('ARS', 'Add Response');

-- **************** UPDATES ****************
ALTER TABLE Request ADD api_mode text DEFAULT '0';
ALTER TABLE service ADD name text;
ALTER TABLE response ADD request_payload text;
ALTER TABLE Response ADD time_taken int;
ALTER TABLE Request ADD time_saved int;
ALTER TABLE service ADD is_trafficAnalyzer boolean;
ALTER TABLE service DROP is_recorlysis;
ALTER TABLE request ADD is_recorded boolean;
ALTER TABLE service ADD portfolio varchar;
ALTER TABLE service ADD region varchar;

ALTER TABLE logs ADD level_affected text;
ALTER TABLE logs ADD service_id text;
ALTER TABLE logs ADD request_id text;
ALTER TABLE logs ADD response_id text;
ALTER TABLE service ADD host_name varchar;


-- **************** SOME QUERIES EXAMPLES ****************
-- GET ALL Resources from an specific service 
SELECT resource FROM Request WHERE service = 'solera-titling-ui-deals.tkg-crm-qae.usdc01.solera.farm' ALLOW FILTERING;

SELECT payload, status_code, id FROM Response WHERE request_id='ec3c03ae-ad0a-40e5-922e-28b8ac64af94' AND is_valid=true ALLOW FILTERING

DELETE from Response where is_valid=false
UPDATE Response SET is_valid = true, last_update = toTimestamp(now()) WHERE id = '46cff7f1-ed7e-4b0e-8896-2048b3c1655b' IF EXISTS;
DELETE FROM logmessages WHERE id = 'SAR' IF EXISTS;

-- Insert into lastResourcesTransactions example:
INSERT INTO LastResourcesTransactions (id, service, resource, mocking, recording, transparent, transaction_date)
VALUES (uuid(), 'solera-titling-ui-deals.tkg-crm-qae.usdc01.solera.farm', 'StateTrans/Finalize', 0, 1, 0, '2024-09-03');