from database import engine, SessionLocal, Base, Admin

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Create a database session
db = SessionLocal()

try:
    # -------------------------
    # Optional: Delete all existing admins
    # -------------------------
    # If you want to remove all existing admins, uncomment below:
    # deleted_count = db.query(Admin).delete()
    # db.commit()
    # print(f"✅ Deleted {deleted_count} existing admin(s).")

    # List of admins to add (password, email, is_active)
    admins_to_add = [
        ("admin123", "admin@gmail.com", 1),
        # Add more admins here as needed
    ]

    for password, email, is_active in admins_to_add:
        existing_admin = db.query(Admin).filter(Admin.email == email).first()
        if existing_admin:
            print(f"Admin already exists! Email: {existing_admin.email}")
        else:
            new_admin = Admin(username=email, password=password, email=email, is_active=is_active)
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            print(f"✅ Admin created successfully! Email: {new_admin.email}")

    # Ensure all changes are committed and session is refreshed before server start
    db.commit()
    db.close()

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
