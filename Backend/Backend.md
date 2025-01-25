# Backend Interview Q

List of 3-phases interview questions


## Practical code

1. Print first 100 prime number

   - Objective: Assess algorithmic thinking and efficiency.
   - Skills Tested: Looping constructs, conditional logic, optimization.

   - I used the Sieve of Eratosthenes algorithm to get the first 100 prime numbers
   - take a look at the `prime.py` file


2. Implement a Rate Limiter for an API Endpoint

   -Description: Write a function that limits the number of requests a user can make to an API endpoint within a specific time frame (e.g., 100 requests per minute).

   - Skills Tested: Understanding of rate-limiting algorithms (e.g., Token Bucket, Leaky Bucket), data structures (e.g., sliding window), concurrency control.


3. Build a Pagination Function for Large Datasets
   - Description: Given a large list of items, implement a function that returns a specific page based on page number and page size, ensuring efficiency.
   - Skills Tested: List slicing, performance optimization, handling edge cases (e.g., last page with fewer items).



## Refactoring

1. refactor a function that config and conn to a PyMongo and then get customers collections to get all services

   - goal is to be able to use any DB (file, PSQL...etc)
   - take look at the `refactor_pymongo.py` file

2.



## System Design

1. Sys Design (REST API) for SaaS system that got following:

   - CRUD of the services & jobs

     - this need some horizontal scaling so some balance loading maybe even RabbitMQ (helpful also for the notif-ms)

   - Quantitative simulation that might takes hour

     - I followed the AppEngine design and talked about having WebSocket / SSE to notify users once it's done

   - notification once the user apply to a job goes bellow a certain performance

     - Notification-MS

   - only certain users can get certain services + users get sms 2fa + some users can create other users
     - IAM

2. Design a Real-Time Analytics Dashboard for Monitoring Application Metrics

   - Description: Create a system that ingests real-time data from various sources, processes and aggregates metrics, stores them efficiently, and presents them on a dashboard with real-time updates.
   - Considerations:
      - Data Ingestion: Use tools like Kafka or AWS Kinesis for handling high-throughput data streams.
      - Stream Processing: Implement stream processing frameworks (e.g., Apache Flink, Spark Streaming) for real-time data aggregation.
      - Storage Solutions: Choose appropriate databases (e.g., Time-Series DB like InfluxDB) for storing metrics.
      - Real-Time Visualization: Utilize WebSockets or SSE for live data feeds to the dashboard.
      - Scalability & Performance: Ensure the system can handle increasing data volumes without performance degradation.
      - Skills Tested: Real-time data processing, database selection, system scalability, data visualization, performance optimization.


3. Design a Real-Time Chat Application with Scalability and Reliability

   - Description: Create a chat system that supports real-time messaging, user presence, and scalability to millions of users.
   - Considerations:
      - Real-Time Communication: Use WebSockets for instant message delivery.
      - Message Storage: Implement persistent storage for chat history using databases like Cassandra or DynamoDB.
      - Scalability: Utilize load balancers and distribute WebSocket connections across multiple servers.
      - Reliability: Ensure message delivery guarantees (e.g., at-least-once delivery) and handle network partitions.
      - Security: Implement end-to-end encryption and authentication mechanisms.
      - Skills Tested: Real-time communication protocols, database selection, system scalability, reliability, security.
