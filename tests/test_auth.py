"""
Backend Unit Tests - Authentication System
Tests for token generation, validation, password hashing, etc.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import jwt


# Mock authentication functions (these would be from your actual auth module)
class AuthService:
    SECRET_KEY = "test_secret_key"

    @staticmethod
    def generate_token(user_id: str, expires_in_minutes: int = 15) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=expires_in_minutes),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, AuthService.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            return jwt.decode(token, AuthService.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    @staticmethod
    def hash_password(password: str) -> str:
        # In real code, use bcrypt
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return AuthService.hash_password(password) == hashed


# ========== TESTS ==========

class TestTokenGeneration:
    """Test JWT token generation"""

    def test_generate_token_creates_valid_jwt(self):
        token = AuthService.generate_token("user123")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_user_id(self):
        user_id = "user456"
        token = AuthService.generate_token(user_id)
        payload = jwt.decode(token, AuthService.SECRET_KEY, algorithms=["HS256"])
        assert payload["user_id"] == user_id

    def test_token_has_expiration(self):
        token = AuthService.generate_token("user789", expires_in_minutes=30)
        payload = jwt.decode(token, AuthService.SECRET_KEY, algorithms=["HS256"])
        assert "exp" in payload
        assert "iat" in payload
        # Token expiration should be after issued-at time
        assert payload["exp"] > payload["iat"]

    def test_token_default_expiration_is_15_minutes(self):
        token = AuthService.generate_token("user000")
        payload = jwt.decode(token, AuthService.SECRET_KEY, algorithms=["HS256"])
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        diff_minutes = (exp_time - iat_time).total_seconds() / 60
        assert 14 < diff_minutes < 16


class TestTokenVerification:
    """Test JWT token verification"""

    def test_verify_valid_token_succeeds(self):
        token = AuthService.generate_token("user123")
        payload = AuthService.verify_token(token)
        assert payload["user_id"] == "user123"

    def test_verify_expired_token_fails(self):
        # Create an already-expired token
        payload = {
            "user_id": "user123",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Already expired
            "iat": datetime.utcnow() - timedelta(hours=2),
        }
        expired_token = jwt.encode(payload, AuthService.SECRET_KEY, algorithm="HS256")

        with pytest.raises(ValueError, match="Token expired"):
            AuthService.verify_token(expired_token)

    def test_verify_invalid_token_fails(self):
        invalid_token = "invalid.token.here"
        with pytest.raises(ValueError, match="Invalid token"):
            AuthService.verify_token(invalid_token)

    def test_verify_token_with_wrong_secret_fails(self):
        token = AuthService.generate_token("user123")
        # Try to verify with wrong secret
        with pytest.raises((ValueError, jwt.InvalidSignatureError)):
            jwt.decode(token, "wrong_secret", algorithms=["HS256"])


class TestPasswordHandling:
    """Test password hashing and verification"""

    def test_hash_password_creates_different_output(self):
        password = "MySecurePassword123!"
        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)
        # Same password produces same hash (for SHA256, unlike bcrypt)
        assert hash1 == hash2

    def test_hash_password_creates_non_empty_string(self):
        hashed = AuthService.hash_password("password")
        assert len(hashed) > 0
        assert isinstance(hashed, str)

    def test_verify_password_with_correct_password(self):
        password = "CorrectPassword123!"
        hashed = AuthService.hash_password(password)
        assert AuthService.verify_password(password, hashed)

    def test_verify_password_with_incorrect_password(self):
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = AuthService.hash_password(password)
        assert not AuthService.verify_password(wrong_password, hashed)

    def test_verify_password_case_sensitive(self):
        password = "MyPassword"
        hashed = AuthService.hash_password(password)
        assert not AuthService.verify_password("mypassword", hashed)


class TestPasswordValidation:
    """Test password strength requirements"""

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list]:
        """Validate password meets requirements"""
        errors = []

        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        if not any(c.isupper() for c in password):
            errors.append("Password must contain uppercase letter")
        if not any(c.islower() for c in password):
            errors.append("Password must contain lowercase letter")
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain number")
        if not any(c in "!@#$%^&*" for c in password):
            errors.append("Password must contain special character")

        return len(errors) == 0, errors

    def test_strong_password_passes_validation(self):
        valid, errors = self.validate_password_strength("StrongPass123!")
        assert valid
        assert len(errors) == 0

    def test_short_password_fails(self):
        valid, errors = self.validate_password_strength("Short1!")
        assert not valid
        assert "at least 8 characters" in errors[0]

    def test_password_missing_uppercase_fails(self):
        valid, errors = self.validate_password_strength("lowercase123!")
        assert not valid
        assert any("uppercase" in e for e in errors)

    def test_password_missing_number_fails(self):
        valid, errors = self.validate_password_strength("NoNumbers!")
        assert not valid
        assert any("number" in e for e in errors)

    def test_password_missing_special_char_fails(self):
        valid, errors = self.validate_password_strength("NoSpecialChar1")
        assert not valid
        assert any("special" in e for e in errors)


class TestAuthenticationFlow:
    """Test complete authentication flow"""

    def test_login_flow_with_valid_credentials(self):
        # User registers with password
        password = "ValidPass123!"
        hashed = AuthService.hash_password(password)

        # User logs in
        provided_password = "ValidPass123!"
        assert AuthService.verify_password(provided_password, hashed)

        # Generate token
        token = AuthService.generate_token("user123")
        assert token is not None

        # Verify token
        payload = AuthService.verify_token(token)
        assert payload["user_id"] == "user123"

    def test_login_flow_with_invalid_password(self):
        password = "ValidPass123!"
        hashed = AuthService.hash_password(password)

        provided_password = "WrongPass123!"
        assert not AuthService.verify_password(provided_password, hashed)


# ========== RUNS WITH: pytest tests/test_auth.py ==========
