from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

class UserProfile(models.Model):
    """
    Extended user profile with balance
    Admin users don't have a balance (set to None)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def save(self, *args, **kwargs):
        # If user is admin, they don't have a balance
        if self.user.is_staff:
            self.balance = None
        super().save(*args, **kwargs)
    
    def deposit(self, amount):
        """
        Add funds to user balance
        Returns True if successful, False otherwise
        """
        if self.user.is_staff:
            return False
        
        if amount <= 0:
            return False
        
        if self.balance is None:
            self.balance = Decimal('0.00')
            
        self.balance += Decimal(str(amount))
        self.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='DEPOSIT',
            description='Funds deposited'
        )
        
        return True
    
    def withdraw(self, amount):
        """
        Remove funds from user balance
        Returns True if successful, False otherwise
        """
        if self.user.is_staff:
            return False
            
        if amount <= 0:
            return False
            
        if self.balance is None or self.balance < amount:
            return False
            
        self.balance -= Decimal(str(amount))
        self.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=self.user,
            amount=-amount,  # Negative for withdrawals
            transaction_type='WITHDRAWAL',
            description='Order payment'
        )
        
        return True
    
    def refund(self, amount, description='Order refund'):
        """
        Refund to user balance
        """
        if self.user.is_staff:
            return False
            
        if amount <= 0:
            return False
            
        if self.balance is None:
            self.balance = Decimal('0.00')
            
        self.balance += Decimal(str(amount))
        self.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='REFUND',
            description=description
        )
        
        return True

class Transaction(models.Model):
    """
    Model to track all balance-related transactions
    """
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('REFUND', 'Refund'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.user.username}"

# Signal to create user profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Signal to save user profile when user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # If profile doesn't exist yet, create it
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)