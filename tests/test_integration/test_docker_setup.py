import os


def test_docker_files_exist():
    assert os.path.exists("docker-compose.yml")
    assert os.path.exists("Dockerfile")
