import argparse
import sys
from src.db import get_db_connection
from src.auth import revoke_all_tokens

def add_staff(email, name, role, department):
    email = email.lower().strip()
    import secrets
    from src.auth import hash_password
    
    # Generate 8-character random readable temp password
    temp_password = secrets.token_hex(4)
    pwd_hash = hash_password(temp_password)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM staff_users WHERE email = ?;", (email,))
        if cursor.fetchone():
            print(f"Error: Staff user with email '{email}' already exists.")
            sys.exit(1)
        
        cursor.execute(
            """INSERT INTO staff_users (email, name, role, department, is_active, password_hash, must_change_password)
               VALUES (?, ?, ?, ?, 1, ?, 1);""",
            (email, name, role, department, pwd_hash)
        )
        conn.commit()
        print(f"Successfully added staff user '{name}' ({email}) with role '{role}' in department '{department}'.")
        print(f"⚠️ TEMPORARY PASSWORD: {temp_password}")
        print("Staff user will be forced to change this password upon their first sign in.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        conn.close()

def list_staff():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, name, role, department, is_active, last_login FROM staff_users;")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("No staff users found.")
        return
    print(f"{'ID':<5} | {'Email':<30} | {'Name':<20} | {'Role':<15} | {'Dept':<10} | {'Active':<6} | {'Last Login'}")
    print("-" * 110)
    for r in rows:
        print(f"{r['id']:<5} | {r['email']:<30} | {r['name']:<20} | {r['role']:<15} | {r['department']:<10} | {r['is_active']:<6} | {r['last_login']}")

def deactivate_staff(email):
    email = email.lower().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM staff_users WHERE email = ?;", (email,))
        row = cursor.fetchone()
        if not row:
            print(f"Error: Staff user with email '{email}' not found.")
            sys.exit(1)
        
        cursor.execute("UPDATE staff_users SET is_active = 0 WHERE email = ?;", (email,))
        conn.commit()
        revoke_all_tokens(row["id"])
        print(f"Successfully deactivated staff user '{email}' and revoked all active sessions.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        conn.close()

def update_staff(email, role=None, department=None):
    email = email.lower().strip()
    if not role and not department:
        print("Error: Specify at least --role or --department to update.")
        sys.exit(1)
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM staff_users WHERE email = ?;", (email,))
        if not cursor.fetchone():
            print(f"Error: Staff user with email '{email}' not found.")
            sys.exit(1)
            
        updates = []
        params = []
        if role:
            updates.append("role = ?")
            params.append(role)
        if department:
            updates.append("department = ?")
            params.append(department)
            
        params.append(email)
        cursor.execute(
            f"UPDATE staff_users SET {', '.join(updates)} WHERE email = ?;",
            tuple(params)
        )
        conn.commit()
        print(f"Successfully updated staff user '{email}'.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        conn.close()

def view_audit_logs(limit):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.timestamp, l.actor_type, l.actor_id, l.action, l.target_type, l.target_id, l.details, l.ip_address,
               s.name AS staff_name, s.email AS staff_email
        FROM audit_logs l
        LEFT JOIN staff_users s ON (l.actor_type = 'staff' AND CAST(l.actor_id AS INTEGER) = s.id)
        ORDER BY l.id DESC 
        LIMIT ?;
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("No audit logs found.")
        return
    print(f"{'Timestamp':<20} | {'Actor':<35} | {'Action':<15} | {'Target':<15} | {'Details'}")
    print("-" * 115)
    for r in rows:
        actor = "System"
        if r['actor_type'] == 'staff':
            actor = f"{r['staff_name'] or 'Staff'} ({r['staff_email'] or r['actor_id']})"
        elif r['actor_type'] == 'student':
            actor = f"Student ({r['actor_id']})"
        elif r['actor_id']:
            actor = r['actor_id']
            
        target = f"{r['target_type'] or ''}"
        if r['target_id']:
            target += f"({r['target_id']})"
        details = (r['details'] or "")[:40]
        print(f"{r['timestamp'][:19]:<20} | {actor:<35} | {r['action']:<15} | {target:<15} | {details}")

def main():
    parser = argparse.ArgumentParser(description="PDP University Career Center Staff Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add-staff
    add_parser = subparsers.add_parser("add-staff", help="Add a staff user to allowlist")
    add_parser.add_argument("--email", required=True, help="Staff email address")
    add_parser.add_argument("--name", required=True, help="Staff full name")
    add_parser.add_argument("--role", required=True, choices=["super_admin", "career_staff", "academic_staff", "teacher", "viewer"], help="Staff role")
    add_parser.add_argument("--department", required=True, choices=["career", "academic", "teaching", "all"], help="Staff department")

    # list-staff
    subparsers.add_parser("list-staff", help="List all allowlisted staff users")

    # deactivate-staff
    deact_parser = subparsers.add_parser("deactivate-staff", help="Deactivate a staff user")
    deact_parser.add_argument("--email", required=True, help="Staff email to deactivate")

    # update-staff
    upd_parser = subparsers.add_parser("update-staff", help="Update role or department for a staff user")
    upd_parser.add_argument("--email", required=True, help="Staff email to update")
    upd_parser.add_argument("--role", choices=["super_admin", "career_staff", "academic_staff", "teacher", "viewer"], help="New role")
    upd_parser.add_argument("--department", choices=["career", "academic", "teaching", "all"], help="New department")

    # audit-logs
    audit_parser = subparsers.add_parser("audit-logs", help="View recent security and administrative audit logs")
    audit_parser.add_argument("--limit", type=int, default=50, help="Maximum number of logs to print")

    args = parser.parse_args()

    if args.command == "add-staff":
        add_staff(args.email, args.name, args.role, args.department)
    elif args.command == "list-staff":
        list_staff()
    elif args.command == "deactivate-staff":
        deactivate_staff(args.email)
    elif args.command == "update-staff":
        update_staff(args.email, args.role, args.department)
    elif args.command == "audit-logs":
        view_audit_logs(args.limit)

if __name__ == "__main__":
    main()
