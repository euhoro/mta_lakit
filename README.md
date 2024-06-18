# MTA_Lakit

## Quick Setup

### On Mac

1. Make the setup script executable and run it:
    ```bash
    chmod +x setup_and_run.sh
    ./setup_and_run.sh
    ```

2. Access the application:
    - [Home](http://127.0.0.1:8000)
    - [API Documentation](http://127.0.0.1:8000/docs)

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
   
# alternative:

# Run with Redis
SETTINGS_MODE=redis docker-compose up --build

# Run with JSON file (for testing only - no real lock )
SETTINGS_MODE=text docker-compose up --build
