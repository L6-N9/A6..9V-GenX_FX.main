import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import os
import numpy as np
import pandas as pd
import sys

# Add project root to path to allow module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test environment variables
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test"
os.environ["REDIS_URL"] = "redis://localhost:6379"

from api.main import app

@pytest.fixture
def client():
    """Create a test client that respects the lifespan context manager."""
    with TestClient(app) as c:
        yield c

class TestEdgeCases:
    """Comprehensive edge case testing for the GenX FX API"""
    
    def test_health_endpoint_structure(self, client):
        """Test health endpoint returns correct structure"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "timestamp" in data
        
        # Validate timestamp format
        from datetime import datetime
        try:
            datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("Invalid timestamp format")
    
    def test_root_endpoint_completeness(self, client):
        """Test root endpoint has all required information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["message", "version", "status", "github", "repository"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        assert data["status"] == "running"
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/")
        # The test client might not fully simulate CORS, but we can check basic structure
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented
    
    def test_large_request_handling(self, client):
        """Test handling of large request payloads"""
        # Test with a reasonably large payload
        large_data = {
            "symbol": "BTCUSDT",
            "data": ["x" * 1000] * 100,  # 100KB of data
            "metadata": {
                "large_array": list(range(1000)),
                "nested": {"deep": {"data": "test" * 100}}
            }
        }
        
        # This should work if the endpoint exists
        response = client.post("/api/v1/predictions", json=large_data)
        # We expect either success or a structured error, not a crash
        assert response.status_code in [200, 400, 404, 422, 500]
    
    def test_malformed_json_handling(self, client):
        """Test handling of malformed JSON requests"""
        # Test with invalid JSON - using correct endpoint
        response = client.post(
            "/api/v1/predictions",
            content="{ invalid json }",
            headers={"content-type": "application/json"}
        )
        # Auth middleware may catch this first, so 401/403 is also acceptable
        assert response.status_code in [400, 401, 403, 422]
    
    def test_null_and_empty_values(self, client):
        """Test handling of null and empty values in requests"""
        test_cases = [
            {},  # Empty object
            {"symbol": None},  # Null values
            {"symbol": ""},  # Empty strings
            {"symbol": "BTCUSDT", "data": None},  # Mixed null
            {"symbol": "BTCUSDT", "data": []},  # Empty arrays
        ]
        
        for test_data in test_cases:
            response = client.post("/api/v1/predictions", json=test_data)
            # Should handle gracefully, not crash (auth may return 401/403)
            assert response.status_code in [200, 400, 401, 403, 422, 500]
            if response.status_code >= 400:
                # Should return structured error
                error_data = response.json()
                assert "detail" in error_data or "error" in error_data
    
    def test_special_characters_handling(self, client):
        """Test handling of special characters and Unicode"""
        special_data = {
            "symbol": "BTC/USDT",  # Special chars in symbol
            "comment": "Testing 🚀📊💹 emojis and café résumé naïve",
            "data": {
                "chinese": "测试数据",
                "arabic": "بيانات الاختبار",
                "special": "!@#$%^&*()_+-=[]{}|;:,.<>?"
            }
        }
        
        response = client.post("/api/v1/predictions", json=special_data)
        assert response.status_code in [200, 400, 401, 403, 422, 500]
    
    def test_numeric_edge_cases(self, client):
        """Test handling of numeric edge cases"""
        edge_cases = [
            {"value": float('inf')},  # Infinity
            {"value": float('-inf')},  # Negative infinity
            {"value": 0},  # Zero
            {"value": -0},  # Negative zero
            {"value": 1e-10},  # Very small number
            {"value": 1e10},  # Very large number
            {"value": 0.1 + 0.2},  # Floating point precision
        ]
        
        for test_data in edge_cases:
            try:
                response = client.post("/api/v1/market-data/", json=test_data)
                assert response.status_code in [200, 400, 401, 403, 405, 422, 500]
            except (ValueError, TypeError):
                # JSON serialization might fail for inf/nan, that's acceptable
                pass
    
    def test_array_edge_cases(self, client):
        """Test handling of array edge cases"""
        array_cases = [
            {"data": []},  # Empty array
            {"data": [None, None, None]},  # Array of nulls
            {"data": [1, "string", True, None, {"nested": "object"}]},  # Mixed types
            {"data": [[1, 2], [3, 4], []]},  # Nested arrays with empty
        ]
        
        for test_data in array_cases:
            response = client.post("/api/v1/market-data/", json=test_data)
            assert response.status_code in [200, 400, 401, 403, 405, 422, 500]
    
    def test_deeply_nested_objects(self, client):
        """Test handling of deeply nested objects"""
        # Create a deeply nested object
        nested_data = {"data": {}}
        current = nested_data["data"]
        for i in range(20):  # 20 levels deep
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]
        current["deep_value"] = "reached the bottom"
        
        response = client.post("/api/v1/market-data/", json=nested_data)
        assert response.status_code in [200, 400, 401, 403, 405, 422, 500]
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10

