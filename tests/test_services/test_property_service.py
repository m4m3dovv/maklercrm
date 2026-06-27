import pytest
from app.services.property_service import PropertyService
from app.schemas.property import PropertyCreate
from app.models.property import PropertyStatus

@pytest.mark.asyncio
async def test_create_and_get_property(db_session):
    from app.services.auth_service import AuthService
    
    # Test üçün əvvəlcə bir agent yaradaq
    actor = await AuthService.get_or_create_user(db_session, 123, "Agent 1")
    
    # Evin yaradılması
    prop_data = PropertyCreate(
        title="Gözəl Ev",
        district="Nəsimi",
        address="Küçə 1",
        room_count=3,
        area=100.5,
        price=150000.0,
        agent_id=actor.id
    )
    
    created_prop = await PropertyService.create_property(db_session, prop_data, actor)
    
    assert created_prop.id is not None
    assert created_prop.title == "Gözəl Ev"
    assert created_prop.status == PropertyStatus.ACTIVE
    
    # Evin statusunun dəyişdirilməsi
    updated_prop = await PropertyService.change_status(
        db=db_session,
        property_id=created_prop.id,
        new_status=PropertyStatus.SOLD,
        actor=actor
    )
    
    assert updated_prop.status == PropertyStatus.SOLD
