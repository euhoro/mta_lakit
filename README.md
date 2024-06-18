# MTA_Lakit

## Quick Setup

### On Mac with python3.10

1. Make the setup script executable and run it 
( python3.10 should be installed and in %PATH% ):
    ```bash
   
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
docker-compose up --build

3. Run to reload a full ATM`:
    ```bash
   curl -L -g -X GET 'http://127.0.0.1:8000/atm/maintenance'


2. Access the application:
   - [API Documentation](http://127.0.0.1:8000/docs)
   - [Home](http://127.0.0.1:8000)

# alternative 2:

# Run with JSON file (for testing only - no real lock )
SETTINGS_MODE=text docker-compose up --build
