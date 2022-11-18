from fastapi import HTTPException, status



credentials_exception = HTTPException(
    status_code = status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


# todo add exceptions

inactive_user = HTTPException(
    status_code = status.HTTP_403_FORBIDDEN,
    detail="Inactive use",
    headers={"WWW-Authenticate": "Bearer"},
)


token_expired = HTTPException(
    status_code = status.HTTP_401_UNAUTHORIZED,
    detail="Token expired",
    headers={"WWW-Authenticate": "Bearer"},
)

google_invalid_token = HTTPException(
    status_code = status.HTTP_400_BAD_REQUEST,
    detail="Invalid token"
)



network_connection_error = HTTPException(
    status_code = 599, # TODO 
    detail="Network connection error"
)