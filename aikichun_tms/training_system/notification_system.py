import datetime
from .models import User, UserRole, UserProfile, Notification, Team

# Simulate Notification Database
_notifications_db = []  # Stores Notification objects
_next_notification_id = 1

# --- Admin Action Functions ---

def send_notification_to_user(admin_user, target_user_profile, message):
    """
    Sends a notification to a specific user profile.
    Callable by an Admin.
    """
    global _next_notification_id
    if not admin_user or admin_user.role != UserRole.ADMIN:
        print(f"Error: User {admin_user.username if admin_user else 'Unknown'} does not have ADMIN privileges to send notifications.")
        return None

    if not target_user_profile:
        print("Error: Target user profile cannot be None.")
        return None

    notification = Notification(
        notification_id=_next_notification_id,
        recipient_user_profile=target_user_profile,
        message=message,
        created_at=datetime.datetime.now(),
        is_read=False
    )
    _notifications_db.append(notification)
    _next_notification_id += 1
    print(f"Notification '{notification.notification_id}' sent to user '{target_user_profile.full_name}' by '{admin_user.username}'.")
    return notification

def send_broadcast_notification(admin_user, message, all_user_profiles):
    """
    Sends a notification to all user profiles.
    Callable by an Admin.
    """
    global _next_notification_id
    if not admin_user or admin_user.role != UserRole.ADMIN:
        print(f"Error: User {admin_user.username if admin_user else 'Unknown'} does not have ADMIN privileges to send broadcast notifications.")
        return []

    if not all_user_profiles:
        print("Warning: No user profiles provided for broadcast.")
        return []

    created_notifications = []
    # Design Choice: Creating individual notifications for each user for clear dashboard display.
    # Alternative: A single notification with recipient_user_profile=None and recipient_team=None,
    # interpreted as broadcast. This would save DB space but might complicate individual 'is_read' status.
    print(f"Admin '{admin_user.username}' initiating broadcast: '{message}'")
    for profile in all_user_profiles:
        notification = Notification(
            notification_id=_next_notification_id,
            recipient_user_profile=profile,
            message=message, # Same message for all
            created_at=datetime.datetime.now(),
            is_read=False
        )
        _notifications_db.append(notification)
        created_notifications.append(notification)
        _next_notification_id += 1
        print(f"  Broadcast notification '{notification.notification_id}' created for '{profile.full_name}'.")
    
    print(f"Broadcast completed. {len(created_notifications)} notifications sent.")
    return created_notifications

def send_team_notification(admin_user, target_team, message, team_member_profiles):
    """
    Sends a notification to all members of a specific team.
    Callable by an Admin.
    `team_member_profiles` is a list of UserProfile objects for members of target_team.
    """
    global _next_notification_id
    if not admin_user or admin_user.role != UserRole.ADMIN:
        print(f"Error: User {admin_user.username if admin_user else 'Unknown'} does not have ADMIN privileges to send team notifications.")
        return []

    if not target_team:
        print("Error: Target team cannot be None.")
        return []
    if not team_member_profiles:
        print(f"Warning: No members found for team '{target_team.name}' to send notification.")
        return []

    created_notifications = []
    print(f"Admin '{admin_user.username}' initiating team notification for team '{target_team.name}': '{message}'")
    for profile in team_member_profiles:
        # In a more complex system, one might create a single notification object linked to a team_id.
        # For this simulation, sticking to individual notifications for simplicity in 'is_read' handling.
        notification = Notification(
            notification_id=_next_notification_id,
            recipient_user_profile=profile, # Could also set recipient_team = target_team
            message=f"[Team: {target_team.name}] {message}", # Prepending team name for clarity
            created_at=datetime.datetime.now(),
            is_read=False
        )
        _notifications_db.append(notification)
        created_notifications.append(notification)
        _next_notification_id += 1
        print(f"  Team notification '{notification.notification_id}' created for member '{profile.full_name}'.")

    print(f"Team notification for '{target_team.name}' completed. {len(created_notifications)} notifications sent.")
    return created_notifications


# --- User Action Functions (for direct use or by other modules) ---

def get_unread_notifications_for_user(user_profile):
    """
    Retrieves unread notifications for a specific user profile.
    """
    if not user_profile:
        return []
    
    return [
        n for n in _notifications_db 
        if n.recipient_user_profile == user_profile and not n.is_read
    ]

def mark_notification_as_read(user_profile, notification_id):
    """
    Marks a specific notification as read for a user.
    """
    if not user_profile:
        return False
        
    for notification in _notifications_db:
        if notification.notification_id == notification_id and notification.recipient_user_profile == user_profile:
            if not notification.is_read:
                notification.is_read = True
                print(f"Notification ID {notification_id} marked as read for {user_profile.full_name}.")
                return True
            else:
                # Already read, still counts as success for this action's purpose
                # print(f"Notification ID {notification_id} was already read by {user_profile.full_name}.")
                return True 
    print(f"Error: Notification ID {notification_id} not found or does not belong to {user_profile.full_name}.")
    return False

