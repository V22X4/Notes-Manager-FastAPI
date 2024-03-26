# Note Manager FastAPI

## Overview

This project implements a secure and scalable RESTful API using FastAPI, allowing users to manage notes. Users can perform CRUD operations (Create, Read, Update, Delete) on their notes, share notes with other users, and search for notes based on keywords. The API also includes authentication endpoints for user signup and login.

## Features

- **Authentication**: Users can create a new account (`POST /api/auth/signup`) or log in to an existing account (`POST /api/auth/login`) to receive an access token.
- **Note Management**: Users can perform CRUD operations on their notes, including creating (`POST /api/notes`), reading (`GET /api/notes` and `GET /api/notes/{id}`), updating (`PUT /api/notes/{id}`), and deleting (`DELETE /api/notes/{id}`) notes.
- **Note Sharing**: Users can share a note with another user (`POST /api/notes/{id}/share`).
- **Search Functionality**: Users can search for notes based on keywords using the `GET /api/search?q={query}` endpoint.

## Technical Details

- **Framework**: FastAPI
- **Database**: MongoDB
- **Authentication**: JWT, OAuth2PasswordBearer
- **Testing**: Unit tests and integration tests using pytest

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/V22X4/Notes-Manager-FastAPI.git
   ```

2. Install dependencies:

   ```bash
   cd Notes-Manager-FastAPI
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   uvicorn main:app --reload
   ```

4. Access the API at `http://localhost:8000`.

## Testing

Run tests:

   ```bash
   python tests.py
   ```

## API Documentation

The API documentation (Swagger UI) can be accessed at `http://localhost:8000/docs`.
