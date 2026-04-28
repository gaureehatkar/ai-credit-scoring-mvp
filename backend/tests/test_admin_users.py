import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.admin_user import AdminUser
from app.utils.security import hash_password
from datetime import datetime

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def super_admin_token():
    """Create a super_admin user and return auth token"""
    db = TestingSessionLocal()
    
    super_admin = AdminUser(
        email="super_admin@test.com",
        full_name="Super Admin",
        password_hash=hash_password("password123"),
        role="super_admin",
        permissions=["create_admin", "update_admin", "delete_admin"],
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(super_admin)
    db.commit()
    
    # Login to get token
    response = client.post(
        "/api/v1/admin/auth/login",
        json={"email": "super_admin@test.com", "password": "password123"}
    )
    
    db.close()
    return response.json()["access_token"]


@pytest.fixture
def admin_token():
    """Create a regular admin user and return auth token"""
    db = TestingSessionLocal()
    
    admin = AdminUser(
        email="admin@test.com",
        full_name="Admin User",
        password_hash=hash_password("password123"),
        role="admin",
        permissions=["view_applications"],
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(admin)
    db.commit()
    
    # Login to get token
    response = client.post(
        "/api/v1/admin/auth/login",
        json={"email": "admin@test.com", "password": "password123"}
    )
    
    db.close()
    return response.json()["access_token"]


def test_create_admin_user_success(super_admin_token):
    """Test creating a new admin user as super_admin"""
    response = client.post(
        "/api/v1/admin/users",
        json={
            "email": "newadmin@test.com",
            "password": "securepass123",
            "full_name": "New Admin",
            "role": "admin",
            "permissions": ["view_applications"]
        },
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newadmin@test.com"
    assert data["full_name"] == "New Admin"
    assert data["role"] == "admin"
    assert data["is_active"] is True


def test_create_admin_user_duplicate_email(super_admin_token):
    """Test creating admin user with duplicate email"""
    # Create first admin
    client.post(
        "/api/v1/admin/users",
        json={
            "email": "duplicate@test.com",
            "password": "securepass123",
            "full_name": "First Admin",
            "role": "admin"
        },
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    # Try to create second admin with same email
    response = client.post(
        "/api/v1/admin/users",
        json={
            "email": "duplicate@test.com",
            "password": "securepass123",
            "full_name": "Second Admin",
            "role": "admin"
        },
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    assert response.status_code == 409
    assert "Email already exists" in response.json()["detail"]


def test_create_admin_user_short_password(super_admin_token):
    """Test creating admin user with password shorter than 8 characters"""
    response = client.post(
        "/api/v1/admin/users",
        json={
            "email": "newadmin@test.com",
            "password": "short",
            "full_name": "New Admin",
            "role": "admin"
        },
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    assert response.status_code == 400


def test_create_admin_user_invalid_role(super_admin_token):
    """Test creating admin user with invalid role"""
    response = client.post(
        "/api/v1/admin/users",
        json={
            "email": "newadmin@test.com",
            "password": "securepass123",
            "full_name": "New Admin",
            "role": "invalid_role"
        },
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    assert response.status_code == 400


def test_create_admin_user_non_super_admin(admin_token):
    """Test that non-super_admin cannot create admin users"""
    response = client.post(
        "/api/v1/admin/users",
        json={
            "email": "newadmin@test.com",
            "password": "securepass123",
            "full_name": "New Admin",
            "role": "admin"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 403


def test_list_admin_users(super_admin_token):
    """Test listing admin users"""
    # Create a few admin users
    for i in range(3):
        client.post(
            "/api/v1/admin/users",
            json={
                "email": f"admin{i}@test.com",
                "password": "securepass123",
                "full_name": f"Admin {i}",
                "role": "admin"
            },
            headers={"Authorization": f"Bearer {super_admin_token}"}
        )
    
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_get_admin_user(super_admin_token):
    """Test getting a specific admin user"""
    # Create an admin user
    create_response = client.post(
        "/api/v1/admin/users",
        json={
            "email": "testadmin@test.com",
            "password": "securepass123",
            "full_name": "Test Admin",
            "role": "admin"
        },
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    admin_id = create_response.json()["admin_id"]
    
    # Get the admin user
    response = client.get(
        f"/api/v1/admin/users/{admin_id}",
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["admin_id"] == admin_id
    assert data["email"] == "testadmin@test.com"


def test_get_admin_user_not_found(super_admin_token):
    """Test getting a non-existent admin user"""
    response = client.get(
        "/api/v1/admin/users/9999",
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    assert response.status_code == 404


def test_update_admin_user(super_admin_token):
    """Test updating an admin user"""
    # Create an admin user
    create_response = client.post(
        "/api/v1/admin/users",
        json={
            "email": "testadmin@test.com",
            "password": "securepass123",
            "full_name": "Test Admin",
            "role": "admin",
            "permissions": []
        },
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    admin_id = create_response.json()["admin_id"]
    
    # Update the admin user
    response = client.patch(
        f"/api/v1/admin/users/{admin_id}",
        json={
            "full_name": "Updated Admin",
            "permissions": ["view_applications", "approve_applications"]
        },
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Admin"
    assert "view_applications" in data["permissions"]


def test_deactivate_admin_user(super_admin_token):
    """Test deactivating an admin user"""
    # Create an admin user
    create_response = client.post(
        "/api/v1/admin/users",
        json={
            "email": "testadmin@test.com",
            "password": "securepass123",
            "full_name": "Test Admin",
            "role": "admin"
        },
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    admin_id = create_response.json()["admin_id"]
    
    # Deactivate the admin user
    response = client.delete(
        f"/api/v1/admin/users/{admin_id}",
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    assert response.status_code == 204
    
    # Verify the admin user is deactivated
    get_response = client.get(
        f"/api/v1/admin/users/{admin_id}",
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    
    assert get_response.json()["is_active"] is False
