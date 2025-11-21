from sqlalchemy.orm import Session
from datetime import datetime
from app.models.auth_user_device import AuthUserDevice

def check_device(db: Session, user, device_info, location):
    """
    Checks if the device is safe to login.

    Args:
        db: SQLAlchemy session
        user: User object (from auth_users table, with .uuid)
        device_info: object with device_id, user_agent, browser, os, ip, is_mobile, device_name
        location: string (city/country)

    Returns:
        (allow_login: bool, reason: str)
    """

    # 1️⃣ Check if device exists
    device = (
        db.query(AuthUserDevice)
        .filter_by(uuid=user.uuid, device_id=device_info.device_id)
        .first()
    )

    if device:
        if device.is_blacklisted:
            return False, "This device is blacklisted"

        # update last_used_at, ip, location
        device.last_used_at = datetime.utcnow()
        device.ip = device_info.ip
        device.location = location
        db.commit()
        return True, None

    # 2️⃣ New device → check suspicious activity
    suspicious, reason = analyze_device_risk(db, user, device_info, location)

    # Insert new device record
    new_device = AuthUserDevice(
        uuid=user.uuid,
        device_id=device_info.device_id,
        user_agent=device_info.user_agent,
        device_name=device_info.device_name,
        browser=device_info.browser,
        os=device_info.os,
        ip=device_info.ip,
        location=location,
        is_mobile=device_info.is_mobile,
        first_used_at=datetime.utcnow(),
        last_used_at=datetime.utcnow(),
        is_blacklisted=suspicious,
        blacklisted_reason=reason if suspicious else None,
        blacklisted_at=datetime.utcnow() if suspicious else None
    )
    db.add(new_device)
    db.commit()

    if suspicious:
        return False, reason

    return True, None


def analyze_device_risk(db: Session, user, device_info, location):
    """
    Simple suspicious activity check.
    Currently checks:
    - if last login location is different country (example)
    - you can expand with impossible travel, VPN, etc.

    Returns: (suspicious: bool, reason: str)
    """
    last_device = (
        db.query(AuthUserDevice)
        .filter_by(user_uuid=user.uuid)
        .order_by(AuthUserDevice.last_used_at.desc())
        .first()
    )

    if last_device and last_device.location != location:
        return True, "Login from a new location"

    return False, None