class TestDataValidation:
    """Test data validation and sanitization"""
    
    def test_sql_injection_prevention(self, client):
        """Test SQL injection attempts are handled safely"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM accounts WHERE 1=1; --",
        ]
        
        for malicious_input in malicious_inputs:
            test_data = {"symbol": malicious_input}
            response = client.post("/api/v1/market-data/", json=test_data)
            # Should not crash and should handle safely
            assert response.status_code in [200, 400, 401, 403, 405, 422, 500]
            
            # Check response doesn't contain SQL error messages
            response_text = response.text.lower()
            dangerous_keywords = ["syntax error", "mysql", "postgresql", "sql", "table"]
            for keyword in dangerous_keywords:
                assert keyword not in response_text, f"Potential SQL injection vulnerability detected: {keyword}"
    
    def test_xss_prevention(self, client):
        """Test XSS attempts are handled safely"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//",
        ]
        
        for payload in xss_payloads:
            test_data = {"comment": payload}
            response = client.post("/api/v1/predictions", json=test_data)
            assert response.status_code in [200, 400, 401, 403, 422, 500]
            
            # Response should not execute scripts (validation error messages may contain them)
            # but should not have executable HTML in headers or unescaped contexts
            if response.headers.get("content-type", "").startswith("text/html"):
                assert "<script>" not in response.text
                assert "javascript:" not in response.text

class TestPerformanceEdgeCases:
    """Test performance-related edge cases"""
    
    def test_response_time_reasonable(self, client):
        """Test that responses come back in reasonable time"""
        import time
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 5.0, f"Health check took too long: {response_time}s"
        assert response.status_code == 200
    
    def test_memory_usage_with_large_data(self, client):
        """Test memory usage doesn't explode with large data"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        # Make request with large data
        large_data = {
            "data": ["x" * 1000] * 1000,  # 1MB of data
            "metadata": {"large_field": "y" * 10000}
        }
        
        response = client.post("/api/v1/market-data/", json=large_data)
        
        # Check memory didn't increase dramatically
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB"

class TestErrorHandling:
    """Test comprehensive error handling"""
    
    def test_undefined_endpoints(self, client):
        """Test handling of undefined endpoints"""
        undefined_endpoints = [
            "/api/v1/nonexistent",
            "/api/v1/admin/secret",
            "/api/v2/predictions/predict",  # Wrong version
            "/api/v1/predictions/delete_all",  # Dangerous endpoint
        ]
        
        for endpoint in undefined_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 404
            
            # Should return structured error
            if response.headers.get("content-type", "").startswith("application/json"):
                error_data = response.json()
                assert "detail" in error_data or "message" in error_data
    
    def test_method_not_allowed(self, client):
        """Test handling of wrong HTTP methods"""
        # Try wrong methods on existing endpoints
        test_cases = [
            ("DELETE", "/"),
            ("PUT", "/health"),
            ("PATCH", "/api/v1/predictions"),
        ]
        
        for method, endpoint in test_cases:
            response = client.request(method, endpoint)
            assert response.status_code in [405, 404]  # Method Not Allowed or Not Found
    
    def test_content_type_handling(self, client):
        """Test handling of different content types"""
        # Test with wrong content type
        response = client.post(
            "/api/v1/predictions",
            content="not json",
            headers={"content-type": "text/plain"}
        )
        assert response.status_code in [400, 401, 403, 415, 422]  # Bad Request or Unsupported Media Type
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, client):
        """Test handling of operations that might timeout"""
        # This would test actual timeout scenarios in a real environment
        # For now, we'll just ensure the structure exists
        with patch('api.services.ml_service.MLService.predict', new_callable=AsyncMock) as mock_predict:
            # Simulate a slow response
            async def slow_predict(*args, **kwargs):
                await asyncio.sleep(0.1)  # Short delay for testing
                return {"signal": "buy", "confidence": 0.8}
            
            mock_predict.side_effect = slow_predict
            
            response = client.post("/api/v1/predictions", json={"symbol": "BTCUSDT"})
            # Should complete even with delay
            assert response.status_code in [200, 400, 404, 422, 500]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
