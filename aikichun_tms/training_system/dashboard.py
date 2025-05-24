import datetime
from dateutil.relativedelta import relativedelta # type: ignore
from .models import User, UserProfile, Team, Subscription, UserRole, Technique, PlayerTechniqueScore, Notification
# For dashboard.py to interact with notifications, we'll use functions from notification_system
# In a real application, these would be proper module imports.
# For this simulation, we will make direct calls to functions assuming they are accessible,
# or re-define simplified versions if needed for the simulation flow.
# Let's assume for now notification_system functions can be called.
# We'll also need a shared notification database or pass it around.

# --- Shared Data Structures (for simulation across modules if run in a coordinated way) ---
# These would typically be managed by a central application instance or database.
_sim_notifications_db_for_dashboard = [] # This will be populated by simulate_data
_sim_next_notification_id_for_dashboard = 1 # Manage ID generation for dashboard-driven simulation

# --- Data Simulation ---
# In-memory "database" for techniques for this simulation
_sim_techniques_db = []


# --- Notification Simulation Helpers (could be imported from notification_system.py) ---
# To avoid direct dependency in this step, we can simulate the sending part here,
# which reflects what would happen if an Admin used notification_system.py,
# and then dashboard.py would use the "get" and "mark as read" functions.

def _simulate_send_notification_to_user_for_dashboard(target_user_profile, message):
    global _sim_notifications_db_for_dashboard, _sim_next_notification_id_for_dashboard
    notification = Notification(
        notification_id=_sim_next_notification_id_for_dashboard,
        recipient_user_profile=target_user_profile,
        message=message,
        created_at=datetime.datetime.now(),
        is_read=False
    )
    _sim_notifications_db_for_dashboard.append(notification)
    _sim_next_notification_id_for_dashboard += 1
    # print(f"Simulated send: Notification '{notification.notification_id}' to user '{target_user_profile.full_name}'.")
    return notification

def _simulate_send_broadcast_notification_for_dashboard(message, all_user_profiles):
    global _sim_notifications_db_for_dashboard, _sim_next_notification_id_for_dashboard
    created_notifications = []
    for profile in all_user_profiles:
        notification = Notification(
            notification_id=_sim_next_notification_id_for_dashboard,
            recipient_user_profile=profile,
            message=message,
            created_at=datetime.datetime.now(),
            is_read=False
        )
        _sim_notifications_db_for_dashboard.append(notification)
        created_notifications.append(notification)
        _sim_next_notification_id_for_dashboard += 1
        # print(f"Simulated broadcast: Notification '{notification.notification_id}' for '{profile.full_name}'.")
    return created_notifications

# --- Notification Interaction Functions (conceptual equivalent of notification_system.py functions) ---
def get_unread_notifications_for_user_from_sim_db(user_profile):
    """Retrieves unread notifications for a user from the shared simulation DB."""
    return [
        n for n in _sim_notifications_db_for_dashboard
        if n.recipient_user_profile == user_profile and not n.is_read
    ]

def mark_notification_as_read_in_sim_db(user_profile, notification_id):
    """Marks a notification as read in the shared simulation DB."""
    for notification in _sim_notifications_db_for_dashboard:
        if notification.notification_id == notification_id and notification.recipient_user_profile == user_profile:
            if not notification.is_read:
                notification.is_read = True
                return True
    return False


def _add_sim_technique(name, description, level, section):
    """Helper to add techniques to our in-memory DB for simulation."""
    # Check if a technique with the same name already exists
    for existing_technique in _sim_techniques_db:
        if existing_technique.name == name:
            return existing_technique # Return existing if duplicate for simulation purposes
    
    tech = Technique(name=name, description=description, level=level, section=section)
    _sim_techniques_db.append(tech)
    return tech

