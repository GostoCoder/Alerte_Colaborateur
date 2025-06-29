# Bourgeois_vehicle

## API Documentation

### Collaborateurs

- **POST /collaborateurs**
  Create a new collaborator.
  **Body:**
  ```json
  {
    "nom": "string",
    "prenom": "string",
    "ifo": "YYYY-MM-DD or null",
    "caces": "YYYY-MM-DD or null",
    "airr": "YYYY-MM-DD or null",
    "hgo_bo": "YYYY-MM-DD or null",
    "visite_med": "YYYY-MM-DD or null",
    "brevet_secour": "YYYY-MM-DD or null"
  }
  ```
  **Response:** 201 Created, collaborator object

- **GET /collaborateurs**
  List all collaborators.
  **Query params:** `skip`, `limit`, `search`, `sort_by`, `direction`
  **Response:** 200 OK, list of collaborators

- **GET /collaborateurs/{id}**
  Get details for a collaborator by ID.
  **Response:** 200 OK, collaborator object or 404

- **PUT /collaborateurs/{id}**
  Update a collaborator by ID.
  **Body:** Same as POST
  **Response:** 200 OK, updated collaborator or 404

- **DELETE /collaborateurs/{id}**
  Delete a collaborator by ID.
  **Response:** 204 No Content or 404

### Notifications

- **POST /notifications/send**
  Trigger notification logic for expiring certifications.
  **Response:** 200 OK or 500 on error

- **GET /notifications/send**
  Manually trigger notification sending.
  **Response:** 200 OK or 500 on error

---

## Installation & Usage

### 1. Clone the repository

```bash
git clone <repo-url>
cd <repo-directory>
```

### 2. Python Environment

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. .env Setup

Create a `.env` file in the root directory with the following variables:

```
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SENDER_EMAIL=your@email.com
SENDER_PASSWORD=yourpassword
RECIPIENT_EMAIL=recipient@email.com
RECIPIENT_EMAIL_2=optional2@email.com
```

### 4. Run with Docker

Build and run:

```bash
docker-compose up --build
```

Or manually:

```bash
docker build -t bourgeois-app .
docker run -p 5000:5000 bourgeois-app
```

### 5. Run Tests

```bash
pytest tests/
```


To access your Dockerized Python app through a custom domain like `https://gestion-des-vehicules` instead of `http://127.0.0.1:5000/`, you'll need to configure a few things, including setting up your app with HTTPS and configuring DNS or a reverse proxy (like Nginx or Traefik). Here's a step-by-step guide:

### 1. **Generate SSL Certificates (for HTTPS)**

To serve your app over HTTPS, you need SSL certificates. For local development, you can generate self-signed certificates, but for production, you should use a certificate from a trusted Certificate Authority (CA).

To create self-signed certificates for local use:

```bash
mkdir -p certs
cd certs
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -in server.csr -signkey server.key -out server.crt
```

This will generate the following files:
- `server.key` (private key)
- `server.crt` (certificate)

### 2. **Modify Your Python App to Use SSL**

You’ll need to modify your Python app to use HTTPS. If you're using Flask (for example), you can use the built-in support for SSL.

Here's how you can modify your Python code to enable SSL:

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, HTTPS!"

if __name__ == "__main__":
    # Point to your SSL certificates
    app.run(host='0.0.0.0', port=5000, ssl_context=('certs/server.crt', 'certs/server.key'))
```

Make sure to adjust the paths to your SSL certificate and key files.

### 3. **Dockerize Your App**

You likely already have a `Dockerfile`, but you need to ensure the SSL certificates are included in the Docker container.

For example, here's a simple `Dockerfile` that copies the certificates into the container:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app

# Install necessary dependencies (Flask, etc.)
RUN pip install -r requirements.txt

# Copy SSL certificates
COPY certs /app/certs

# Expose port for HTTPS
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
```

### 4. **Run the Docker Container**

Build and run the Docker container:

```bash
docker build -t bourgeois-app .
docker run -p 5000:5000 bourgeois-app
```

### 5. **Access the App Using a Custom Domain (`gestion-des-vehicules`)**

Now you need to make the app available via `https://gestion-des-vehicules`.

1. **Edit Your Hosts File (Local Development)**:
   - On Linux/macOS, the file is located at `/etc/hosts`.
   - On Windows, it's located at `C:\Windows\System32\drivers\etc\hosts`.

   Add a line like this to point `gestion-des-vehicules` to `127.0.0.1`:

   ```bash
   127.0.0.1 gestion-des-vehicules
   ```

2. **Configure Nginx as a Reverse Proxy (Optional)**:
   
   If you want to use Nginx (or another reverse proxy) to map `https://gestion-des-vehicules` to your Docker container, you would need to install and configure Nginx on your host machine.

   Here’s an example Nginx configuration:

   ```nginx
   server {
       listen 443 ssl;
       server_name gestion-des-vehicules;

       ssl_certificate /path/to/certs/server.crt;
       ssl_certificate_key /path/to/certs/server.key;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   - **Enable Nginx to listen on port 443** for HTTPS.
   - Use your SSL certificates (make sure they are valid for your domain).

   After updating the Nginx configuration, restart the Nginx service:

   ```bash
   sudo service nginx restart
   ```

   You may also need to adjust firewall settings to allow traffic on port 443.

### 6. **Access Your App**

Now, you should be able to access your app by navigating to `https://gestion-des-vehicules` in your browser.

---

### Notes:
- If you're using a self-signed certificate, the browser may warn you that the connection is not secure. You can proceed despite the warning or use a trusted certificate from a CA for production.
- The `gestion-des-vehicules` domain will only work on your local machine unless you configure a public DNS service.
- If deploying to production, you'll want to secure your application with a trusted SSL certificate from a CA and make sure to configure proper DNS settings.

Let me know if you need further clarification on any of the steps!