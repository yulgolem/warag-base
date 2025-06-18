# Worldbuilding Assistant

This project provides a small foundation for an agent-based system that
processes markdown files and stores extracted knowledge in databases.

## Setup

1. Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

2. Copy the example environment file and adjust values as needed:

```bash
cp .env.example .env
```

## Running tests

```bash
pytest -q
```

## Docker Compose Deployment

The project can be started locally using Docker Compose. This will run the
application together with PostgreSQL, Neo4j and Ollama services.

1. Ensure Docker and Docker Compose are installed.
2. Copy the example environment file if you have not done so already:

   ```bash
   cp .env.example .env
   ```

3. Build and start all services:

    ```bash
    docker compose up -d --build
    ```

4. View application logs:

    ```bash
    docker compose logs -f app
    ```

5. Verify that containers are running:

   ```bash
   docker compose ps
   ```

6. The Streamlit interface will be available at
   [http://localhost:8501](http://localhost:8501).

7. To run tests inside the app container use:

   ```bash
   docker compose exec app pytest -q
   ```

Stop the stack with `docker compose down` when you are done. For a clean restart use `docker compose down -v` before bringing the stack up again.

