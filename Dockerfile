FROM python:3.9-slim

# Install system dependencies including Icarus Verilog
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    iverilog \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir pyverilog pyyaml

WORKDIR /workspace

# Copy the script into the container
COPY v2lib.py /opt/v2lib/v2lib.py
RUN chmod +x /opt/v2lib/v2lib.py

# Set entrypoint so the container runs as an executable
ENTRYPOINT ["python3", "/opt/v2lib/v2lib.py"]
