from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from datetime import datetime

from app import app, db
from replit_auth import require_admin
from models import Giveaway, Entry, User

@app.route('/admin')
@require_admin
def admin_dashboard():
    total_giveaways = Giveaway.query.count()
    active_giveaways = Giveaway.query.filter(
        Giveaway.is_active == True,
        Giveaway.end_date > datetime.now()
    ).count()
    total_users = User.query.count()
    total_entries = Entry.query.count()
    
    recent_giveaways = Giveaway.query.order_by(Giveaway.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_giveaways=total_giveaways,
                         active_giveaways=active_giveaways,
                         total_users=total_users,
                         total_entries=total_entries,
                         recent_giveaways=recent_giveaways)

@app.route('/admin/giveaways')
@require_admin
def admin_giveaways():
    page = request.args.get('page', 1, type=int)
    giveaways = Giveaway.query.order_by(Giveaway.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('admin/giveaways.html', giveaways=giveaways)

@app.route('/admin/giveaways/create', methods=['GET', 'POST'])
@require_admin
def create_giveaway():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        prize = request.form['prize']
        end_date_str = request.form['end_date']
        max_entries = request.form.get('max_entries', type=int)
        
        try:
            end_date = datetime.fromisoformat(end_date_str.replace('T', ' '))
            
            giveaway = Giveaway(
                title=title,
                description=description,
                prize=prize,
                end_date=end_date,
                max_entries=max_entries if max_entries else None
            )
            
            db.session.add(giveaway)
            db.session.commit()
            flash('Giveaway created successfully!', 'success')
            return redirect(url_for('admin_giveaways'))
            
        except ValueError:
            flash('Invalid date format. Please try again.', 'error')
    
    return render_template('admin/create_giveaway.html')

@app.route('/admin/giveaways/<int:giveaway_id>/edit', methods=['GET', 'POST'])
@require_admin
def edit_giveaway(giveaway_id):
    giveaway = Giveaway.query.get_or_404(giveaway_id)
    
    if request.method == 'POST':
        giveaway.title = request.form['title']
        giveaway.description = request.form['description']
        giveaway.prize = request.form['prize']
        end_date_str = request.form['end_date']
        giveaway.max_entries = request.form.get('max_entries', type=int) or None
        giveaway.is_active = 'is_active' in request.form
        
        try:
            giveaway.end_date = datetime.fromisoformat(end_date_str.replace('T', ' '))
            db.session.commit()
            flash('Giveaway updated successfully!', 'success')
            return redirect(url_for('admin_giveaways'))
            
        except ValueError:
            flash('Invalid date format. Please try again.', 'error')
    
    return render_template('admin/edit_giveaway.html', giveaway=giveaway)

@app.route('/admin/giveaways/<int:giveaway_id>/select_winner', methods=['POST'])
@require_admin
def select_winner(giveaway_id):
    giveaway = Giveaway.query.get_or_404(giveaway_id)
    
    if giveaway.winner_id:
        flash('Winner has already been selected for this giveaway.', 'error')
        return redirect(url_for('admin_giveaways'))
    
    if not giveaway.entries:
        flash('No entries found for this giveaway.', 'error')
        return redirect(url_for('admin_giveaways'))
    
    winner = giveaway.select_winner()
    if winner:
        db.session.commit()
        flash(f'Winner selected: {winner.display_name}!', 'success')
    else:
        flash('Error selecting winner. Please try again.', 'error')
    
    return redirect(url_for('admin_giveaways'))

@app.route('/admin/giveaways/<int:giveaway_id>/delete', methods=['POST'])
@require_admin
def delete_giveaway(giveaway_id):
    giveaway = Giveaway.query.get_or_404(giveaway_id)
    db.session.delete(giveaway)
    db.session.commit()
    flash('Giveaway deleted successfully!', 'success')
    return redirect(url_for('admin_giveaways'))

@app.route('/admin/users')
@require_admin
def admin_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<user_id>/toggle_admin', methods=['POST'])
@require_admin
def toggle_user_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin status from yourself
    if user.id == current_user.id:
        flash('You cannot modify your own admin status.', 'error')
        return redirect(url_for('admin_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin access {status} for {user.display_name}.', 'success')
    return redirect(url_for('admin_users'))
