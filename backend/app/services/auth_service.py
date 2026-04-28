import secrets
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.services.email_service import EmailService


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: UserCreate) -> dict:
        """Register new user and send verification email"""
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters"
            )

        verification_token = secrets.token_urlsafe(32)

        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            is_verified=False,
            verification_token=verification_token
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        # Send verification email
        try:
            email_service = EmailService()
            email_service.send_verification_email(
                to_email=new_user.email,
                full_name=new_user.full_name,
                token=verification_token
            )
        except Exception as e:
            # Don't fail registration if email fails - just log it
            print(f"Warning: Failed to send verification email: {e}")

        return {"message": "Registration successful. Please check your email to verify your account."}

    def verify_email(self, token: str) -> dict:
        """Verify email with token"""
        user = self.db.query(User).filter(User.verification_token == token).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )

        user.is_verified = True
        user.verification_token = None
        self.db.commit()

        return {"message": "Email verified successfully. You can now log in."}

    def authenticate_user(self, credentials: UserLogin) -> TokenResponse:
        """Authenticate user and return JWT token"""
        user = self.db.query(User).filter(User.email == credentials.email).first()

        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before logging in"
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            role=user.role
        )
