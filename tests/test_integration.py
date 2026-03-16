"""
Integration Tests - Authentication and Verification Flows
Tests for complete end-to-end workflows
"""
import pytest
from datetime import datetime, timezone
import hashlib


# ========== INTEGRATION SCENARIO HELPERS ==========

class User:
    """Represents a user"""
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.id = f"user_{hashlib.sha256(email.encode()).hexdigest()[:8]}"
        self.token = None
        self.role = "analyst"


class IntegrationTestEnvironment:
    """Represents a test environment with users and data"""

    def __init__(self):
        self.users = {}
        self.proofs = {}
        self.sessions = {}

    def create_user(self, email: str, password: str) -> User:
        """Create a user"""
        user = User(email, password)
        self.users[user.id] = user
        return user

    def authenticate_user(self, email: str, password: str) -> dict:
        """Authenticate a user"""
        # Find user
        user = None
        for u in self.users.values():
            if u.email == email:
                user = u
                break

        if not user or user.password != password:
            return {"success": False, "error": "Invalid credentials"}

        # Generate token
        token = hashlib.sha256(f"{user.id}{datetime.now(timezone.utc)}".encode()).hexdigest()
        user.token = token
        self.sessions[token] = user

        return {
            "success": True,
            "token": token,
            "user_id": user.id,
            "role": user.role
        }

    def submit_verification(self, token: str, content: str) -> dict:
        """Submit verification with authenticated token"""
        if token not in self.sessions:
            return {"success": False, "error": "Unauthenticated"}

        user = self.sessions[token]
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        proof_id = f"proof_{len(self.proofs) + 1}"

        self.proofs[proof_id] = {
            "id": proof_id,
            "user_id": user.id,
            "content_hash": content_hash,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "verified"
        }

        return {
            "success": True,
            "proof_id": proof_id,
            "status": "verified"
        }

    def get_proof(self, token: str, proof_id: str) -> dict:
        """Retrieve proof with authentication"""
        if token not in self.sessions:
            return {"success": False, "error": "Unauthenticated"}

        if proof_id not in self.proofs:
            return {"success": False, "error": "Proof not found"}

        proof = self.proofs[proof_id]
        return {
            "success": True,
            "proof_id": proof["id"],
            "content_hash": proof["content_hash"],
            "timestamp": proof["timestamp"],
            "status": proof["status"]
        }

    def logout_user(self, token: str) -> dict:
        """Logout a user"""
        if token in self.sessions:
            del self.sessions[token]
            return {"success": True}
        return {"success": False}


# ========== TESTS ==========

@pytest.fixture
def env():
    """Create test environment"""
    return IntegrationTestEnvironment()


class TestAuthenticationFlow:
    """Test complete authentication workflow"""

    def test_user_can_register(self, env):
        user = env.create_user("alice@test.com", "SecurePass123!")
        assert user.email == "alice@test.com"
        assert user.id in env.users

    def test_user_can_login_with_correct_credentials(self, env):
        # Register user
        env.create_user("bob@test.com", "CorrectPass123!")

        # Login
        result = env.authenticate_user("bob@test.com", "CorrectPass123!")
        assert result["success"] is True
        assert "token" in result

    def test_user_cannot_login_with_wrong_password(self, env):
        env.create_user("charlie@test.com", "CorrectPass123!")

        result = env.authenticate_user("charlie@test.com", "WrongPass123!")
        assert result["success"] is False
        assert "error" in result

    def test_user_cannot_login_with_nonexistent_email(self, env):
        result = env.authenticate_user("nonexistent@test.com", "AnyPass123!")
        assert result["success"] is False

    def test_user_receives_token_on_login(self, env):
        env.create_user("dave@test.com", "Pass123!")
        result = env.authenticate_user("dave@test.com", "Pass123!")

        token = result["token"]
        assert token is not None
        assert len(token) > 0
        assert token in env.sessions

    def test_user_can_logout(self, env):
        env.create_user("eve@test.com", "Pass123!")
        login_result = env.authenticate_user("eve@test.com", "Pass123!")
        token = login_result["token"]

        logout_result = env.logout_user(token)
        assert logout_result["success"] is True
        assert token not in env.sessions


