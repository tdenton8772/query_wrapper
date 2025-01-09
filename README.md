# Query Wrapper
The query_wrapper repository provides a Flask-based API layer for interacting with Apache Pinot, managing and executing SQL queries, validating tokens, and more. This document provides an overview of the repository, its APIs, and how to use them.

## Table of Contents
- [Features](#features)
- [Setup](#setup)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [APIs](#apis)
  - [List APIs](#list-apis)
  - [Execute Query](#execute-query)
  - [Pass-through Query](#pass-through-query)
  - [Token Validation](#token-validation)
  - [Create, Update, and Delete APIs](#create-update-and-delete-apis)
    - [Create API Configuration](#create-api-configuration)
    - [Update API Configuration](#update-api-configuration)
    - [Delete API Configuration](#delete-api-configuration)


## Features
- Manage and execute SQL queries dynamically.
- Reuse saved parameterized queries
- Standardize query syntax across all platforms
- Proxy SQL queries directly to Apache Pinot.
- Token-based authentication with caching for improved performance.
- Simple API to list, create, update, and delete query configurations.
- Flask session integration for token validation.

## Setup
### Prerequisites
- Python 3.8 or higher
- Apache Pinot running and accessible
- Redis for caching query configurations

### Installation
1. Clone the repository:

```bash
git clone https://github.com/tdenton8772/query_wrapper.git
cd query_wrapper
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your environment variables or edit the config.py file to include:

- `REDIS_CONFIG` (host, port, db)
- `PINOT_CONFIG` (broker, controller)

4. Run the Flask application:

```bash
flask run
```

## Configuration
Edit the config.py file to include the following:

```python
class Config:
    SECRET_KEY = "your_secret_key"  # For session management
    SESSION_TYPE = "filesystem"    # Use filesystem for session storage
    REDIS_CONFIG = {
        "host": "localhost",
        "port": 6379,
        "db": 0
    }
    PINOT_CONFIG = {
        "broker": "http://your-broker-url:8099",
        "controller": "http://your-controller-url:9000"
    }
```

## APIs
### List APIs
#### Endpoint
```http
GET /v1/execute/list
```

#### Description
Lists all API configurations stored in Redis.

#### Response
```json
{
    "success": true,
    "apis": [
        "samplequery",
        "anotherquery"
    ]
}
```

### Execute Query
#### Endpoint
```http
POST /v1/execute/api/<name>
```

```http
POST /v1/execute/version/<uuid>
```

#### Description
Executes a query based on the given API name or version UUID.

#### Request Body
```json
{
    "parameters": {
        "param_name": "value"
    }
}
```

#### Response
```json
{
    "success": true,
    "data": {
        "resultTable": {
            "dataSchema": {
                "columnNames": ["col1", "col2"],
                "columnDataTypes": ["STRING", "LONG"]
            },
            "rows": [
                ["value1", 123],
                ["value2", 456]
            ]
        },
        "exceptions": []
    }
}
```

### Pass-through Query
#### Endpoint
```http
POST /v1/query/
```

#### Description
Proxies a query directly to Apache Pinot.

#### Request Body
```json
{
    "sql": "SELECT * FROM my_table LIMIT 10"
}
```

#### Response
```json
{
    "success": true,
    "data": {
        "resultTable": {
            "dataSchema": {
                "columnNames": ["col1", "col2"],
                "columnDataTypes": ["STRING", "LONG"]
            },
            "rows": [
                ["value1", 123],
                ["value2", 456]
            ]
        },
        "exceptions": []
    }
}
```

### Token Validation
#### Description
Token validation is performed automatically for all APIs using a Bearer token. Tokens are validated against the Pinot /health endpoint and cached using Flask sessions.

## Create, Update, and Delete APIs
### Create API Configuration
#### Endpoint
```http
POST /v1/create/
```

#### Request Body

```json
{
    "name": "samplequery",
    "sql": "SELECT * FROM table WHERE %column% = %value%",
    "parameters": {
        "column": {"default": "fname", "type": "column"},
        "value": {"default": "schultz", "type": "string"}
    }
}
```

### Update API Configuration
#### Endpoint
```http
POST /v1/update/<name>
```

#### Request Body
```json
{
    "sql": "SELECT * FROM table WHERE %column% = %value%",
    "parameters": {
        "column": {"default": "lname", "type": "column"},
        "value": {"default": "denton", "type": "string"}
    }
}
```

#### Delete API Configuration
```http
DELETE /v1/delete/version/<uuid>
DELETE /v1/delete/api/<name>
```
