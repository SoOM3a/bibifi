import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Placeholder for framework's Model base class
class Model:
    pass

# User Roles
class UserRole:
    ADMIN = 'Admin'
    ASSISTANT_ADMIN = 'AssistantAdmin'
    COACH = 'Coach'
    PLAYER = 'Player'

class User(Model):
    def __init__(self, username, email, role):
        self.username = username
        self.email = email
        self.role = role
        self.password_hash = None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

class Team(Model):
    def __init__(self, name, branch_name=None):
        self.name = name                # String
        self.branch_name = branch_name  # String, nullable

class UserProfile(Model):
    def __init__(self, user, full_name, photo_url=None, date_of_birth=None, job=None, 
                 height_cm=None, weight_kg=None, children_details=None, 
                 membership_level=None, training_start_date=None, team=None, 
                 coach=None, team_leader=None, speed_level=None):
        self.user = user  # ForeignKey to User
        self.full_name = full_name # String
        self.photo_url = photo_url  # String
        self.date_of_birth = date_of_birth  # Date
        self.job = job  # String
        self.height_cm = height_cm  # Integer
        self.weight_kg = weight_kg  # Decimal
        self.children_details = children_details  # JSON or Text
        self.membership_level = membership_level  # String
        self.training_start_date = training_start_date  # Date
        self.team = team  # ForeignKey to Team, nullable
        self.coach = coach  # ForeignKey to User (where user.role is 'Coach'), nullable
        self.team_leader = team_leader  # ForeignKey to User (where user.role is 'Player'), nullable
        self.speed_level = speed_level  # String - S, M, G

class Technique(Model):
    def __init__(self, name, description, level, section):
        self.name = name              # String
        self.description = description  # Text
        self.level = level            # String or Integer
        self.section = section          # String

class PlayerTechniqueScore(Model):
    def __init__(self, player_profile, technique, score_slot_1=0, score_slot_2=0, 
                 score_slot_3=0, score_slot_4=0, score_slot_5=0):
        self.player_profile = player_profile  # ForeignKey to UserProfile
        self.technique = technique            # ForeignKey to Technique
        self.score_slot_1 = score_slot_1      # Integer, default 0
        self.score_slot_2 = score_slot_2      # Integer, default 0
        self.score_slot_3 = score_slot_3      # Integer, default 0
        self.score_slot_4 = score_slot_4      # Integer, default 0
        self.score_slot_5 = score_slot_5      # Integer, default 0

class SubscriptionStatus:
    ACTIVE = 'active'
    EXPIRED = 'expired'
    PENDING_RENEWAL = 'pending_renewal'
    CANCELLED = 'cancelled'
    PENDING_APPROVAL = 'pending_approval' # Added for clarity for when proof is submitted

class Subscription(Model):
    def __init__(self, user_profile, start_date, end_date, status, proof_of_payment_url=None):
        self.user_profile = user_profile  # ForeignKey to UserProfile
        self.start_date = start_date      # Date
        self.end_date = end_date          # Date
        self.status = status              # String, use SubscriptionStatus constants
        self.proof_of_payment_url = proof_of_payment_url  # String, nullable

class Notification(Model):
    def __init__(self, notification_id, message, recipient_user_profile=None, recipient_team=None,
                 created_at=None, is_read=False):
        self.notification_id = notification_id  # Unique identifier
        self.recipient_user_profile = recipient_user_profile  # ForeignKey to UserProfile, nullable
        self.recipient_team = recipient_team    # ForeignKey to Team, nullable
        self.message = message                  # Text
        self.created_at = created_at if created_at else datetime.datetime.now()  # DateTime
        self.is_read = is_read                  # Boolean, default False

class Achievement(Model):
    def __init__(self, name, description, icon_url=None):
        self.name = name                # String (e.g., 'Commitment', 'Teamwork')
        self.description = description  # Text
        self.icon_url = icon_url        # String, nullable

class UserAchievement(Model):
    def __init__(self, user_profile, achievement, awarded_date):
        self.user_profile = user_profile  # ForeignKey to UserProfile
        self.achievement = achievement    # ForeignKey to Achievement
        self.awarded_date = awarded_date  # Date
