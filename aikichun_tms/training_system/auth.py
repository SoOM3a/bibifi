# Placeholder for actual user data storage/querying
# In a real application, this would interact with a database.
_users_db = {} # Store users by username: User(username, email, role)

def register_user_for_testing(user_object, password):
    """
    Helper function to populate _users_db for testing.
    This is NOT part of the core auth logic for a real app.
    """
    user_object.set_password(password)
    _users_db[user_object.username] = user_object

def authenticate_user(username, password):
    """
    Authenticates a user.
    In a real system, this would query the database for the user.
    """
    user = _users_db.get(username)
    if user and user.check_password(password):
        return user
    return None

def login_user(user):
    """
    Logs in a user.
    In a real system, this would set up a session for the user.
    """
    if user:
        print(f"User {user.username} logged in.")
        # Placeholder for session management: current_user = user
    else:
        print("Login failed: User not provided.")


# Placeholder for current logged-in user (would be managed by session in a real app)
_current_user_session = {"user": None}

def set_current_user_for_testing(user):
    """Helper to simulate a user being logged in for testing role_required."""
    _current_user_session["user"] = user

def logout_user():
    """
    Logs out a user.
    In a real system, this would clear the session.
    """
    logged_out_username = None
    if _current_user_session["user"]:
        logged_out_username = _current_user_session["user"].username
    _current_user_session["user"] = None
    if logged_out_username:
        print(f"User {logged_out_username} logged out.")
    else:
        print("No user was logged in. Logout process simulated.")


def role_required(required_role):
    """
    Checks if the 'logged-in' user has the required role.
    This is a simplified version. In a real app, this would be a decorator
    that inspects the current session/request for user information.
    
    For this placeholder, it checks a conceptually 'logged-in' user.
    We'll use a helper function to 'log in' a user for testing this.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # In a real app, get user from session/request context
            current_user = _current_user_session.get("user") 
            
            if not current_user:
                print("Access denied: No user is logged in.")
                return False # Or raise an exception/redirect
            
            if current_user.role == required_role:
                print(f"Role '{required_role}' check passed for user {current_user.username}.")
                return func(*args, **kwargs) # Call the original function
            else:
                print(f"Access denied: User {current_user.username} (Role: {current_user.role}) does not have required role '{required_role}'.")
                return False # Or raise an exception/redirect
        return wrapper
    return decorator

from .models import User, UserRole # Use the actual User and UserRole from models.py

# Example usage of role_required (for testing purposes)
# @role_required(UserRole.ADMIN)
# def admin_only_action():
#     print("Admin action executed successfully!")

# @role_required(UserRole.PLAYER)
# def player_action():
#     print("Player action executed successfully!")

# This is just to ensure the file can be imported and basic structure is fine.
# Real testing would involve creating User instances and calling these functions.
if __name__ == '__main__':
    # This block is for basic, isolated testing of this file's contents.
    # It won't run when imported as a module.

    # Test user registration and authentication
    # We use the real User and UserRole from models.py
    test_admin = User(username="admin1", email="admin@example.com", role=UserRole.ADMIN)
    # Note: register_user_for_testing now expects a User object and will call its set_password
    register_user_for_testing(test_admin, "securepassword123") 
    
    test_player = User(username="player1", email="player@example.com", role=UserRole.PLAYER)
    register_user_for_testing(test_player, "playerpass")

    print("--- Testing Authentication ---")
    # authenticate_user will use the User's check_password method
    authenticated_user = authenticate_user("admin1", "securepassword123")
    if authenticated_user:
        print(f"Authentication successful for: {authenticated_user.username}")
        login_user(authenticated_user)
        set_current_user_for_testing(authenticated_user) # Simulate login for role_required
    else:
        print("Authentication failed for admin1.")

    authenticated_user_fail = authenticate_user("admin1", "wrongpassword")
    if not authenticated_user_fail:
        print("Authentication correctly failed for admin1 with wrong password.")

    print("\n--- Testing Role Required (as Admin) ---")
    
    @role_required(UserRole.ADMIN) # Use UserRole from models
    def an_admin_task():
        print("Executing admin task...")
        return True
    
    an_admin_task() # Should pass

    @role_required(UserRole.PLAYER) # Use UserRole from models
    def a_player_task_for_admin():
        print("Executing player task (should be denied for admin)...")
        return True

    a_player_task_for_admin() # Should be denied


    print("\n--- Simulate Player Login & Test Role ---")
    authenticated_player = authenticate_user("player1", "playerpass")
    if authenticated_player:
        login_user(authenticated_player) # Prints login message
        set_current_user_for_testing(authenticated_player) # "Logs in" the player for role_required
    
    @role_required(UserRole.PLAYER) # Use UserRole from models
    def another_player_task():
        print("Executing player task...")
        return True

    another_player_task() # Should pass if player1 is "logged in"

    @role_required(UserRole.ADMIN) # Use UserRole from models
    def another_admin_task_for_player():
        print("Executing admin task (should be denied for player)...")
        return True
    
    another_admin_task_for_player() # Should be denied

    print("\n--- Testing Logout ---")
    logout_user() # Logs out current user (player1)
    
    print("\n--- Testing Role Required (after logout) ---")
    set_current_user_for_testing(None) # Ensure no user is set as current
    
    @role_required(UserRole.ADMIN) # Use UserRole from models
    def task_after_logout():
        print("This should not execute if no one is logged in.")
        return True
    
    task_after_logout() # Should be denied as no one is logged in
    
    print("\n--- End of auth.py self-test ---")
