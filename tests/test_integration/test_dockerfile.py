import os
import requests
import time
import pytest

if not os.environ.get("RUN_DOCKER_TESTS"):
    pytest.skip("Docker services not running", allow_module_level=True)


def test_all_services_healthy():
    """Test that all services are running and healthy."""
    # Wait for services to start
    time.sleep(30)

    # Test Streamlit app
    response = requests.get("http://localhost:8501/_stcore/health", timeout=10)
    assert response.status_code == 200

    # Test Ollama
    response = requests.get("http://localhost:11434/api/tags", timeout=10)
    assert response.status_code == 200

    # Test that models are loaded
    models = response.json()
    model_names = [model["name"] for model in models.get("models", [])]
    assert "nuextract" in str(model_names)
    assert "saiga" in str(model_names)


def test_app_accessible():
    """Test that Streamlit app is accessible."""
    response = requests.get("http://localhost:8501", timeout=10)
    assert response.status_code == 200
    assert "Worldbuilding Assistant" in response.text
