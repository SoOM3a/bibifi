import datetime
from dateutil.relativedelta import relativedelta # type: ignore
from .models import User, UserRole, UserProfile, Subscription, SubscriptionStatus

# Simulate Databases
_users_db = []
_user_profiles_db = []
_subscriptions_db = []

# --- Helper: Find User/Profile ---
def _find_user_by_username(username):
    for u in _users_db:
        if u.username == username:
            return u
    return None

def _find_profile_by_user(user):
    for p in _user_profiles_db:
        if p.user == user:
            return p
    return None

def _find_subscription_by_profile_and_id(user_profile, subscription_id):
    # For simplicity, using list index as ID in this simulation if subscription_id is int
    # In a real system, subscription would have a unique ID property.
    # Here we'll find the first subscription for the user_profile that matches.
    # A more robust ID system would be needed for multiple subscriptions per user.
    
    # Let's assume for this simulation, a user has at most one subscription for simplicity,
    # or the subscription_id is a direct reference to the object or a unique property.
    # For this example, we'll make subscription_id an index if int, or find first if None.
    
    found_sub = None
    if isinstance(subscription_id, int) and 0 <= subscription_id < len(_subscriptions_db):
        # Treat as index if it's a valid int index
        sub_at_index = _subscriptions_db[subscription_id]
        if sub_at_index.user_profile == user_profile:
            found_sub = sub_at_index
    else: # Fallback to finding the first subscription for the user if no valid ID given
        for sub in _subscriptions_db:
            if sub.user_profile == user_profile:
                found_sub = sub # Return first one found for this user
                break 
    return found_sub


# --- Player Action Function ---
def player_submit_renewal_proof(player_user_profile, subscription_id, proof_file_path):
    """
    Allows a player to submit proof of payment for their subscription renewal.
    """
    if not player_user_profile or player_user_profile.user.role != UserRole.PLAYER:
        print("Error: Only a logged-in Player can submit renewal proof.")
        return False

    subscription = _find_subscription_by_profile_and_id(player_user_profile, subscription_id)

    if not subscription:
        print(f"Error: Subscription ID '{subscription_id}' not found for player {player_user_profile.full_name}.")
        return False

    # Define conditions under which renewal proof can be submitted
    # e.g., expired, or active but nearing expiry (e.g., within 30 days)
    is_renewable = False
    if subscription.status == SubscriptionStatus.EXPIRED:
        is_renewable = True
    elif subscription.status == SubscriptionStatus.ACTIVE:
        days_to_expiry = (subscription.end_date - datetime.date.today()).days
        if 0 <= days_to_expiry <= 30: # Nearing expiry (within 30 days) or expired today
            is_renewable = True
        elif days_to_expiry < 0: # Already expired
             subscription.status = SubscriptionStatus.EXPIRED # Correct status if needed
             is_renewable = True
    elif subscription.status == SubscriptionStatus.PENDING_RENEWAL: # Already submitted
        print(f"Notice: Subscription for {player_user_profile.full_name} is already pending renewal review.")
        # Optionally allow re-submission:
        # subscription.proof_of_payment_url = proof_file_path
        # print(f"Proof of payment re-submitted for {player_user_profile.full_name}.")
        # return True
        return False # For now, don't allow re-submission if already pending

    if is_renewable:
        subscription.proof_of_payment_url = proof_file_path
        subscription.status = SubscriptionStatus.PENDING_APPROVAL # Changed from PENDING_RENEWAL for clarity
        print(f"Success: Renewal proof '{proof_file_path}' submitted for {player_user_profile.full_name}. Status changed to '{SubscriptionStatus.PENDING_APPROVAL}'.")
        return True
    else:
        print(f"Error: Subscription for {player_user_profile.full_name} (Status: {subscription.status}) is not currently eligible for renewal proof submission.")
        return False

