# Asynchronous FastAPI ATM Service

## Overview

This document outlines the design and architecture of the asynchronous FastAPI ATM service. The service handles ATM operations such as withdrawing money, refilling money, and checking the inventory. The inventory state is stored in Redis for production and in a JSON file for local testing.

## Components

### 1. FastAPI Application

- **Endpoints**:
  - `/atm/withdrawal`: Withdraws a specified amount from the ATM.
  - `/atm/refill`: Refills the ATM with specified bills and coins.
  - `/atm/inventory`: Retrieves the current inventory of the ATM.
  - `/atm/total`: Retrieves the total amount of money in the ATM.
  - `/atm/maintenance`: Resets the ATM to its initial state.

### 2. Inventory Services

- **RedisInventoryService**: Manages the ATM inventory using Redis.
- **JSONFileInventoryService**: Manages the ATM inventory using a JSON file for local testing.

### 3. ATMService

- Handles business logic for ATM operations and interacts with the inventory services.

## Architecture

### FastAPI Application Architecture

```mermaid
graph TD;
    A[FastAPI Application] --> B[ATMService];
    B[ATMService] --> C[RedisInventoryService];
    B[ATMService] --> D[JSONFileInventoryService];
    C[RedisInventoryService] --> E[Redis Database];
    D[JSONFileInventoryService] --> F[JSON File];

sequenceDiagram
    participant User
    participant FastAPI
    participant ATMService
    participant InventoryService

    User->>FastAPI: POST /atm/withdrawal
    FastAPI->>ATMService: withdraw_money(amount)
    ATMService->>InventoryService: acquire_lock()
    InventoryService-->>ATMService: lock_acquired
    ATMService->>InventoryService: read_inventory()
    InventoryService-->>ATMService: inventory_data
    ATMService->>InventoryService: write_inventory(updated_inventory)
    ATMService->>InventoryService: release_lock()
    ATMService-->>FastAPI: withdrawal_result
    FastAPI-->>User: withdrawal_result

sequenceDiagram
    participant User
    participant FastAPI
    participant ATMService
    participant InventoryService

    User->>FastAPI: POST /atm/refill
    FastAPI->>ATMService: refill_money(money)
    ATMService->>InventoryService: acquire_lock()
    InventoryService-->>ATMService: lock_acquired
    ATMService->>InventoryService: read_inventory()
    InventoryService-->>ATMService: inventory_data
    ATMService->>InventoryService: write_inventory(updated_inventory)
    ATMService->>InventoryService: release_lock()
    ATMService-->>FastAPI: refill_result
    FastAPI-->>User: refill_result

