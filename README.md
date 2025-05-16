# Terraform Playground: API -> SNS -> SQS -> Lambda

This is a little "toy project" I put together to mess around with various AWS services (all simulated with LocalStack, of course) and to get my hands dirty with Terraform in a slightly more involved setup. The main idea was to practice the message flow from an API endpoint through to a set of Lambda functions, using SNS and SQS as the intermediaries.


## What's This All About? The Architecture

I've set up a fairly common event-driven data flow:

1.  **API Endpoint (FastAPI):**
    *   A simple API built with FastAPI. This API would receive `POST` requests carrying some sort of data ("new order placed" event).

2.  **Publishing to SNS:**
    *   Once the API (or any other publisher) gets an event, it publishes it to an **SNS topic**.
    *   SNS acts as a message dispatcher.

3.  **Fan-Out to SQS Queues (Simple Queue Service):**
    *   We have several SQS queues subscribed to that SNS topic (this is the "fan-out" pattern).
    *   This means every message published to the SNS topic gets a copy sent to *each* of the subscribed SQS queues.
    *   This is super handy because different downstream services can react to the same event in different ways, without the original publisher needing to know anything about them.

4.  **Triggering Lambda Functions:**
    *   Each SQS queue has a Lambda function associated with it.
    *   When a message arrives in an SQS queue, AWS automatically invokes the corresponding Lambda, passing the message as an event.
    *   Each Lambda can then process the message independently.

**Quick Conceptual Diagram:**

```mermaid

graph TD
    A[Client/API POST <br/> (FastAPI - Future)] --> B(SNS Topic <br/> "ImportantEvents");
    B --> C1[SQS Queue <br/> "ProcessOrder"];
    B --> C2[SQS Queue <br/> "SendNotification"];
    C1 --> D1[Lambda <br/> "OrderProcessor"];
    C2 --> D2[Lambda <br/> "UserNotification"];

    subgraph "Event Source"
        A
    end

    subgraph "Messaging & Dispatch"
        B
    end

    subgraph "Queueing & Decoupling"
        C1
        C2
    end

    subgraph "Processing Logic"
        D1
        D2
    end
```


## Infrastructure as Code with Terraform

All of this architecture – the SNS topic, the SQS queues, the Lambda functions, the necessary IAM roles, and the subscriptions/mappings between them – is defined using **Terraform**.

This is awesome because:
*   I can spin up and tear down the entire setup with a couple of commands.
*   The infrastructure definition is versioned right alongside the application code.
*   It's easy to replicate the environment or make changes in a controlled way.

You'll find the Terraform files in the `ops/terraform` directory.

## What's In Here (and What's Missing)?

*   ✅ **Terraform for SNS, SQS, Lambdas, IAM Roles:** The core infrastructure is defined.
*   ✅ **Sample Lambda Functions (Python):** Basic Python handlers are in place to demonstrate them being triggered and processing messages.
*   ✅ **LocalStack Setup (Docker Compose):** Configuration to run LocalStack easily.
*   ✅ **FastAPI Endpoint:** As mentioned, this is a planned addition to make the "front door" of the system more concrete.
*   🚧 **CI/CD with Drone CI:** I've also been playing with setting up a Drone CI pipeline to automatically `terraform apply` changes on push. (You might see a `.drone.yml` file if I've started that bit!)

## Getting Started

1.  **Prerequisites:**
    *   Docker & Docker Compose
    *   Terraform CLI
    *   AWS CLI (configured for LocalStack, e.g., with a profile using `http://localhost:4566` as the endpoint URL)
2.  **Spin up LocalStack:**
    Make sure your `docker-compose.yml` for LocalStack is configured (especially the `SERVICES` environment variable to include `sns`, `sqs`, `lambda`, `iam`).
    
3.  **Deploy Infrastructure:**
    Navigate to the `/terraform` directory (or wherever your Terraform files are):
    ```bash
    cd terraform
    terraform init
    terraform plan
    terraform apply --auto-approve
    ```
4.  **Test it out:**
    *   Star fastapi service in src/main/main.py with `uv run python -m src.main.main` and post a message with swagger.

    *   Check the LocalStack logs (`docker logs <your_localstack_container_name>`) to see the Lambdas being invoked and processing the messages.