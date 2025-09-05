from flask import session, render_template, request, redirect, url_for, flash
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app import app, db
from replit_auth import require_login, make_replit_blueprint
from models import Giveaway, Entry

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/home')
@require_login
def home():
    # Get active giveaways
    active_giveaways = Giveaway.query.filter(
        Giveaway.is_active == True,
        Giveaway.end_date > datetime.now()
    ).order_by(Giveaway.end_date.asc()).all()
    
    # Get past giveaways with winners
    past_giveaways = Giveaway.query.filter(
        Giveaway.winner_id.isnot(None)
    ).order_by(Giveaway.winner_selected_at.desc()).limit(5).all()
    
    # Get user's entries
    user_entries = Entry.query.filter_by(user_id=current_user.id).all()
    user_giveaway_ids = [entry.giveaway_id for entry in user_entries]
    
    return render_template('home.html', 
                         active_giveaways=active_giveaways,
                         past_giveaways=past_giveaways,
                         user_giveaway_ids=user_giveaway_ids)

@app.route('/giveaway/<int:giveaway_id>')
@require_login
def giveaway_detail(giveaway_id):
    giveaway = Giveaway.query.get_or_404(giveaway_id)
    
    # Check if user has entered
    user_entry = Entry.query.filter_by(
        user_id=current_user.id,
        giveaway_id=giveaway_id
    ).first()
    
    return render_template('giveaway_detail.html', 
                         giveaway=giveaway,
                         user_entry=user_entry)

@app.route('/giveaway/<int:giveaway_id>/enter', methods=['POST'])
@require_login
def enter_giveaway(giveaway_id):
    giveaway = Giveaway.query.get_or_404(giveaway_id)
    
    if not giveaway.can_enter:
        flash('This giveaway is no longer accepting entries.', 'error')
        return redirect(url_for('giveaway_detail', giveaway_id=giveaway_id))
    
    # Check if user can afford the ticket
    if not giveaway.can_user_afford(current_user):
        flash(f'You need {giveaway.ticket_price} coins to enter this giveaway. You have {current_user.currency_balance} coins.', 'error')
        return redirect(url_for('giveaway_detail', giveaway_id=giveaway_id))
    
    # Check if user already entered
    existing_entry = Entry.query.filter_by(
        user_id=current_user.id,
        giveaway_id=giveaway_id
    ).first()
    
    if existing_entry:
        flash('You have already entered this giveaway.', 'error')
        return redirect(url_for('giveaway_detail', giveaway_id=giveaway_id))
    
    try:
        # Deduct currency from user
        current_user.currency_balance -= giveaway.ticket_price
        
        # Create entry record
        entry = Entry()
        entry.user_id = current_user.id
        entry.giveaway_id = giveaway_id
        entry.cost_paid = giveaway.ticket_price
        
        # Create transaction record
        from models import Transaction
        transaction = Transaction()
        transaction.user_id = current_user.id
        transaction.amount = -giveaway.ticket_price
        transaction.transaction_type = 'ticket_purchase'
        transaction.description = f'Entered giveaway: {giveaway.title}'
        transaction.related_giveaway_id = giveaway_id
        
        db.session.add(entry)
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Successfully entered the giveaway for {giveaway.ticket_price} coins!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Error entering giveaway. Please try again.', 'error')
    
    return redirect(url_for('giveaway_detail', giveaway_id=giveaway_id))

@app.route('/profile')
@require_login
def profile():
    # Get user's entries with giveaway details
    entries = Entry.query.filter_by(user_id=current_user.id).join(Giveaway).all()
    
    # Get giveaways user has won
    won_giveaways = Giveaway.query.filter_by(winner_id=current_user.id).all()
    
    return render_template('profile.html', 
                         entries=entries,
                         won_giveaways=won_giveaways)
