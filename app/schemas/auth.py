from pydantic import BaseModel, EmailStr


# ---------- Register ----------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class RegisterResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str | None = None


# ---------- Login ----------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ---------- Refresh ----------
class RefreshRequest(BaseModel):
    refresh_token: str
