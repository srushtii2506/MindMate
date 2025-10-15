from database import SessionLocal, Admin

def delete_admin_by_email(email: str):
    # Print the database URL to verify which DB is used
    from database import DATABASE_URL
    print(f"Connecting to database: {DATABASE_URL}")
    db = SessionLocal()
    try:
        admin_to_delete = db.query(Admin).filter(Admin.email == email).first()
        if admin_to_delete:
            db.delete(admin_to_delete)
            db.commit()
            print(f"✅ Admin deleted successfully! Email: {email}")
        else:
            print(f"⚠️ Admin not found with email: {email}")
    except Exception as e:
        print(f"Error deleting admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python delete_admin.py <admin_email>")
    else:
        delete_admin_by_email(sys.argv[1])