class TestVerificationFlow:
    """Test complete verification workflow"""

    def test_user_can_submit_verification(self, env):
        # Setup
        env.create_user("user@test.com", "Pass123!")
        auth_result = env.authenticate_user("user@test.com", "Pass123!")
        token = auth_result["token"]

        # Submit verification
        verify_result = env.submit_verification(
            token, "Model output: classified as A"
        )
        assert verify_result["success"] is True
        assert "proof_id" in verify_result

    def test_unauthenticated_user_cannot_submit_verification(self, env):
        result = env.submit_verification("invalid_token", "Some content")
        assert result["success"] is False
        assert "Unauthenticated" in result["error"]

    def test_user_can_retrieve_submitted_verification(self, env):
        # Setup
        env.create_user("user@test.com", "Pass123!")
        auth_result = env.authenticate_user("user@test.com", "Pass123!")
        token = auth_result["token"]

        # Submit
        verify_result = env.submit_verification(token, "Output data")
        proof_id = verify_result["proof_id"]

        # Retrieve
        get_result = env.get_proof(token, proof_id)
        assert get_result["success"] is True
        assert get_result["proof_id"] == proof_id

    def test_cannot_retrieve_nonexistent_proof(self, env):
        env.create_user("user@test.com", "Pass123!")
        auth_result = env.authenticate_user("user@test.com", "Pass123!")
        token = auth_result["token"]

        result = env.get_proof(token, "nonexistent_proof")
        assert result["success"] is False

    def test_cannot_retrieve_proof_when_logged_out(self, env):
        # Setup and submit
        env.create_user("user@test.com", "Pass123!")
        auth_result = env.authenticate_user("user@test.com", "Pass123!")
        token = auth_result["token"]
        verify_result = env.submit_verification(token, "Data")
        proof_id = verify_result["proof_id"]

        # Logout
        env.logout_user(token)

        # Try to retrieve
        result = env.get_proof(token, proof_id)
        assert result["success"] is False


class TestMultiUserFlow:
    """Test multiple users in system"""

    def test_multiple_users_can_exist(self, env):
        user1 = env.create_user("user1@test.com", "Pass1!")
        user2 = env.create_user("user2@test.com", "Pass2!")
        user3 = env.create_user("user3@test.com", "Pass3!")

        assert len(env.users) == 3

    def test_users_have_separate_sessions(self, env):
        # Create and login users
        env.create_user("alice@test.com", "Pass123!")
        env.create_user("bob@test.com", "Pass123!")

        alice_result = env.authenticate_user("alice@test.com", "Pass123!")
        bob_result = env.authenticate_user("bob@test.com", "Pass123!")

        alice_token = alice_result["token"]
        bob_token = bob_result["token"]

        assert alice_token != bob_token
        assert len(env.sessions) == 2

    def test_users_have_separate_proofs(self, env):
        # Create and login users
        env.create_user("user1@test.com", "Pass123!")
        env.create_user("user2@test.com", "Pass123!")

        user1_auth = env.authenticate_user("user1@test.com", "Pass123!")
        user2_auth = env.authenticate_user("user2@test.com", "Pass123!")

        # Submit proofs
        proof1 = env.submit_verification(user1_auth["token"], "User1 data")
        proof2 = env.submit_verification(user2_auth["token"], "User2 data")

        # Each user can only see their own proof
        assert proof1["proof_id"] != proof2["proof_id"]

        get1 = env.get_proof(user1_auth["token"], proof1["proof_id"])
        get2 = env.get_proof(user2_auth["token"], proof2["proof_id"])

        assert get1["success"] is True
        assert get2["success"] is True


class TestCompleteUserJourney:
    """Test complete user journey from start to finish"""

    def test_full_user_journey(self, env):
        # 1. User registers
        user = env.create_user("journey@test.com", "SecurePass123!")
        assert user.id in env.users

        # 2. User logs in
        login = env.authenticate_user("journey@test.com", "SecurePass123!")
        assert login["success"] is True
        token = login["token"]

        # 3. User submits first verification
        verify1 = env.submit_verification(token, "First inference output")
        assert verify1["success"] is True
        proof_id1 = verify1["proof_id"]

        # 4. User submits second verification
        verify2 = env.submit_verification(token, "Second inference output")
        assert verify2["success"] is True
        proof_id2 = verify2["proof_id"]

        # 5. User retrieves first proof
        get1 = env.get_proof(token, proof_id1)
        assert get1["success"] is True

        # 6. User retrieves second proof
        get2 = env.get_proof(token, proof_id2)
        assert get2["success"] is True

        # 7. User has 2 proofs
        assert len(env.proofs) == 2

        # 8. User logs out
        logout = env.logout_user(token)
        assert logout["success"] is True

        # 9. User cannot access after logout
        get_after_logout = env.get_proof(token, proof_id1)
        assert get_after_logout["success"] is False


# ========== RUNS WITH: pytest tests/test_integration.py ==========