def get_all_notifications_for_user_for_testing(user_profile):
    """Helper for testing: gets all notifications for a user, read or unread."""
    return [n for n in _notifications_db if n.recipient_user_profile == user_profile]

def clear_all_notifications_for_testing():
    """Helper for testing: clears the notification database."""
    global _notifications_db, _next_notification_id
    _notifications_db = []
    _next_notification_id = 1
    print("All notifications cleared for testing.")


# --- Main execution block (for demonstration) ---
if __name__ == '__main__':
    # 0. Clear previous test data
    clear_all_notifications_for_testing()

    # 1. Create sample Users and UserProfiles (simplified, no DB for users here)
    admin = User(username="NotifyAdmin", email="notify@admin.com", role=UserRole.ADMIN)
    player_profile_alice = UserProfile(user=User("Alice", "alice@example.com", UserRole.PLAYER), full_name="Alice Wonderland")
    player_profile_bob = UserProfile(user=User("Bob", "bob@example.com", UserRole.PLAYER), full_name="Bob The Builder")
    
    # For team notification
    team_alpha = Team(name="Alpha Team")
    # Assign profiles to team (conceptual, UserProfile.team would be set in a real app)
    player_profile_alice.team = team_alpha 
    # player_profile_bob is not in Alpha Team for this test

    all_profiles = [player_profile_alice, player_profile_bob]
    alpha_team_members = [player_profile_alice]


    print("\n--- Testing Notification System ---")

    # 2. Admin sends a specific notification to Alice
    print("\n1. Admin sending notification to Alice:")
    send_notification_to_user(admin, player_profile_alice, "Your training session is confirmed for tomorrow.")

    # 3. Admin sends a broadcast notification
    print("\n2. Admin sending broadcast notification:")
    send_broadcast_notification(admin, "System maintenance tonight at 2 AM.", all_profiles)
    
    # 4. Admin sends a team notification to Alpha Team
    print("\n3. Admin sending team notification to Alpha Team:")
    send_team_notification(admin, team_alpha, "Team Alpha meeting scheduled for Friday.", alpha_team_members)


    # 5. Alice views her unread notifications
    print(f"\n4. Alice's unread notifications ({player_profile_alice.full_name}):")
    alice_unread = get_unread_notifications_for_user(player_profile_alice)
    if alice_unread:
        for notif in alice_unread:
            print(f"  ID: {notif.notification_id}, From: System (Admin), Read: {notif.is_read}, Message: {notif.message}")
    else:
        print("  No unread notifications for Alice.")

    # 6. Bob views his unread notifications
    print(f"\n5. Bob's unread notifications ({player_profile_bob.full_name}):")
    bob_unread = get_unread_notifications_for_user(player_profile_bob)
    if bob_unread:
        for notif in bob_unread:
            print(f"  ID: {notif.notification_id}, From: System (Admin), Read: {notif.is_read}, Message: {notif.message}")
    else:
        print("  No unread notifications for Bob.")

    # 7. Alice marks one of her notifications as read
    if alice_unread:
        print(f"\n6. Alice marking notification ID {alice_unread[0].notification_id} as read:")
        mark_notification_as_read(player_profile_alice, alice_unread[0].notification_id)
    
        print(f"\n7. Alice's unread notifications after marking one as read:")
        alice_unread_after_mark = get_unread_notifications_for_user(player_profile_alice)
        if alice_unread_after_mark:
            for notif in alice_unread_after_mark:
                print(f"  ID: {notif.notification_id}, Read: {notif.is_read}, Message: {notif.message}")
        else:
            print("  No unread notifications for Alice.")
            
    # 8. Attempting to mark a non-existent notification
    print("\n8. Alice attempting to mark non-existent notification ID 999 as read:")
    mark_notification_as_read(player_profile_alice, 999)
    
    print("\n--- All notifications for Alice (for verification) ---")
    all_alice_notifs = get_all_notifications_for_user_for_testing(player_profile_alice)
    for notif in all_alice_notifs:
        print(f"  ID: {notif.notification_id}, Read: {notif.is_read}, Message: {notif.message}")

    print("\n--- All notifications for Bob (for verification) ---")
    all_bob_notifs = get_all_notifications_for_user_for_testing(player_profile_bob)
    for notif in all_bob_notifs:
        print(f"  ID: {notif.notification_id}, Read: {notif.is_read}, Message: {notif.message}")
        
    print("\n--- End of notification_system.py simulation ---")
