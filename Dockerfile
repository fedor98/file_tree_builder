# Use the official Alpine-based Python image.
FROM python:3.12-alpine

# Set working directory.
WORKDIR /app

# Copy the Python script into the container.
COPY generate_file_tree.py .

# Make sure the script is executable (optional).
RUN chmod +x generate_file_tree.py

# Set the entrypoint so that the container runs the script.
ENTRYPOINT ["python", "generate_file_tree.py"]
