# 🚀 FastAPI Google OAuth 2.0 Authentication

A secure Google OAuth 2.0 implementation using **FastAPI**, **Authlib**, and **session-based authentication**, with CSRF protection, secure cookies, and environment-based configuration.

## 🛠️ Tech Stack

### **Backend Framework**
- **FastAPI** – Modern, fast (high-performance) web framework for building APIs

### **Authentication & OAuth**
- **Authlib** – OAuth and OpenID Connect client library
- **Google OAuth 2.0** – OAuth provider for user authentication

### **Session Management**
- **Starlette Sessions** – Session middleware
- **ItsDangerous** – Cryptographic signing for session cookies

### **HTTP & Async**
- **Uvicorn** – ASGI server for FastAPI
- **HTTPX** – Async HTTP client for API calls

### **Configuration & Environment**
- **Pydantic** – Settings and validation
- **python-dotenv** – Environment variable management

### **Security**
- **CORS** – Cross-Origin Resource Sharing
- **CSRF Protection** – via OAuth2 `state` parameter
- **Session Cookies** – HTTP-only, secure

## 📁 Project Structure

app/
├── main.py # FastAPI app & middleware
├── config/
│ └── settings.py # Environment configuration
└── api/v1/endpoints/
└── auth.py # OAuth routes & logic


---

## 🔐 OAuth 2.0 Flow

1. **Initiate Login** → `/login` → Redirects to Google
2. **Callback** → `/callback` → Google redirects back with code
3. **Token Exchange** → Exchanges auth code for tokens (manual HTTP call)
4. **User Info** → Fetches user profile from Google API
5. **Session Creation** → Stores user info securely in session
6. **Auth Check** → `/me` returns logged-in user info
7. **Logout** → `/logout` clears session

---

## 🌐 API Endpoints

| Method | Endpoint                  | Purpose                       |
|--------|---------------------------|-------------------------------|
| GET    | `/api/v1/auth/login`      | Start OAuth flow              |
| GET    | `/api/v1/auth/callback`   | OAuth callback handler        |
| GET    | `/api/v1/auth/logout`     | Clear user session            |
| GET    | `/api/v1/auth/me`         | Get current authenticated user|

---

## ✅ Features

- 🔐 Google OAuth 2.0 Integration
- 🧠 Session-Based Authentication
- 🛡️ CSRF Protection using OAuth2 State
- 🌍 CORS Configuration for Frontend
- 🔧 Manual Token Exchange Logic (no Authlib bugs!)
- 📦 Environment-Based Config with `.env`
- ❌ Secure Cookie Management
- ✅ Error Handling & Validation

---

## 📦 Installation

```bash
git clone https://github.com/your-username/fastapi-google-oauth.git
cd fastapi-google-oauth
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

⚙️ Environment Variables

Create a .env file in the root directory:

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=your_random_secret_key
SESSION_COOKIE_NAME=fastapi_session
BASE_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:3000

🚀 Running the App
uvicorn app.main:app --reload

🧪 Testing the Flow

- Open browser and go to: http://localhost:8000/api/v1/auth/login

- Authenticate with Google

- You’ll be redirected back and your session will be stored

- Test /api/v1/auth/me to get user info

- Use /api/v1/auth/logout to clear the session
