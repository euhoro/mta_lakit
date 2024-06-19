# MTA_Lakit Asynchronous FastAPI ATM Service

## Overview

This project is an asynchronous ATM service built with FastAPI. It handles ATM operations such as withdrawing money, refilling money, and checking the inventory. The inventory state is stored in Redis for production and in a JSON file for local testing.

## Features

- Withdraw money
- Refill money
- Check inventory
- Get total amount
- Maintenance mode

## Setup

### Prerequisites

- Python 3.10
- Redis (for production)
- Docker (optional, for running with Docker)
 
## Quick Setup - Installation and Run

### On Mac with python3.10

1. Make the setup script executable and run it 
( python3.10 should be installed and in %PATH% ):
    ```bash
    git clone https://github.com/euhoro/mta_lakit.git
    cd mta_lakit
    chmod +x setup_and_run.sh
    ./setup_and_run.sh
    ```

2. Access the application:
   - [API Documentation](http://127.0.0.1:8000/docs)
   - [Home](http://127.0.0.1:8000)
   
## Detailed Setup

1. Create a virtual environment:
    ```bash
    python3.10 -m venv venv
    ```

2. Activate the virtual environment:
    ```bash
   source venv/bin/activate
   
3. Install requirements`:
    ```bash
   pip install -r requirements.txt   
   
4. Running redis locally`:
    ```bash
   docker run --name redis -d -p 6379:6379 redis 
   
3. Run App`:
    ```bash
   uvicorn main:app --reload
   
# alternative 1:

# Run with Redis

1. Run the app`:
    ```bash
   SETTINGS_MODE=redis docker-compose up --build
   
2. Run to reload a full ATM`:
    ```bash
   curl -L -g -X GET 'http://127.0.0.1:8000/atm/maintenance'

3. Access the application:
   - [API Documentation](http://127.0.0.1:8000/docs)
   - [Home](http://127.0.0.1:8000)

# alternative 2:
# Run with JSON file (for testing only - no real lock )
1. Run the app`:
    ```bash
   SETTINGS_MODE=text docker-compose up --build



### Testing

#### Locally

1. Set the environment variable:
    ```sh
    export SETTINGS_MODE=text
    ```

2. Start the app:
    ```sh
    uvicorn main:app --host 127.0.0.1 --port 8000 &
    ```

3. Run the tests:
    ```sh
    pytest --cov=./ --cov-report=xml
    ```
   
4. Stop the app:
    ```sh
    pkill -f "uvicorn main:app"
    ```


## TODOs

- Create 2 modules app and core
- Optimize Logic Structure
- Achieve 95% Test Coverage
- Split tests to short (text) and long (redis)
- Integrate the stress test


## Contributing

Feel free to fork the repository and make contributions. Pull requests are welcome.

## License

This project is licensed under the MIT License.
