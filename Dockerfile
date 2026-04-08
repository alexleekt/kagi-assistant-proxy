# Multi-stage build for kagi-assistant-proxy
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .
COPY lib/ ./lib/
COPY tester.html .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, os; port = os.environ.get('PORT', 5000); urllib.request.urlopen(f'http://localhost:{port}/', timeout=5)"

# Run the application
CMD ["python", "server.py"]
