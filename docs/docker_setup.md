# Docker Setup

The project is containerized for easy deployment and reproducibility. A `Dockerfile` will build an environment with Python, Redis (for short-term memory), and database drivers.

## Basic Usage

1. Build the image:
   ```bash
   docker build -t writeragents .
   ```
2. Run the container:
   ```bash
   docker run -it writeragents
   ```

For persistent storage, mount a volume for the database location and configure Redis as needed.

