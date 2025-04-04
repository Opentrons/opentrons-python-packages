# Use an ARM-specific Python 3.10 image
FROM arm64v8/python:3.10-bullseye


# Update apt and install the PC/SC development package (provides libpcsclite.so.1)
RUN apt-get update && \
    apt-get install -y libpcsclite-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy the wheel from your local wheelhouse directory into /wheels inside the image
COPY wheelhouse /wheels

# Install the pyscard wheel from /wheels
RUN pip install /wheels/pyscard-2.2.1-cp310-cp310-linux_aarch64.whl

# Set the container to run a test: import the module and print a success message
CMD ["python", "-c", "import smartcard; print('pyscard imported successfully!')"]
