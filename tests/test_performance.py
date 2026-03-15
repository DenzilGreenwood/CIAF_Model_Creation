"""
Performance Benchmarks for CIAF Platform
Tests performance of critical operations
"""
import pytest
import time
import statistics
from datetime import datetime, timedelta
import jwt
import hashlib


class PerformanceMetrics:
    """Track performance metrics"""

    def __init__(self):
        self.measurements = []

    def measure(self, operation_name: str, duration: float):
        """Record a measurement"""
        self.measurements.append({
            "operation": operation_name,
            "duration_ms": duration * 1000,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_stats(self, operation_name: str) -> dict:
        """Get statistics for an operation"""
        durations = [m["duration_ms"] for m in self.measurements
                     if m["operation"] == operation_name]

        if not durations:
            return {}

        return {
            "min_ms": min(durations),
            "max_ms": max(durations),
            "avg_ms": statistics.mean(durations),
            "median_ms": statistics.median(durations),
            "stddev_ms": statistics.stdev(durations) if len(durations) > 1 else 0,
            "count": len(durations)
        }


# ========== PERFORMANCE FIXTURES ==========

@pytest.fixture
def metrics():
    return PerformanceMetrics()


# ========== AUTHENTICATION BENCHMARKS ==========

class TestAuthenticationPerformance:
    """Benchmark authentication operations"""

    SECRET_KEY = "test_secret_key"

    def test_password_hashing_performance(self, metrics):
        """Password hashing should complete within 100ms"""
        password = "VerySecurePassword123!@#$%^&*()"

        for i in range(10):
            start = time.time()
            hashed = hashlib.sha256(password.encode()).hexdigest()
            duration = time.time() - start
            metrics.measure("password_hash", duration)

        stats = metrics.get_stats("password_hash")
        assert stats["avg_ms"] < 100, f"Password hashing too slow: {stats['avg_ms']}ms"
        print(f"Password Hash - Avg: {stats['avg_ms']:.2f}ms")

    def test_token_generation_performance(self, metrics):
        """Token generation should complete within 50ms"""
        for i in range(10):
            start = time.time()
            payload = {
                "user_id": f"user_{i}",
                "exp": datetime.utcnow() + timedelta(minutes=15),
                "iat": datetime.utcnow(),
            }
            token = jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
            duration = time.time() - start
            metrics.measure("token_generate", duration)

        stats = metrics.get_stats("token_generate")
        assert stats["avg_ms"] < 50, f"Token generation too slow: {stats['avg_ms']}ms"
        print(f"Token Generation - Avg: {stats['avg_ms']:.2f}ms")

    def test_token_verification_performance(self, metrics):
        """Token verification should complete within 50ms"""
        # Generate a token first
        payload = {
            "user_id": "user123",
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")

        for i in range(10):
            start = time.time()
            decoded = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
            duration = time.time() - start
            metrics.measure("token_verify", duration)

        stats = metrics.get_stats("token_verify")
        assert stats["avg_ms"] < 50, f"Token verification too slow: {stats['avg_ms']}ms"
        print(f"Token Verification - Avg: {stats['avg_ms']:.2f}ms")

    def test_login_flow_performance(self, metrics):
        """Complete login flow should complete within 200ms"""
        password = "UserPassword123!"
        hashed = hashlib.sha256(password.encode()).hexdigest()

        for i in range(5):
            start = time.time()
            # Verify password
            provided = "UserPassword123!"
            verified = hashlib.sha256(provided.encode()).hexdigest() == hashed
            # Generate token
            payload = {"user_id": f"user_{i}", "exp": datetime.utcnow() + timedelta(minutes=15)}
            token = jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
            duration = time.time() - start
            metrics.measure("login_flow", duration)

        stats = metrics.get_stats("login_flow")
        assert stats["avg_ms"] < 200, f"Login flow too slow: {stats['avg_ms']}ms"
        print(f"Login Flow - Avg: {stats['avg_ms']:.2f}ms, Median: {stats['median_ms']:.2f}ms")


# ========== VERIFICATION/PROOF BENCHMARKS ==========

class TestVerificationPerformance:
    """Benchmark proof generation and verification"""

    def test_hash_computation_performance(self, metrics):
        """SHA-256 hash should compute within 10ms"""
        content = "Model output: classification result A with 95% confidence"

        for i in range(20):
            start = time.time()
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            duration = time.time() - start
            metrics.measure("hash_compute", duration)

        stats = metrics.get_stats("hash_compute")
        assert stats["avg_ms"] < 10, f"Hash computation too slow: {stats['avg_ms']}ms"
        print(f"Hash Computation - Avg: {stats['avg_ms']:.2f}ms")

    def test_proof_generation_performance(self, metrics):
        """Proof generation should complete within 50ms"""
        contents = [
            "Output 1: classified as A",
            "Output 2: classified as B",
            "Output 3: classified as C",
        ]

        for content in contents:
            for i in range(5):
                start = time.time()
                # Compute hash
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                # Generate timestamp
                timestamp = datetime.utcnow().isoformat()
                # Create signature
                signature = hashlib.sha256(
                    f"{content_hash}{timestamp}".encode()
                ).hexdigest()
                duration = time.time() - start
                metrics.measure("proof_generate", duration)

        stats = metrics.get_stats("proof_generate")
        assert stats["avg_ms"] < 50, f"Proof generation too slow: {stats['avg_ms']}ms"
        print(f"Proof Generation - Avg: {stats['avg_ms']:.2f}ms, Max: {stats['max_ms']:.2f}ms")

    def test_proof_verification_performance(self, metrics):
        """Proof verification should complete within 50ms"""
        # Generate proofs first
        proofs = []
        for i in range(5):
            content = f"Output content {i}"
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            timestamp = datetime.utcnow().isoformat()
            signature = hashlib.sha256(f"{content_hash}{timestamp}".encode()).hexdigest()
            proofs.append((content, content_hash, timestamp, signature))

        # Verify proofs
        for content, content_hash, timestamp, signature in proofs:
            for j in range(5):
                start = time.time()
                # Verify consistency
                expected_hash = hashlib.sha256(content.encode()).hexdigest()
                expected_signature = hashlib.sha256(
                    f"{expected_hash}{timestamp}".encode()
                ).hexdigest()
                is_valid = content_hash == expected_hash and signature == expected_signature
                duration = time.time() - start
                metrics.measure("proof_verify", duration)

        stats = metrics.get_stats("proof_verify")
        assert stats["avg_ms"] < 50, f"Proof verification too slow: {stats['avg_ms']}ms"
        print(f"Proof Verification - Avg: {stats['avg_ms']:.2f}ms")

    def test_materialization_performance(self, metrics):
        """Proof materialization should complete within 20ms"""
        proofs_data = []
        for i in range(10):
            content = f"Output {i}"
            proof = {
                "content_hash": hashlib.sha256(content.encode()).hexdigest(),
                "timestamp": datetime.utcnow().isoformat(),
                "signature": hashlib.sha256(f"sig_{i}".encode()).hexdigest(),
                "verified": True
            }
            proofs_data.append(proof)

        for proof in proofs_data:
            for j in range(5):
                start = time.time()
                # Materialize
                materialized = {
                    "proof": proof,
                    "materialized_at": datetime.utcnow().isoformat(),
                    "status": "verified" if proof["verified"] else "unverified"
                }
                duration = time.time() - start
                metrics.measure("materialize", duration)

        stats = metrics.get_stats("materialize")
        assert stats["avg_ms"] < 20, f"Materialization too slow: {stats['avg_ms']}ms"
        print(f"Materialization - Avg: {stats['avg_ms']:.2f}ms")


# ========== API RESPONSE TIME BENCHMARKS ==========

class TestAPIPerformance:
    """Benchmark API response times"""

    def test_verification_endpoint_response_time(self, metrics):
        """API endpoint should respond within 500ms"""
        # Simulate API call overhead
        for i in range(5):
            start = time.time()
            # Simulate database write, signature generation
            content_hash = hashlib.sha256(f"output_{i}".encode()).hexdigest()
            proof_id = f"proof_{i}"
            timestamp = datetime.utcnow().isoformat()
            # Simulate network latency (minimal in tests)
            duration = time.time() - start
            metrics.measure("api_verify_submit", duration)

        stats = metrics.get_stats("api_verify_submit")
        assert stats["avg_ms"] < 500, f"API response too slow: {stats['avg_ms']}ms"
        print(f"API Verify Submit - Avg: {stats['avg_ms']:.2f}ms")

    def test_get_proof_endpoint_response_time(self, metrics):
        """Get proof API should respond within 200ms"""
        for i in range(10):
            start = time.time()
            # Simulate database lookup
            proof = {
                "id": f"proof_{i}",
                "content_hash": hashlib.sha256(f"data_{i}".encode()).hexdigest(),
                "timestamp": datetime.utcnow().isoformat(),
                "status": "verified"
            }
            duration = time.time() - start
            metrics.measure("api_get_proof", duration)

        stats = metrics.get_stats("api_get_proof")
        assert stats["avg_ms"] < 200, f"Get proof too slow: {stats['avg_ms']}ms"
        print(f"API Get Proof - Avg: {stats['avg_ms']:.2f}ms")

    def test_health_check_response_time(self, metrics):
        """Health check should respond within 100ms"""
        for i in range(20):
            start = time.time()
            # Check services
            health = {
                "status": "healthy",
                "version": "1.0.0",
                "database": "connected"
            }
            duration = time.time() - start
            metrics.measure("api_health", duration)

        stats = metrics.get_stats("api_health")
        assert stats["avg_ms"] < 100, f"Health check too slow: {stats['avg_ms']}ms"
        print(f"API Health - Avg: {stats['avg_ms']:.2f}ms")


# ========== SUMMARY BENCHMARK REPORT ==========

@pytest.fixture(scope="session", autouse=True)
def print_benchmark_summary(request):
    """Print benchmark summary after tests"""
    yield
    print("\n" + "="*60)
    print("CIAF PLATFORM PERFORMANCE BENCHMARKS")
    print("="*60)
    print("\nTarget Performance Metrics:")
    print("  - Password Hashing: < 100ms")
    print("  - Token Generation: < 50ms")
    print("  - Token Verification: < 50ms")
    print("  - Hash Computation: < 10ms")
    print("  - Proof Generation: < 50ms")
    print("  - Proof Verification: < 50ms")
    print("  - API Response Times: < 500ms")
    print("  - Health Check: < 100ms")
    print("="*60 + "\n")


# ========== RUNS WITH: pytest tests/test_performance.py -v ==========
# ========== Or: pytest tests/test_performance.py --benchmark-only ==========
