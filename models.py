from datetime import datetime
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
import random

# (IMPORTANT) This table is mandatory for Replit Auth, don't drop it.
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    currency_balance = db.Column(db.Integer, default=1000, nullable=False)  # Start with 1000 coins
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    entries = db.relationship('Entry', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    @property
    def display_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.email:
            return self.email.split('@')[0]
        else:
            return f"User {self.id}"

# (IMPORTANT) This table is mandatory for Replit Auth, don't drop it.
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

class Giveaway(db.Model):
    __tablename__ = 'giveaways'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    prize = db.Column(db.String(500), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(db.DateTime, nullable=False)
    max_entries = db.Column(db.Integer, nullable=True)  # Optional entry limit
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    winner_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=True)
    winner_selected_at = db.Column(db.DateTime, nullable=True)
    ticket_price = db.Column(db.Integer, default=100, nullable=False)  # Cost in currency to enter
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    entries = db.relationship('Entry', backref='giveaway', lazy=True, cascade='all, delete-orphan')
    winner = db.relationship('User', foreign_keys=[winner_id], backref='won_giveaways')
    
    @property
    def is_ended(self):
        return datetime.now() > self.end_date
    
    @property
    def can_enter(self):
        if not self.is_active or self.is_ended or self.winner_id:
            return False
        if self.max_entries and self.entry_count >= self.max_entries:
            return False
        return True
    
    def can_user_afford(self, user):
        """Check if user can afford the ticket price"""
        return user.currency_balance >= self.ticket_price
    
    @property
    def entry_count(self):
        from app import db
        return db.session.query(Entry).filter_by(giveaway_id=self.id).count()
    
    def select_winner(self):
        """Select a random winner from entries"""
        from app import db
        entries_list = db.session.query(Entry).filter_by(giveaway_id=self.id).all()
        if entries_list and not self.winner_id:
            winner_entry = random.choice(entries_list)
            self.winner_id = winner_entry.user_id
            self.winner_selected_at = datetime.now()
            return winner_entry.user
        return None

class Entry(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    giveaway_id = db.Column(db.Integer, db.ForeignKey('giveaways.id'), nullable=False)
    entered_at = db.Column(db.DateTime, default=datetime.now)
    cost_paid = db.Column(db.Integer, nullable=False)  # Amount of currency paid for this entry
    
    # Ensure a user can only enter once per giveaway
    __table_args__ = (UniqueConstraint('user_id', 'giveaway_id', name='uq_user_giveaway'),)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Positive for earning, negative for spending
    transaction_type = db.Column(db.String(50), nullable=False)  # 'ticket_purchase', 'admin_grant', 'bonus', etc.
    description = db.Column(db.String(200), nullable=True)
    related_giveaway_id = db.Column(db.Integer, db.ForeignKey('giveaways.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    related_giveaway = db.relationship('Giveaway', backref='transactions')
