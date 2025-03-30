"""Erasumus Genetic Programming - Public Key Repository API"""

from datetime import datetime, timedelta, timezone

import models
from fastapi import FastAPI, HTTPException, status

# --- Application Setup ---

# Create the FastAPI application instance
# Add title and version for documentation purposes
app = FastAPI(
    title="EGPPKR API",
    description="Erasmus Genetic Programming - Public Key Repository API",
    version="1.0.0",
)

# --- API Endpoints ---

# Define a prefix for all API routes for better organization (optional but good practice)
API_PREFIX = "/api/v1"


@app.get(
    f"{API_PREFIX}/keys/{{app_uuid}}",
    response_model=list[models.KeyInfoResponse],
    summary="Get Keys for Application UUID",
    tags=["Keys"],  # Tag for grouping in API docs
)
async def get_keys(app_uuid: str) -> list[models.KeyInfoResponse]:
    """
    Retrieves all registered public keys (and their status) associated
    with a specific Application UUID.

    **(Phase 1 Placeholder): Returns dummy data for 'test-uuid-123', otherwise 404.**
    """
    print(f"Received request to get keys for UUID: {app_uuid}")  # Basic logging
    # --- Placeholder Logic ---
    if app_uuid == "test-uuid-123":
        # Simulate finding keys for this specific UUID
        dummy_key_list: list[models.KeyInfoResponse] = [
            models.KeyInfoResponse(
                publicKeyPem="-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAExgMP/03XMO0tHdDmy7nOSkQQ\nNOCwfisG949F/VICnVss3mQV8vZDojDbqjXy1ZGeh2IQ+wi9ZiJRaFvN91k5Vg==\n-----END PUBLIC KEY-----\n",
                status="Active",
                statusTimestamp=datetime.now(timezone.utc),  # Use timezone-aware UTC time
            ),
            models.KeyInfoResponse(
                publicKeyPem="-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEfWZ4XiKVObhyrdlL0FpkN9p9\nlx7T7A+P8a9zZ4E9n7kv8v6sT5yF+M+qG+J/3rX0sD/lP5aH3jI6bZ7R8zXqWw==\n-----END PUBLIC KEY-----\n",
                status="Deprecated",
                statusTimestamp=datetime.now(timezone.utc)
                - timedelta(days=10),  # Example past timestamp
            ),
        ]
        return dummy_key_list
    else:
        # Simulate UUID not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application UUID '{app_uuid}' not found.",
        )
    # --- End Placeholder Logic ---


@app.post(
    f"{API_PREFIX}/keys",
    response_model=models.KeyInfoResponse,
    status_code=status.HTTP_201_CREATED,  # Standard code for successful resource creation
    summary="Register First Key for Application UUID",
    tags=["Keys"],
)
async def register_first_key(registration_info: models.ApplicationRegistrationRequest):
    """
    Registers the very first key for a new `applicationUuid` and links it
    to the (future) authenticated caller's Google User ID.

    **(Phase 1 Placeholder): Accepts data, prints it, and returns a simulated response.**
    """
    # FastAPI automatically validates incoming 'registration_info' against the Pydantic model.
    print(f"Received request to register first key for UUID: {registration_info.applicationUuid}")
    print(f"Public Key PEM received:\n{registration_info.publicKeyPem}")

    # --- Placeholder Logic ---
    # In Phase 2, we'll check if UUID exists and save to Firestore.
    # For now, just simulate success and return data based on the input.
    response_data = models.KeyInfoResponse(
        publicKeyPem=registration_info.publicKeyPem,
        status="Active",  # Newly registered key is always Active
        statusTimestamp=datetime.now(timezone.utc),
    )
    return response_data
    # --- End Placeholder Logic ---


@app.post(
    f"{API_PREFIX}/keys/{{app_uuid}}/add",
    response_model=models.KeyInfoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add New Active Key",
    tags=["Keys"],
)
async def add_key(app_uuid: str, key_to_add: models.KeyInfoCreate):
    """
    Adds a new key as "Active" for an *existing* `applicationUuid`.
    Requires the caller to be authenticated and own the `app_uuid`.
    Fails if another key is already active or limits exceeded (checks in later phases).

    **(Phase 1 Placeholder): Accepts data, prints it, and returns a simulated response.**
    """
    print(f"Received request to add key for existing UUID: {app_uuid}")
    print(f"New Public Key PEM received:\n{key_to_add.publicKeyPem}")

    # --- Placeholder Logic ---
    # In Phase 3, we'll add checks: ownership, no active key exists, limits.
    # For now, simulate success.
    response_data = models.KeyInfoResponse(
        publicKeyPem=key_to_add.publicKeyPem,
        status="Active",  # Newly added key becomes Active
        statusTimestamp=datetime.now(timezone.utc),
    )
    return response_data
    # --- End Placeholder Logic ---


@app.post(
    f"{API_PREFIX}/keys/{{app_uuid}}/update",
    response_model=models.KeyInfoResponse,
    status_code=status.HTTP_200_OK,  # Standard code for successful update
    summary="Update Key Status",
    tags=["Keys"],
)
async def update_key_status(app_uuid: str, update_info: models.KeyInfoStatusUpdate):
    """
    Updates the status of a specific existing key to "Deprecated" or "Compromised".
    Requires the caller to be authenticated and own the `app_uuid`.

    **(Phase 1 Placeholder): Accepts data, prints it, and returns a simulated response.**
    """
    print(f"Received request to update key status for UUID: {app_uuid}")
    print(f"Key PEM to update:\n{update_info.publicKeyPemToUpdate}")
    print(f"New desired status: {update_info.newStatus}")

    # --- Placeholder Logic ---
    # In Phase 3, we'll add checks: ownership, find the actual key.
    # For now, simulate success, returning the key PEM provided with the new status.
    response_data = models.KeyInfoResponse(
        publicKeyPem=update_info.publicKeyPemToUpdate,  # Return the key that was updated
        status=update_info.newStatus,  # Reflect the new status
        statusTimestamp=datetime.now(timezone.utc),  # Reflect update time
    )
    return response_data
    # --- End Placeholder Logic ---


# --- Root Endpoint (Optional) ---
@app.get("/", include_in_schema=False)  # Basic check endpoint, excluded from OpenAPI docs
async def read_root():
    return {"message": "EGPPKR API is running!"}
