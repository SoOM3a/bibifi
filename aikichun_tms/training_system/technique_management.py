from .models import User, UserRole, Technique

# Simulate Technique Database
_techniques_db = []  # Stores Technique objects

# --- Admin Action Functions ---

def add_technique_by_admin(admin_user, name, description, level, section):
    """
    Adds a new technique, callable by an admin.
    """
    if not admin_user or admin_user.role != UserRole.ADMIN:
        print(f"Error: User {admin_user.username if admin_user else 'Unknown'} does not have ADMIN privileges to add techniques.")
        return None

    # Check if a technique with the same name already exists
    for existing_technique in _techniques_db:
        if existing_technique.name == name:
            print(f"Error: Technique with name '{name}' already exists.")
            return None

    # Create and add new Technique
    new_technique = Technique(
        name=name,
        description=description,
        level=level,
        section=section
    )
    _techniques_db.append(new_technique)

    print(f"Technique '{name}' added successfully by admin '{admin_user.username}'.")
    return new_technique

def modify_technique_by_admin(admin_user, technique_name, new_description=None, new_level=None, new_section=None):
    """
    Modifies an existing technique, callable by an admin.
    """
    if not admin_user or admin_user.role != UserRole.ADMIN:
        print(f"Error: User {admin_user.username if admin_user else 'Unknown'} does not have ADMIN privileges to modify techniques.")
        return False

    target_technique = None
    for technique_in_db in _techniques_db:
        if technique_in_db.name == technique_name:
            target_technique = technique_in_db
            break
    
    if not target_technique:
        print(f"Error: Technique '{technique_name}' not found.")
        return False

    changes = []
    if new_description is not None:
        target_technique.description = new_description
        changes.append("description")
    if new_level is not None:
        target_technique.level = new_level
        changes.append("level")
    if new_section is not None:
        target_technique.section = new_section
        changes.append("section")

    if changes:
        print(f"Technique '{technique_name}' successfully modified by admin '{admin_user.username}'. Changed: {', '.join(changes)}.")
    else:
        print(f"No changes applied to technique '{technique_name}'.")
        
    return True

# --- Helper function to print technique details ---
def print_all_techniques():
    print("\n--- Current Techniques in Database ---")
    if not _techniques_db:
        print("No techniques in the database.")
        return
    for tech in _techniques_db:
        print(f"  Name: {tech.name}, Level: {tech.level}, Section: {tech.section}, Description: {tech.description}")
    print("------------------------------------")

# --- Main execution block ---
if __name__ == '__main__':
    # 1. Create a sample Admin user (not added to any DB, just for role check)
    admin_user_obj = User(username="TechAdmin", email="techadmin@example.com", role=UserRole.ADMIN)
    admin_user_obj.set_password("techadminpass") # Not strictly needed for this script but good practice
    
    print(f"Simulated Admin User '{admin_user_obj.username}' for technique management.")

    # 2. Simulate Admin adding new techniques
    print("\n--- Admin adding new techniques ---")
    add_technique_by_admin(
        admin_user=admin_user_obj,
        name="Aikido Punch Defense",
        description="Basic defense against a straight punch.",
        level="Kyu 5",
        section="Self-Defense"
    )
    add_technique_by_admin(
        admin_user=admin_user_obj,
        name="Wrist Lock I",
        description="Fundamental wrist lock technique.",
        level="Kyu 5",
        section="Joint Locks"
    )
    print_all_techniques()

    # 3. Simulate Admin modifying an existing technique
    print("\n--- Admin modifying 'Aikido Punch Defense' ---")
    modify_technique_by_admin(
        admin_user=admin_user_obj,
        technique_name="Aikido Punch Defense",
        new_description="Improved defense against a straight punch, focusing on evasion.",
        new_level="Kyu 4"
    )
    print_all_techniques()
    
    # 4. Test Cases
    print("\n--- Test Cases ---")

    # Non-admin attempting to add a technique
    non_admin_user = User(username="PlayerX", email="playerx@example.com", role=UserRole.PLAYER)
    print(f"\n--- Attempt by non-admin '{non_admin_user.username}' to add a technique ---")
    add_technique_by_admin(
        admin_user=non_admin_user,
        name="Unauthorized Technique",
        description="A technique added by a non-admin.",
        level="Kyu 1",
        section="Advanced"
    )
    print_all_techniques()

    # Non-admin attempting to modify a technique
    print(f"\n--- Attempt by non-admin '{non_admin_user.username}' to modify 'Wrist Lock I' ---")
    modify_technique_by_admin(
        admin_user=non_admin_user,
        technique_name="Wrist Lock I",
        new_description="Unauthorized modification."
    )
    print_all_techniques()

    # Trying to add a technique with a duplicate name
    print("\n--- Admin attempting to add technique with duplicate name 'Wrist Lock I' ---")
    add_technique_by_admin(
        admin_user=admin_user_obj,
        name="Wrist Lock I", # Duplicate name
        description="Another wrist lock.",
        level="Kyu 6",
        section="Joint Locks"
    )
    print_all_techniques()

    # Trying to modify a non-existent technique
    print("\n--- Admin attempting to modify non-existent technique 'Ghost Technique' ---")
    modify_technique_by_admin(
        admin_user=admin_user_obj,
        technique_name="Ghost Technique",
        new_description="This should fail."
    )
    print_all_techniques()
    
    # Trying to modify with no actual changes
    print("\n--- Admin attempting to modify 'Wrist Lock I' with no actual changes ---")
    modify_technique_by_admin(
        admin_user=admin_user_obj,
        technique_name="Wrist Lock I" 
        # No new_description, new_level, or new_section provided
    )
    print_all_techniques()

    print("\n--- End of technique_management.py simulation ---")
