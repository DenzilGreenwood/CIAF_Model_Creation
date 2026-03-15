"""
Backend Unit Tests - API Endpoints
Tests for FastAPI verification endpoints
"""
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional


# ========== MOCK API MODELS ==========

class VerificationRequest(BaseModel):
    content: str
    model_version: str
    output_type: str


class VerificationResponse(BaseModel):
    proof_id: str
    status: str
    content_hash: str
    verification_timestamp: str


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str


# ========== MOCK API APPLICATION ==========

app = FastAPI()

# In-memory storage for tests
proofs_store = {}


@app.post("/verify", response_model=VerificationResponse)
async def submit_verification(request: VerificationRequest):
    """Submit output for verification"""
    import hashlib
    from datetime import datetime

    content_hash = hashlib.sha256(request.content.encode()).hexdigest()
    proof_id = f"proof_{len(proofs_store) + 1}"

    proof = {
        "id": proof_id,
        "content_hash": content_hash,
        "status": "verified",
        "timestamp": datetime.utcnow().isoformat(),
        "content": request.content
    }
    proofs_store[proof_id] = proof

    return VerificationResponse(
        proof_id=proof_id,
        status="verified",
        content_hash=content_hash,
        verification_timestamp=datetime.utcnow().isoformat()
    )


@app.get("/verify/{proof_id}", response_model=VerificationResponse)
async def get_verification(proof_id: str):
    """Retrieve verification proof"""
    if proof_id not in proofs_store:
        raise HTTPException(status_code=404, detail="Proof not found")

    proof = proofs_store[proof_id]
    from datetime import datetime
    return VerificationResponse(
        proof_id=proof_id,
        status=proof["status"],
        content_hash=proof["content_hash"],
        verification_timestamp=proof["timestamp"]
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        database="connected"
    )


@app.post("/auth/login")
async def login(email: str, password: str):
    """Mock login endpoint"""
    if email == "demo@ciaf.io" and password == "ValidPass123!":
        return {
            "access_token": "token_xyz",
            "token_type": "bearer",
            "user": {
                "id": "user123",
                "email": "demo@ciaf.io",
                "role": "analyst"
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/auth/logout")
async def logout():
    """Mock logout endpoint"""
    return {"status": "success", "message": "Logged out"}


# ========== TESTS ==========

@pytest.fixture
def client():
    """Create test client"""
    proofs_store.clear()  # Reset before each test
    return TestClient(app)


class TestVerificationEndpoint:
    """Test verification submission endpoint"""

    def test_submit_verification_returns_200(self, client):
        response = client.post(
            "/verify",
            json={
                "content": "Model output",
                "model_version": "1.0.0",
                "output_type": "classification"
            }
        )
        assert response.status_code == 200

    def test_submit_verification_returns_proof_id(self, client):
        response = client.post(
            "/verify",
            json={
                "content": "Test output",
                "model_version": "1.0.0",
                "output_type": "classification"
            }
        )
        data = response.json()
        assert "proof_id" in data
        assert data["proof_id"].startswith("proof_")

    def test_submit_verification_returns_content_hash(self, client):
        response = client.post(
            "/verify",
            json={
                "content": "Test output",
                "model_version": "1.0.0",
                "output_type": "classification"
            }
        )
        data = response.json()
        assert "content_hash" in data
        assert len(data["content_hash"]) == 64  # SHA-256 hash length

    def test_submit_verification_returns_status(self, client):
        response = client.post(
            "/verify",
            json={
                "content": "Test output",
                "model_version": "1.0.0",
                "output_type": "classification"
            }
        )
        data = response.json()
        assert data["status"] == "verified"

    def test_submit_verification_with_missing_field_fails(self, client):
        response = client.post(
            "/verify",
            json={
                "content": "Test output"
                # Missing required fields
            }
        )
        assert response.status_code == 422  # Validation error


class TestGetVerificationEndpoint:
    """Test proof retrieval endpoint"""

    def test_get_verification_returns_stored_proof(self, client):
        # First, submit verification
        submit_response = client.post(
            "/verify",
            json={
                "content": "Test output",
                "model_version": "1.0.0",
                "output_type": "classification"
            }
        )
        proof_id = submit_response.json()["proof_id"]

        # Then retrieve it
        get_response = client.get(f"/verify/{proof_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["proof_id"] == proof_id

    def test_get_nonexistent_verification_returns_404(self, client):
        response = client.get("/verify/nonexistent_id")
        assert response.status_code == 404

    def test_get_verification_preserves_content_hash(self, client):
        # Submit
        submit_response = client.post(
            "/verify",
            json={
                "content": "Specific content",
                "model_version": "1.0.0",
                "output_type": "classification"
            }
        )
        submitted_hash = submit_response.json()["content_hash"]
        proof_id = submit_response.json()["proof_id"]

        # Retrieve and verify hash is unchanged
        get_response = client.get(f"/verify/{proof_id}")
        retrieved_hash = get_response.json()["content_hash"]
        assert submitted_hash == retrieved_hash


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_includes_version(self, client):
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert data["version"] is not None

    def test_health_check_includes_database_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert "database" in data


class TestAuthenticationEndpoints:
    """Test authentication endpoints"""

    def test_login_with_valid_credentials(self, client):
        response = client.post(
            "/auth/login",
            params={
                "email": "demo@ciaf.io",
                "password": "ValidPass123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_returns_user_info(self, client):
        response = client.post(
            "/auth/login",
            params={
                "email": "demo@ciaf.io",
                "password": "ValidPass123!"
            }
        )
        data = response.json()
        user = data["user"]
        assert user["email"] == "demo@ciaf.io"
        assert user["role"] == "analyst"

    def test_login_with_invalid_credentials(self, client):
        response = client.post(
            "/auth/login",
            params={
                "email": "demo@ciaf.io",
                "password": "WrongPassword"
            }
        )
        assert response.status_code == 401

    def test_logout_returns_success(self, client):
        response = client.post("/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestAPIErrorHandling:
    """Test API error handling"""

    def test_invalid_endpoint_returns_404(self, client):
        response = client.get("/invalid/endpoint")
        assert response.status_code == 404

    def test_invalid_method_returns_405(self, client):
        response = client.put("/verify")  # POST only
        assert response.status_code == 405

    def test_malformed_json_returns_422(self, client):
        response = client.post(
            "/verify",
            json={"invalid": "structure"}
        )
        assert response.status_code == 422


class TestAPIResponseFormats:
    """Test API response consistency"""

    def test_verification_response_has_required_fields(self, client):
        response = client.post(
            "/verify",
            json={
                "content": "Test",
                "model_version": "1.0.0",
                "output_type": "classification"
            }
        )
        data = response.json()
        required_fields = ["proof_id", "status", "content_hash", "verification_timestamp"]
        for field in required_fields:
            assert field in data

    def test_health_response_has_required_fields(self, client):
        response = client.get("/health")
        data = response.json()
        required_fields = ["status", "version", "database"]
        for field in required_fields:
            assert field in data


# ========== RUNS WITH: pytest tests/test_api.py ==========