# --- Admin/Assistant Admin Action Functions ---
def admin_view_pending_renewals(requesting_user):
    """
    Allows Admins or Assistant Admins to view subscriptions pending renewal approval.
    """
    if not requesting_user or (requesting_user.role != UserRole.ADMIN and requesting_user.role != UserRole.ASSISTANT_ADMIN):
        print(f"Error: User {requesting_user.username if requesting_user else 'Unknown'} does not have privileges to view pending renewals.")
        return []

    pending_renewals = [
        sub for sub in _subscriptions_db if sub.status == SubscriptionStatus.PENDING_APPROVAL
    ]

    if not pending_renewals:
        print("No subscriptions are currently pending renewal approval.")
        return []

    print(f"\n--- Subscriptions Pending Renewal Approval (Viewed by: {requesting_user.username}) ---")
    for sub in pending_renewals:
        print_subscription_details(sub, print_profile_details=True)
    print("----------------------------------------------------")
    return pending_renewals

def admin_approve_subscription_renewal(admin_user, subscription_id_or_object):
    """
    Approves a subscription renewal, setting it to active and extending its end date.
    Callable by Admin or Assistant Admin.
    """
    if not admin_user or (admin_user.role != UserRole.ADMIN and admin_user.role != UserRole.ASSISTANT_ADMIN):
        print(f"Error: User {admin_user.username if admin_user else 'Unknown'} does not have privileges to approve subscriptions.")
        return False

    subscription_to_approve = None
    if isinstance(subscription_id_or_object, Subscription):
        # Direct object passed
        if subscription_id_or_object in _subscriptions_db:
            subscription_to_approve = subscription_id_or_object
    elif isinstance(subscription_id_or_object, int):
        # ID (index for simulation) passed
        if 0 <= subscription_id_or_object < len(_subscriptions_db):
            subscription_to_approve = _subscriptions_db[subscription_id_or_object]
    
    if not subscription_to_approve:
        print(f"Error: Subscription ID/object '{subscription_id_or_object}' not found in database.")
        return False

    if subscription_to_approve.status != SubscriptionStatus.PENDING_APPROVAL:
        print(f"Error: Subscription for {subscription_to_approve.user_profile.full_name} (Status: {subscription_to_approve.status}) is not pending approval.")
        return False

    # Extend end_date logic
    today = datetime.date.today()
    if subscription_to_approve.end_date > today:
        # If old end_date is in the future, add 1 year to old end_date
        subscription_to_approve.end_date = subscription_to_approve.end_date + relativedelta(years=1)
    else:
        # If old end_date is in the past (expired), add 1 year to today
        subscription_to_approve.end_date = today + relativedelta(years=1)
        
    subscription_to_approve.status = SubscriptionStatus.ACTIVE
    subscription_to_approve.proof_of_payment_url = None # Clear proof URL

    print(f"Success: Subscription for {subscription_to_approve.user_profile.full_name} approved and activated by {admin_user.username}. New End Date: {subscription_to_approve.end_date.strftime('%Y-%m-%d')}.")
    return True

# --- Helper Function ---
def print_subscription_details(subscription, print_profile_details=False):
    """Prints details of a single subscription."""
    if not subscription:
        print("  Subscription details not found.")
        return
        
    profile_info = ""
    if print_profile_details and subscription.user_profile:
        profile_info = f" (Player: {subscription.user_profile.full_name}, User: {subscription.user_profile.user.username})"

    print(f"  Subscription for UserProfile{profile_info}:")
    print(f"    Start Date: {subscription.start_date}")
    print(f"    End Date: {subscription.end_date}")
    print(f"    Status: {subscription.status}")
    print(f"    Proof URL: {subscription.proof_of_payment_url if subscription.proof_of_payment_url else 'N/A'}")