def simulate_data():
    """Creates and returns sample data for testing the dashboard."""
    global _sim_techniques_db, _sim_notifications_db_for_dashboard, _sim_next_notification_id_for_dashboard
    _sim_techniques_db = [] # Clear for fresh simulation run
    _sim_notifications_db_for_dashboard = [] # Clear for fresh simulation run
    _sim_next_notification_id_for_dashboard = 1


    # Create Users
    coach_user = User(username="CoachLee", email="coach@example.com", role=UserRole.COACH)
    coach_user.set_password("coachpass")
    
    team_leader_user = User(username="LeaderKim", email="leader@example.com", role=UserRole.PLAYER)
    team_leader_user.set_password("leaderpass")

    player_user = User(username="PlayerPark", email="player@example.com", role=UserRole.PLAYER)
    player_user.set_password("playerpass")

    # Create Team
    main_team = Team(name="Flying Dragons", branch_name="Main Branch")
    
    # Simulate some Techniques
    tech1 = _add_sim_technique("Basic Stance", "Fundamental ready stance.", "Kyu 10", "Basics")
    tech2 = _add_sim_technique("Front Kick", "Mae Geri - basic front kick.", "Kyu 9", "Kicking")
    tech3 = _add_sim_technique("Wrist Lock Alpha", "Kotegaeshi variation.", "Kyu 8", "Joint Locks")
    tech4 = _add_sim_technique("Shoulder Throw", "Seoi Nage variation.", "Kyu 7", "Throws")


    # Create Player's UserProfile
    player_profile = UserProfile(
        user=player_user,
        full_name="Park Ji-Sung",
        photo_url="http://example.com/path/to/player_park_photo.jpg",
        date_of_birth=datetime.date(1990, 5, 15),
        job="Software Developer",
        height_cm=175,
        weight_kg=70.5,
        children_details=[{'name': 'Park Min-Jun', 'age': 5}, {'name': 'Park Seo-yeon', 'age': 8}],
        membership_level="Gold",
        training_start_date=datetime.date(2022, 1, 10),
        team=main_team,
        coach=coach_user, 
        team_leader=team_leader_user,
        speed_level="M"
    )

    # Create Subscription for the player
    subscription_start = datetime.date.today() - datetime.timedelta(days=180) # Approx 6 months ago
    subscription_end = datetime.date.today() + datetime.timedelta(days=185) # Approx 6 months from now
    player_subscription = Subscription(
        user_profile=player_profile,
        start_date=subscription_start,
        end_date=subscription_end,
        status="active"
    )
    
    # Create PlayerTechniqueScores for the player
    player_scores = []
    # Technique 1: Newly learned, all scores 0
    score1 = PlayerTechniqueScore(player_profile=player_profile, technique=tech1)
    player_scores.append(score1)

    # Technique 2: Some progress
    score2 = PlayerTechniqueScore(player_profile=player_profile, technique=tech2, 
                                  score_slot_1=5, score_slot_2=3) # Example scores
    player_scores.append(score2)

    # Technique 3: Mastered (example)
    score3 = PlayerTechniqueScore(player_profile=player_profile, technique=tech3,
                                  score_slot_1=10, score_slot_2=10, score_slot_3=10, 
                                  score_slot_4=10, score_slot_5=10)
    player_scores.append(score3)
    
    # Note: tech4 is not yet learned by PlayerPark

    # Create PlayerTechniqueScores for the player
    player_scores = []
    # Technique 1: Newly learned, all scores 0
    score1 = PlayerTechniqueScore(player_profile=player_profile, technique=tech1)
    player_scores.append(score1)

    # Technique 2: Some progress
    score2 = PlayerTechniqueScore(player_profile=player_profile, technique=tech2, 
                                  score_slot_1=5, score_slot_2=3) # Example scores
    player_scores.append(score2)

    # Technique 3: Mastered (example)
    score3 = PlayerTechniqueScore(player_profile=player_profile, technique=tech3,
                                  score_slot_1=10, score_slot_2=10, score_slot_3=10, 
                                  score_slot_4=10, score_slot_5=10)
    player_scores.append(score3)
    
    # Note: tech4 is not yet learned by PlayerPark

    # Simulate some notifications being sent (as if by an Admin)
    # These will populate _sim_notifications_db_for_dashboard
    all_sim_profiles = [player_profile] # In a broader simulation, this list would be more complete
    if coach_user:
        # Create a dummy profile for coach to be in all_sim_profiles if needed for broadcast test
        coach_profile_sim = UserProfile(user=coach_user, full_name=coach_user.username)
        all_sim_profiles.append(coach_profile_sim)

    _simulate_send_notification_to_user_for_dashboard(
        target_user_profile=player_profile,
        message="Welcome to your dashboard, Park Ji-Sung! Your next session is scheduled."
    )
    _simulate_send_broadcast_notification_for_dashboard(
        message="Reminder: The dojo will be closed next Monday for a public holiday.",
        all_user_profiles=all_sim_profiles # Simulating broadcast to available profiles
    )


    # In a real app, these would be saved to a DB. For simulation, we can return them.
    # For notifications, get_player_dashboard_data will fetch from _sim_notifications_db_for_dashboard
    return player_profile, player_subscription, player_scores, [coach_user, team_leader_user, player_user], main_team, _sim_techniques_db

