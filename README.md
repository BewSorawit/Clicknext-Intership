# Backend
Assuming that you are a backend engineer on an AI team, our client has requested a Proof-of-Concept (POC) for a face detection system. This system should be able to receive vidoeo input from the client application, send the images to the server for detect face, and store the results in a database. Fortunately, we already have a face detection engine and client sample application. Your task is to develop a backend application based on the following requirements

![diagram](https://gitlab.com/clicknext-ai/technical-test/backend/-/raw/main/doc/backend_technical_test.jpg)

### Test#1 backend service
Please develop a backend service using your preferred framework that meets the following requirements.

[USER]
- Able to register the new user and contains user_name, email, password, and api_request_qauota (default is 100)
- Able to login with registered user account
- Using JWT with refresh token
- Provide api request token for the client

[FACE]
- The client able to send request image to the backend and forward to FACE_SERVICE to perform face detection
- Able to store the face detected result to the database
- Check if the api request qauota is not over the limit 
- Able to query the results that belong to the user which these conditions
  - All result
  - From time to time
  - Specific id

[NOTE]
- FACE_SERVICE api is synchronous mode
- Need to modify face_client to add more required information such as token or ssl key files

### Test#2 Extra point (Optional)
- Provide docker file for backend service
- Provide docker file for face_engine service
- Provide docker compose for all services
- Check if the api request is not over the rate limit (10 request per second)
- Apply message queue such as Redis, Kafka, RabbitMQ
- Apply TSL/SSL for secure data transfer between client and server
- Simple frontend web application
- Modify face_client to read video file instead of image file
- API document
- Using FastAPI
- Document and diagram
- Strutured directory

### Output
- Video demo
- Source code