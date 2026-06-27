import pytest
from app.services.auth_service import AuthService
from app.models.user import UserRole
from app.core.exceptions import PermissionDeniedException

@pytest.mark.asyncio
async def test_get_or_create_user(db_session):
    # 1. Yeni istifadəçi yaradılır
    user1 = await AuthService.get_or_create_user(
        db=db_session,
        telegram_id=111222,
        full_name="Test Agent",
        username="testagent"
    )
    
    assert user1.id is not None
    assert user1.telegram_id == 111222
    assert user1.role == UserRole.AGENT # Default
    
    # 2. Eyni istifadəçini yenidən çağırırıq (Create yox, Get olmalıdır)
    user2 = await AuthService.get_or_create_user(
        db=db_session,
        telegram_id=111222,
        full_name="Test Agent Yeni Ad",
        username="testagent"
    )
    
    assert user1.id == user2.id # Eyni istifadəçi olmalıdır
    assert user2.full_name == "Test Agent Yeni Ad" # Adı yeniləndi

@pytest.mark.asyncio
async def test_admin_permission_check():
    # Saxta istifadəçi obyektləri
    class DummyUser:
        def __init__(self, role):
            self.role = role

    agent = DummyUser(role=UserRole.AGENT)
    admin = DummyUser(role=UserRole.ADMIN)

    # Admin xəta verməməlidir
    AuthService.check_is_admin(admin)
    
    # Agent isə PermissionDeniedException verməlidir
    with pytest.raises(PermissionDeniedException):
        AuthService.check_is_admin(agent)
