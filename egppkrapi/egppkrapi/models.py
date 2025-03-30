"""Models for the EGPPKRA API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# --- Core Key Information ---


class KeyInfoBase(BaseModel):
    """
    Base model containing the core information for a public key.
    Other models will inherit from this.
    """

    publicKeyPem: str = Field(
        ...,  # The '...' means this field is required
        description="The public key in standard PEM format (e.g., -----BEGIN PUBLIC KEY-----...).",
        # Example added for clarity in docs
        # example="-----BEGIN PUBLIC KEY-----\nMFkwEwYHoZIzj0DAQcDQgAE...\n-----END PUBLIC KEY-----"
    )


# --- Models for API Requests (Input) ---


class ApplicationRegistrationRequest(BaseModel):
    """
    Data required when registering the very first key for a new application UUID.
    Used as the request body for POST /api/v1/keys
    """

    applicationUuid: str = Field(..., description="The application-specific UUID being registered.")
    publicKeyPem: str = Field(..., description="The initial public key in PEM format.")


class KeyInfoCreate(KeyInfoBase):
    """
    Data required when adding a new key to an existing application UUID.
    Used as the request body for POST /api/v1/keys/{app_uuid}/add
    Inherits publicKeyPem from KeyInfoBase.
    """

    # No additional fields needed beyond the base key info for now


class KeyInfoStatusUpdate(BaseModel):
    """
    Data required to update the status of an existing key.
    Used as the request body for POST /api/v1/keys/{app_uuid}/update
    """

    publicKeyPemToUpdate: str = Field(
        ..., description="The exact PEM string of the public key whose status needs updating."
    )
    newStatus: Literal["Deprecated", "Compromised"] = Field(
        ..., description="The new status for the key (must be 'Deprecated' or 'Compromised')."
    )


# --- Models for API Responses (Output) ---


class KeyInfoResponse(KeyInfoBase):
    """
    Represents the full information about a key returned by the API.
    Used as the response model for endpoints returning key details.
    Inherits publicKeyPem from KeyInfoBase.
    """

    status: Literal["Active", "Deprecated", "Compromised"] = Field(
        ..., description="Current status of the key."
    )
    statusTimestamp: datetime = Field(
        ..., description="Timestamp (UTC) when the current status was set."
    )
    # Optional: If you decide to store and return creation timestamp later
    # creationTimestamp: datetime = Field(..., description="Timestamp (UTC)
    # when the key was first added.")

    # Configuration for Pydantic V2 and later:
    # Tells Pydantic it can create this model from objects that have attributes
    # (like data read from Firestore), not just dictionaries.
    class Config:
        """
        Pydantic configuration for KeyInfoResponse.
        """

        from_attributes = True
        # For Pydantic V1 you would use:
        # orm_mode = True


class ErrorDetail(BaseModel):
    """
    Represents the full information about a key returned by the API.
    Used as the response model for endpoints returning key details.
    Inherits publicKeyPem from KeyInfoBase.
    """

    detail: str = Field(..., description="A detailed message explaining the error.")
