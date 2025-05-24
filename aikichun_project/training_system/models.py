from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class UserTypeChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        ASSISTANT_ADMIN = 'ASSISTANT_ADMIN', 'Assistant Admin'
        COACH = 'COACH', 'Coach'
        PLAYER = 'PLAYER', 'Player'

    user_type = models.CharField(
        max_length=20,
        choices=UserTypeChoices.choices,
        default=UserTypeChoices.PLAYER,
    )
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    job = models.CharField(max_length=100, null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    children_details = models.JSONField(null=True, blank=True, default=list)

    def __str__(self):
        return self.username

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    branch = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class TrainingDetail(models.Model):
    class MembershipLevelChoices(models.TextChoices):
        BEGINNER = 'BEGINNER', 'Beginner'
        INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
        ADVANCED = 'ADVANCED', 'Advanced'

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    membership_level = models.CharField(
        max_length=20,
        choices=MembershipLevelChoices.choices,
        default=MembershipLevelChoices.BEGINNER,
    )
    training_start_date = models.DateField()
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    coach = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coached_players',
        limit_choices_to={'user_type': CustomUser.UserTypeChoices.COACH}
    )
    team_leader = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_teams',
        limit_choices_to={'user_type': CustomUser.UserTypeChoices.PLAYER}
    )

    def __str__(self):
        return f"{self.user.username}'s Training Details"

class Subscription(models.Model):
    class SubscriptionStatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        EXPIRED = 'EXPIRED', 'Expired'
        PENDING_RENEWAL = 'PENDING_RENEWAL', 'Pending Renewal'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatusChoices.choices,
        default=SubscriptionStatusChoices.EXPIRED,
    )
    expiration_date = models.DateField()
    proof_of_payment = models.FileField(upload_to='proofs/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Subscription ({self.status})"

class Achievement(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    badge_icon = models.ImageField(upload_to='achievement_icons/', null=True, blank=True)

    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='user_awards')
    date_awarded = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

class PerformanceMetric(models.Model):
    class SpeedLevelChoices(models.TextChoices):
        S_LEVEL = 'S', 'S'
        M_LEVEL = 'M', 'M'
        G_LEVEL = 'G', 'G'

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='performance_metrics')
    speed_level = models.CharField(max_length=1, choices=SpeedLevelChoices.choices, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Performance Metrics"

class TechniqueCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Technique(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(TechniqueCategory, on_delete=models.CASCADE, related_name='techniques')
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('category', 'name')

    def __str__(self):
        return self.name

class UserTechniqueScore(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='technique_scores')
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE, related_name='user_scores')
    scores = models.JSONField(default=lambda: [0, 0, 0, 0, 0])
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'technique')

    def __str__(self):
        return f"{self.user.username} - {self.technique.name} Scores"

class Notification(models.Model):
    class NotificationTypeChoices(models.TextChoices):
        SYSTEM = 'SYSTEM', 'System'
        RENEWAL = 'RENEWAL', 'Renewal Reminder'
        TEAM_UPDATE = 'TEAM_UPDATE', 'Team Update'
        NEW_MATERIAL = 'NEW_MATERIAL', 'New Training Material'
        GENERAL = 'GENERAL', 'General Notification'

    recipient_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    recipient_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_notifications', null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationTypeChoices.choices,
        default=NotificationTypeChoices.GENERAL,
    )

    def __str__(self):
        recipient = "All Users"
        if self.recipient_user:
            recipient = self.recipient_user.username
        elif self.recipient_team:
            recipient = self.recipient_team.name
        return f"Notification for {recipient} - Type: {self.get_notification_type_display()}"

    class Meta:
        ordering = ['-created_at']