# --- Dashboard Logic ---
def get_player_dashboard_data(user_profile, subscription, player_technique_scores):
    """
    Retrieves and structures data for a player's dashboard.
    """
    dashboard_data = {}

    # Personal Details
    dashboard_data['personal_details'] = {
        "full_name": user_profile.full_name,
        "photo_url": user_profile.photo_url,
        "job": user_profile.job,
        "height_cm": user_profile.height_cm,
        "weight_kg": user_profile.weight_kg,
        "children": user_profile.children_details
    }
    if user_profile.date_of_birth:
        today = datetime.date.today()
        age = today.year - user_profile.date_of_birth.year - \
              ((today.month, today.day) < (user_profile.date_of_birth.month, user_profile.date_of_birth.day))
        dashboard_data['personal_details']['age'] = age
    else:
        dashboard_data['personal_details']['age'] = "N/A"

    # Training Details
    dashboard_data['training_details'] = {
        "membership_level": user_profile.membership_level,
        "training_start_date": user_profile.training_start_date.strftime("%Y-%m-%d") if user_profile.training_start_date else "N/A",
        "team_name": user_profile.team.name if user_profile.team else "N/A",
        "coach_name": user_profile.coach.username if user_profile.coach else "N/A",
        "team_leader_name": user_profile.team_leader.username if user_profile.team_leader else "N/A",
        "speed_level": user_profile.speed_level
    }

    # Subscription Status
    if subscription and subscription.end_date:
        time_left = subscription.end_date - datetime.date.today()
        if time_left.days < 0:
            dashboard_data['subscription_status'] = {
                "status": "Expired",
                "renewal_info": f"Expired on {subscription.end_date.strftime('%Y-%m-%d')}"
            }
        else:
            try:
                # Use dateutil.relativedelta for a more human-readable difference
                delta = relativedelta(subscription.end_date, datetime.date.today())
                parts = []
                if delta.years > 0: parts.append(f"{delta.years} year(s)")
                if delta.months > 0: parts.append(f"{delta.months} month(s)")
                if delta.days > 0: parts.append(f"{delta.days} day(s)")
                time_left_str = ", ".join(parts) if parts else "Today"
                dashboard_data['subscription_status'] = {
                    "status": subscription.status,
                    "renewal_info": f"Renews in {time_left_str} (on {subscription.end_date.strftime('%Y-%m-%d')})"
                }
            except NameError: # dateutil.relativedelta not available
                 dashboard_data['subscription_status'] = {
                    "status": subscription.status,
                    "renewal_info": f"{time_left.days} days left (until {subscription.end_date.strftime('%Y-%m-%d')})"
                }

    else:
        dashboard_data['subscription_status'] = {
            "status": "N/A",
            "renewal_info": "No subscription information found."
        }

    # Learned Techniques
    dashboard_data['learned_techniques'] = []
    if player_technique_scores:
        for pts in player_technique_scores:
            total_score = (pts.score_slot_1 + pts.score_slot_2 + pts.score_slot_3 +
                           pts.score_slot_4 + pts.score_slot_5)
            dashboard_data['learned_techniques'].append({
                "name": pts.technique.name,
                "description": pts.technique.description,
                "level": pts.technique.level,
                "section": pts.technique.section,
                "scores": [pts.score_slot_1, pts.score_slot_2, pts.score_slot_3, 
                           pts.score_slot_4, pts.score_slot_5],
                "total_score": total_score
            })
            
    # Unread Notifications
    dashboard_data['unread_notifications'] = []
    unread_notifs = get_unread_notifications_for_user_from_sim_db(user_profile)
    if unread_notifs:
        for notif in unread_notifs:
            dashboard_data['unread_notifications'].append({
                "notification_id": notif.notification_id,
                "message": notif.message,
                "created_at": notif.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
            
    return dashboard_data

def print_dashboard(dashboard_data):
    """Prints the dashboard data in a readable format."""
    print("\n--- Player Dashboard ---")

    if 'personal_details' in dashboard_data:
        print("\n[Personal Details]")
        pd = dashboard_data['personal_details']
        print(f"  Name: {pd.get('full_name', 'N/A')}")
        print(f"  Age: {pd.get('age', 'N/A')}")
        print(f"  Photo: {pd.get('photo_url', 'N/A')}")
        print(f"  Job: {pd.get('job', 'N/A')}")
        print(f"  Height: {pd.get('height_cm', 'N/A')} cm")
        print(f"  Weight: {pd.get('weight_kg', 'N/A')} kg")
        if pd.get('children'):
            print("  Children:")
            for child in pd['children']:
                print(f"    - {child.get('name', 'N/A')} (Age: {child.get('age', 'N/A')})")

    if 'training_details' in dashboard_data:
        print("\n[Training Details]")
        td = dashboard_data['training_details']
        print(f"  Membership Level: {td.get('membership_level', 'N/A')}")
        print(f"  Training Start Date: {td.get('training_start_date', 'N/A')}")
        print(f"  Team: {td.get('team_name', 'N/A')}")
        print(f"  Coach: {td.get('coach_name', 'N/A')}")
        print(f"  Team Leader: {td.get('team_leader_name', 'N/A')}")
        print(f"  Speed Level: {td.get('speed_level', 'N/A')}")

    if 'subscription_status' in dashboard_data:
        print("\n[Subscription Status]")
        ss = dashboard_data['subscription_status']
        print(f"  Status: {ss.get('status', 'N/A')}")
        print(f"  Details: {ss.get('renewal_info', 'N/A')}")

    if 'learned_techniques' in dashboard_data and dashboard_data['learned_techniques']:
        print("\n[Learned Techniques]")
        for tech_info in dashboard_data['learned_techniques']:
            print(f"  Technique: {tech_info['name']} (Level: {tech_info['level']}, Section: {tech_info['section']})")
            print(f"    Description: {tech_info['description']}")
            print(f"    Scores: {tech_info['scores']}")
            print(f"    Total Score: {tech_info['total_score']}")
    else:
        print("\n[Learned Techniques]")
        print("  No techniques scores recorded yet.")

    if 'unread_notifications' in dashboard_data and dashboard_data['unread_notifications']:
        print("\n[Unread Notifications]")
        for notif_info in dashboard_data['unread_notifications']:
            print(f"  ID: {notif_info['notification_id']} (Received: {notif_info['created_at']})")
            print(f"    Message: {notif_info['message']}")
    else:
        print("\n[Unread Notifications]")
        print("  No new notifications.")
        
    print("\n--- End of Dashboard ---")

# --- Main Execution ---
if __name__ == '__main__':
    # 1. Simulate data
    # This will now also populate _sim_notifications_db_for_dashboard via _simulate_send... functions
    player_profile, player_subscription, player_scores, _, _, _ = simulate_data()

    # Ensure we have a player profile to display
    if player_profile and player_profile.user.role == UserRole.PLAYER:
        # 2. Get dashboard data for the player (includes fetching unread notifications)
        print("Fetching dashboard for the first time (notifications should appear as unread):")
        dashboard_info_first_view = get_player_dashboard_data(player_profile, player_subscription, player_scores)
        
        # 3. Print the dashboard information
        print_dashboard(dashboard_info_first_view)
        
        # 4. Simulate marking displayed notifications as read
        notifications_marked_read_count = 0
        if dashboard_info_first_view.get('unread_notifications'):
            print("\n--- Marking displayed notifications as read ---")
            for notif_data in dashboard_info_first_view['unread_notifications']:
                if mark_notification_as_read_in_sim_db(player_profile, notif_data['notification_id']):
                    notifications_marked_read_count +=1
            if notifications_marked_read_count > 0:
                print(f"{notifications_marked_read_count} notification(s) marked as read for {player_profile.full_name}.")
            else:
                print("No notifications were marked as read (or none to mark).")
        
        # 5. Fetch and print dashboard again to show notifications are gone
        print("\nFetching dashboard for the second time (notifications should be marked as read):")
        dashboard_info_second_view = get_player_dashboard_data(player_profile, player_subscription, player_scores)
        print_dashboard(dashboard_info_second_view)

    else:
        print("Could not find a sample player to display the dashboard.")

    print("\nNote: If 'relativedelta' is mentioned as not available, the 'python-dateutil' library needs to be installed.")
    print("You can typically install it using: pip install python-dateutil")
