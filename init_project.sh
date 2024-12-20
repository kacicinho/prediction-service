#!/bin/bash

# Create .github directory for GitHub Actions workflows
mkdir -p .github/workflows

# Create app directory and feature-based subdirectories
mkdir -p app/core
mkdir -p app/services
mkdir -p app/tests
mkdir -p app/config

# Create empty files in the app structure
touch app/__init__.py
touch app/core/config.py
touch app/core/kafka_handler.py
touch app/core/s3_handler.py

touch app/services/image_service.py
touch app/services/event_service.py

touch app/tests/__init__.py
touch app/tests/test_image_service.py
touch app/tests/test_event_service.py
touch app/tests/test_integration.py

touch app/config/config.yaml

# Create requirements.txt file
touch requirements.txt

# Create Dockerfile
touch Dockerfile

# Create README.md file
touch README.md

# Display success message
echo "Project structure created successfully!"