# --- Main execution block ---
if __name__ == '__main__':
    # 1. Create sample Users and UserProfiles
    admin_user = User(username="MainAdmin", email="admin@example.com", role=UserRole.ADMIN)
    admin_user.set_password("adminpass")
    _users_db.append(admin_user)
    admin_profile = UserProfile(user=admin_user, full_name="Head Admin")
    _user_profiles_db.append(admin_profile)

    assistant_admin_user = User(username="AssistAdmin", email="assist@example.com", role=UserRole.ASSISTANT_ADMIN)
    assistant_admin_user.set_password("assistpass")
    _users_db.append(assistant_admin_user)
    assistant_admin_profile = UserProfile(user=assistant_admin_user, full_name="Assistant Admin")
    _user_profiles_db.append(assistant_admin_profile)
    
    player1_user = User(username="PlayerJane", email="jane@example.com", role=UserRole.PLAYER)
    player1_user.set_password("janepass")
    _users_db.append(player1_user)
    player1_profile = UserProfile(user=player1_user, full_name="Jane Doe")
    _user_profiles_db.append(player1_profile)

    player2_user = User(username="PlayerExpired", email="expired@example.com", role=UserRole.PLAYER)
    player2_user.set_password("expiredpass")
    _users_db.append(player2_user)
    player2_profile = UserProfile(user=player2_user, full_name="Old Timer")
    _user_profiles_db.append(player2_profile)

    print("Sample users and profiles created.")

    # 2. Create sample Subscriptions
    # Subscription for PlayerJane (active, nearing expiry)
    sub1_start = datetime.date.today() - datetime.timedelta(days=335) # Almost a year ago
    sub1_end = datetime.date.today() + datetime.timedelta(days=15) # Expires in 15 days
    subscription1 = Subscription(
        user_profile=player1_profile,
        start_date=sub1_start,
        end_date=sub1_end,
        status=SubscriptionStatus.ACTIVE
    )
    _subscriptions_db.append(subscription1)
    # For simulation, use index as ID
    sub1_id = _subscriptions_db.index(subscription1) 

    # Subscription for PlayerExpired (already expired)
    sub2_start = datetime.date.today() - datetime.timedelta(days=400)
    sub2_end = datetime.date.today() - datetime.timedelta(days=35) # Expired 35 days ago
    subscription2 = Subscription(
        user_profile=player2_profile,
        start_date=sub2_start,
        end_date=sub2_end,
        status=SubscriptionStatus.EXPIRED
    )
    _subscriptions_db.append(subscription2)
    sub2_id = _subscriptions_db.index(subscription2)

    print("\n--- Initial Subscriptions ---")
    print_subscription_details(subscription1)
    print_subscription_details(subscription2)
    print("---------------------------")

    # 3. Simulate PlayerJane submitting proof
    print(f"\n--- Player '{player1_profile.full_name}' submitting renewal proof ---")
    player_submit_renewal_proof(
        player_user_profile=player1_profile,
        subscription_id=sub1_id, 
        proof_file_path="/path/to/jane_payment_proof.pdf"
    )
    print_subscription_details(subscription1)
    
    # 4. Simulate PlayerExpired submitting proof
    print(f"\n--- Player '{player2_profile.full_name}' submitting renewal proof ---")
    player_submit_renewal_proof(
        player_user_profile=player2_profile,
        subscription_id=sub2_id,
        proof_file_path="/path/to/expired_payment_proof.jpg"
    )
    print_subscription_details(subscription2)

    # 5. Simulate Admin viewing pending renewals
    print("\n--- Admin viewing pending renewals ---")
    admin_view_pending_renewals(admin_user)

    # 6. Simulate Assistant Admin viewing pending renewals
    print("\n--- Assistant Admin viewing pending renewals ---")
    admin_view_pending_renewals(assistant_admin_user)

    # 7. Simulate Admin approving Jane's subscription (which was active but nearing expiry)
    print(f"\n--- Admin '{admin_user.username}' approving renewal for '{player1_profile.full_name}' (ID: {sub1_id}) ---")
    admin_approve_subscription_renewal(
        admin_user=admin_user,
        subscription_id_or_object=sub1_id 
    )
    print_subscription_details(subscription1, print_profile_details=True)

    # 8. Simulate Assistant Admin approving Old Timer's subscription (which was expired)
    print(f"\n--- Assistant Admin '{assistant_admin_user.username}' approving renewal for '{player2_profile.full_name}' (ID: {sub2_id}) ---")
    admin_approve_subscription_renewal(
        admin_user=assistant_admin_user,
        subscription_id_or_object=sub2_id
    )
    print_subscription_details(subscription2, print_profile_details=True)

    # 9. Test case: Admin attempting to approve a subscription that is already active (Jane's after approval)
    print(f"\n--- Admin '{admin_user.username}' attempting to re-approve '{player1_profile.full_name}'s already active subscription ---")
    admin_approve_subscription_renewal(
        admin_user=admin_user,
        subscription_id_or_object=subscription1 # Pass object this time
    )
    print_subscription_details(subscription1)
    
    # 10. Test case: A Player attempting to approve a subscription
    # Create a new pending subscription for this test
    player3_user = User(username="PlayerNew", email="new@example.com", role=UserRole.PLAYER)
    player3_user.set_password("newpass")
    _users_db.append(player3_user)
    player3_profile = UserProfile(user=player3_user, full_name="Newbie Nate")
    _user_profiles_db.append(player3_profile)
    
    sub3_start = datetime.date.today() - datetime.timedelta(days=5)
    sub3_end = datetime.date.today() - datetime.timedelta(days=2) # Expired
    subscription3 = Subscription(
        user_profile=player3_profile,
        start_date=sub3_start,
        end_date=sub3_end,
        status=SubscriptionStatus.PENDING_APPROVAL, # Directly set to pending for test
        proof_of_payment_url="/path/to/newbie_proof.pdf"
    )
    _subscriptions_db.append(subscription3)
    sub3_id = _subscriptions_db.index(subscription3)

    print(f"\n--- Player '{player1_user.username}' attempting to approve '{player3_profile.full_name}'s subscription (ID: {sub3_id}) ---")
    print("Original subscription details before attempt:")
    print_subscription_details(subscription3, print_profile_details=True)
    admin_approve_subscription_renewal(
        admin_user=player1_user, # Player trying to act as admin
        subscription_id_or_object=sub3_id
    )
    print("Subscription details after attempt (should be unchanged):")
    print_subscription_details(subscription3, print_profile_details=True)


    # 11. Test case: Submitting proof for a non-existent subscription (from previous tests, slightly adjusted)
    print("\n--- Player submitting proof for non-existent subscription ID ---")
    player_submit_renewal_proof(
        player_user_profile=player1_profile,
        subscription_id=9999, # Non-existent ID
        proof_file_path="/path/to/ghost_proof.pdf"
    )
    
    # 12. Test case: Submitting proof for a subscription that is not renewable (e.g., active and not near expiry - from previous tests)
    active_not_near_expiry_sub = Subscription(
        user_profile=player1_profile, # Another sub for Jane, e.g. a different type
        start_date=datetime.date.today() - datetime.timedelta(days=30),
        end_date=datetime.date.today() + datetime.timedelta(days=180), # Far from expiry
        status=SubscriptionStatus.ACTIVE
    )
    _subscriptions_db.append(active_not_near_expiry_sub)
    active_sub_id = _subscriptions_db.index(active_not_near_expiry_sub)

    print("\n--- Player submitting proof for active, non-expiring subscription ---")
    print_subscription_details(active_not_near_expiry_sub)
    player_submit_renewal_proof(
        player_user_profile=player1_profile,
        subscription_id=active_sub_id,
        proof_file_path="/path/to/unnecessary_proof.pdf"
    )
    print_subscription_details(active_not_near_expiry_sub) # Show it hasn't changed

    print("\n--- End of subscription_management.py simulation ---")
