import datetime
from werkzeug.security import generate_password_hash # Not strictly needed if User.set_password uses it
from .models import User, UserRole, UserProfile

# Simulate User Database
_users_db = []  # Stores User objects
_user_profiles_db = [] # Stores UserProfile objects

# --- Admin Action Functions ---

def add_user_by_admin(admin_user, username, email, password, role, full_name, date_of_birth_str=None):
    """
    Adds a new user and their profile, callable by an admin.
    """
    if not admin_user or admin_user.role != UserRole.ADMIN:
        print(f"Error: User {admin_user.username if admin_user else 'Unknown'} does not have ADMIN privileges to add users.")
        return None

    # Check for existing username or email
    for existing_user in _users_db:
        if existing_user.username == username:
            print(f"Error: Username '{username}' already exists.")
            return None
        if existing_user.email == email:
            print(f"Error: Email '{email}' already exists.")
            return None

    # Create and add new User
    new_user = User(username=username, email=email, role=role)
    new_user.set_password(password) # Hashes and sets password_hash
    _users_db.append(new_user)

    # Create and add new UserProfile
    dob = None
    if date_of_birth_str:
        try:
            dob = datetime.datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"Warning: Invalid date format for '{date_of_birth_str}'. Date of birth not set.")
            
    new_user_profile = UserProfile(
        user=new_user,
        full_name=full_name,
        date_of_birth=dob
        # Other UserProfile fields will default to None or their specified defaults
    )
    _user_profiles_db.append(new_user_profile)

    print(f"User '{username}' ({role}) created successfully by admin '{admin_user.username}'. Profile also created.")
    return new_user

def assign_role_by_admin(admin_user, target_username, new_role):
    """
    Assigns a new role to a user, callable by an admin.
    """
    if not admin_user or admin_user.role != UserRole.ADMIN:
        print(f"Error: User {admin_user.username if admin_user else 'Unknown'} does not have ADMIN privileges to assign roles.")
        return False

    target_user = None
    for user_in_db in _users_db:
        if user_in_db.username == target_username:
            target_user = user_in_db
            break
    
    if not target_user:
        print(f"Error: User '{target_username}' not found.")
        return False

    # Validate new_role
    if new_role not in [UserRole.ADMIN, UserRole.ASSISTANT_ADMIN, UserRole.COACH, UserRole.PLAYER]:
        print(f"Error: Invalid role '{new_role}'.")
        return False

    target_user.role = new_role
    print(f"Role for user '{target_username}' successfully updated to '{new_role}' by admin '{admin_user.username}'.")
    return True

# --- Helper function to print user details ---
def print_all_users_details():
    print("\n--- Current Users in Database ---")
    if not _users_db:
        print("No users in the database.")
        return
    for user in _users_db:
        profile = next((p for p in _user_profiles_db if p.user == user), None)
        profile_info = ""
        if profile:
            profile_info = f", Full Name: {profile.full_name}, DoB: {profile.date_of_birth}"
            
        print(f"  Username: {user.username}, Email: {user.email}, Role: {user.role}{profile_info}")
    print("---------------------------------")

# --- Main execution block ---
if __name__ == '__main__':
    # 1. Create a sample Admin user and their profile (manually for simulation)
    admin_user_obj = User(username="SuperAdmin", email="superadmin@example.com", role=UserRole.ADMIN)
    admin_user_obj.set_password("adminpass123")
    _users_db.append(admin_user_obj)
    
    admin_profile = UserProfile(
        user=admin_user_obj,
        full_name="Administrator Prime",
        date_of_birth=datetime.date(1980, 1, 1)
    )
    _user_profiles_db.append(admin_profile)
    
    print(f"Simulated Admin User '{admin_user_obj.username}' created.")
    print_all_users_details()

    # 2. Simulate Admin adding a new Player user
    print("\n--- Admin adding a new Player ---")
    new_player = add_user_by_admin(
        admin_user=admin_user_obj,
        username="NewPlayer01",
        email="player01@example.com",
        password="playerpass",
        role=UserRole.PLAYER,
        full_name="John Doe",
        date_of_birth_str="1995-06-20"
    )
    print_all_users_details()

    # Test adding a user with an existing username
    print("\n--- Admin attempting to add user with existing username ---")
    add_user_by_admin(
        admin_user=admin_user_obj,
        username="NewPlayer01", # Existing username
        email="anotherplayer@example.com",
        password="pass",
        role=UserRole.PLAYER,
        full_name="Jane Doe",
        date_of_birth_str="1998-11-10"
    )
    print_all_users_details()

    # 3. Simulate Admin changing the role of the newly added user to Coach
    if new_player: # Only if player creation was successful
        print(f"\n--- Admin changing role of '{new_player.username}' to Coach ---")
        role_change_success = assign_role_by_admin(
            admin_user=admin_user_obj,
            target_username=new_player.username,
            new_role=UserRole.COACH
        )
        print_all_users_details()

        # Test assigning an invalid role
        print(f"\n--- Admin attempting to assign an invalid role to '{new_player.username}' ---")
        assign_role_by_admin(
            admin_user=admin_user_obj,
            target_username=new_player.username,
            new_role="SuperPlayer" # Invalid role
        )
        print_all_users_details()

    # Test assigning role to a non-existent user
    print("\n--- Admin attempting to assign role to non-existent user ---")
    assign_role_by_admin(
        admin_user=admin_user_obj,
        target_username="GhostUser",
        new_role=UserRole.PLAYER
    )
    print_all_users_details()
    
    # Test action by non-admin
    non_admin_user = User(username="NotAnAdmin", email="nota@example.com", role=UserRole.PLAYER)
    non_admin_user.set_password("pass")
    _users_db.append(non_admin_user) # Add to db for the test
    non_admin_profile = UserProfile(user=non_admin_user, full_name="Normal User")
    _user_profiles_db.append(non_admin_profile)
    
    print("\n--- Non-admin attempting to add a user ---")
    add_user_by_admin(
        admin_user=non_admin_user,
        username="AttemptedUser",
        email="attempt@example.com",
        password="secure",
        role=UserRole.PLAYER,
        full_name="Try Hard",
        date_of_birth_str="2000-01-01"
    )
    print_all_users_details()
    
    print("\n--- End of admin_management.py simulation ---")
