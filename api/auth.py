"""
Supabase authentication integration for the Band Manager API.
Handles JWT token validation and user authentication.
"""

import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import logging

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY") 
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# Security scheme for FastAPI
security = HTTPBearer()

class SupabaseAuth:
    """Handles Supabase authentication operations"""
    
    def __init__(self):
        if not all([SUPABASE_URL, SUPABASE_ANON_KEY]):
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        self.jwt_secret = SUPABASE_JWT_SECRET
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a Supabase JWT token.
        
        Args:
            token: The JWT token to verify
            
        Returns:
            Dict containing the decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # If we have the JWT secret, verify the signature
            if self.jwt_secret:
                payload = jwt.decode(
                    token, 
                    self.jwt_secret, 
                    algorithms=["HS256"],
                    audience="authenticated"
                )
            else:
                # If no secret provided, decode without verification (development only)
                logger.warning("JWT secret not provided - token signature not verified")
                payload = jwt.decode(
                    token, 
                    options={"verify_signature": False}
                )
            
            return payload
            
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def get_user_from_token(self, token: str) -> Dict[str, Any]:
        """
        Extract user information from a valid JWT token.
        
        Args:
            token: The JWT token
            
        Returns:
            Dict containing user information
        """
        payload = self.verify_jwt_token(token)
        
        # Extract user info from token payload
        user_metadata = payload.get("user_metadata", {})
        user_info = {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role", "authenticated"),
            "aud": payload.get("aud"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
            "display_name": user_metadata.get("display_name")
        }
        
        if not user_info["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_info

# Global auth instance
supabase_auth = SupabaseAuth()

# Dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency to get the current authenticated user.
    
    This function extracts the JWT token from the Authorization header,
    validates it with Supabase, and returns the user information.
    
    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        
    Returns:
        Dict containing user information from the token
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        token = credentials.credentials
        user_info = supabase_auth.get_user_from_token(token)
        return user_info
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Optional dependency for getting current user (allows anonymous access)
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency to optionally get the current authenticated user.
    
    This allows endpoints to work with both authenticated and anonymous users.
    
    Args:
        credentials: Optional HTTP Authorization credentials
        
    Returns:
        Dict containing user information if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None