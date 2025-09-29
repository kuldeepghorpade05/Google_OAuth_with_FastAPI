from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from app.config.settings import settings
import httpx 

router = APIRouter()

# OAuth setup
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get("/login")
async def login(request: Request):
    """Initiate Google OAuth login"""
    redirect_uri = settings.OAUTH_REDIRECT_URI
    
    # Generate authorization URL with prompt parameter
    result = await oauth.google.create_authorization_url(
        redirect_uri,
        prompt="select_account"  # This forces Google to show account selection
    )
    
    # Store state in session
    request.session['oauth_state'] = result['state']
    
    print(f"Generated state: {result['state']}")
    print(f"Redirecting to: {result['url']}")
    
    return RedirectResponse(result['url'])

@router.get("/callback")
async def auth_callback(request: Request):
    """OAuth callback endpoint"""
    try:
        print("=== OAUTH CALLBACK STARTED ===")
        print(f"Full URL: {request.url}")
        
        # Get state from query parameters and session
        query_state = request.query_params.get('state')
        session_state = request.session.get('oauth_state')
        
        print(f"Query state: {query_state}")
        print(f"Session state: {session_state}")
        
        # Verify state exists and matches
        if not query_state or not session_state or session_state != query_state:
            raise HTTPException(status_code=400, detail="State verification failed")
        
        print("✓ State verification passed!")
        
        # Get the authorization code
        code = request.query_params.get('code')
        if not code:
            raise HTTPException(status_code=400, detail="No authorization code received")
        
        print(f"✓ Authorization code received")
        
        # MANUALLY exchange code for token to bypass Authlib's state verification
        redirect_uri = settings.OAUTH_REDIRECT_URI
        token_url = 'https://oauth2.googleapis.com/token'
        
        # Prepare token request
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                token_url,
                data={
                    'client_id': settings.GOOGLE_CLIENT_ID,
                    'client_secret': settings.GOOGLE_CLIENT_SECRET,
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Token exchange failed: {token_response.text}"
                )
            
            token_data = token_response.json()
            print("✓ Token received via manual exchange")
        
        # Get user info using the access token
        user_info_url = 'https://openidconnect.googleapis.com/v1/userinfo'
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                user_info_url,
                headers={'Authorization': f"Bearer {token_data['access_token']}"}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail=f"User info fetch failed: {user_response.text}"
                )
            
            user_info = user_response.json()
            print(f"✓ User info received: {user_info.get('email')}")
        
        # Clear the state from session
        request.session.pop('oauth_state', None)
        
        # Store user in session
        request.session['user'] = {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture': user_info.get('picture'),
            'google_id': user_info.get('sub')
        }
        
        print("✓ User stored in session")
        print("=== OAUTH CALLBACK COMPLETED SUCCESSFULLY ===")
        
        return {
            "message": "Authentication successful",
            "user": request.session['user']
        }
        
    except HTTPException:
        request.session.pop('oauth_state', None)
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        request.session.pop('oauth_state', None)
        raise HTTPException(
            status_code=400, 
            detail="Authentication failed. Please try again."
        )
    

@router.get("/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.pop('user', None)
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_current_user(request: Request):
    """Get current user info"""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


# debug endpoint ---------------------------------

# @router.get("/debug-redirect-uri")
# async def debug_redirect_uri(request: Request):
#     """Debug endpoint to check the redirect URI"""
#     redirect_uri = str(request.url_for("auth_callback"))
#     return {
#         "redirect_uri": redirect_uri,
#         "expected_uri": "http://localhost:8000/api/v1/auth/callback"
#     }

# debug endpoint ---------------------------

# @router.get("/debug-session")
# async def debug_session(request: Request):
#     """Debug endpoint to check session state"""
#     return {
#         "session_keys": list(request.session.keys()),
#         "oauth_state": request.session.get('oauth_state'),
#         "user": request.session.get('user')
#     }


# debug endpoint -----------------------------------

# @router.get("/debug-oauth-config")
# async def debug_oauth_config():
#     """Debug OAuth configuration"""
#     return {
#         "client_id_set": bool(settings.GOOGLE_CLIENT_ID),
#         "client_secret_set": bool(settings.GOOGLE_CLIENT_SECRET),
#         "redirect_uri": settings.OAUTH_REDIRECT_URI,
#         "metadata_url": "https://accounts.google.com/.well-known/openid-configuration"
#     }


# debug endpoint ------------------------------

# @router.get("/debug-oauth-request")
# async def debug_oauth_request(request: Request):
#     """Debug the actual OAuth request being made"""
#     redirect_uri = settings.OAUTH_REDIRECT_URI
    
#     # Create the authorization URL to see what's being generated
#     result = await oauth.google.create_authorization_url(redirect_uri)
    
#     return {
#         "redirect_uri_used": redirect_uri,
#         "full_auth_url": result['url'],
#         "generated_state": result['state'],
#         "current_oauth_redirect_uri": settings.OAUTH_REDIRECT_URI
#     }

# debug endpoint ----------------------

# @router.get("/check-settings")
# async def check_settings():
#     """Check current OAuth settings"""
#     return {
#         "GOOGLE_CLIENT_ID": "Set" if settings.GOOGLE_CLIENT_ID else "Not Set",
#         "GOOGLE_CLIENT_SECRET": "Set" if settings.GOOGLE_CLIENT_SECRET else "Not Set", 
#         "OAUTH_REDIRECT_URI": settings.OAUTH_REDIRECT_URI,
#         "ENVIRONMENT": settings.ENVIRONMENT
#     }

# debug endpoint -----------------------------

# @router.get("/test-session")
# async def test_session(request: Request):
#     """Test if session persistence works across requests"""
#     if 'test_counter' not in request.session:
#         request.session['test_counter'] = 1
#     else:
#         request.session['test_counter'] += 1
    
#     return {
#         "test_counter": request.session['test_counter'],
#         "session_keys": list(request.session.keys())
#     }

# debug endpoint --------------------------------------

# @router.get("/clear-session")
# async def clear_session(request: Request):
#     """Clear session for testing"""
#     request.session.clear()
#     return {"message": "Session cleared"}

# debug endpoint ----------------------------------

# @router.get("/debug-session-full")
# async def debug_session_full(request: Request):
#     """Comprehensive session debugging"""
#     # Test session write
#     request.session['debug_test'] = 'session_works'
    
#     # Get all session data
#     session_data = dict(request.session)
    
#     # Check cookies
#     cookies = request.cookies
    
#     return {
#         "session_data": session_data,
#         "cookies_present": list(cookies.keys()),
#         "has_session_cookie": 'session_id' in cookies,
#         "session_keys": list(request.session.keys())
#     }