"""
Subscription management module - Handles premium subscriptions and indigent fee waivers.
"""
import json
import logging
import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from models import User, Subscription, ROLE_PREMIUM, ROLE_MOD, db
from forms import SubscriptionForm, FeeWaiverForm, WaiverReviewForm
from fee_waiver_calculator import calculate_fee_waiver_percentage, get_poverty_threshold, calculate_adjusted_fee, POVERTY_GUIDELINES

# Create blueprint
subscriptions_bp = Blueprint('subscriptions', __name__)

@subscriptions_bp.route('/premium', methods=['GET'])
def premium_info():
    """Display information about premium features"""
    return render_template('premium_info.html')

@subscriptions_bp.route('/my-subscription', methods=['GET', 'POST'])
@login_required
def my_subscription():
    """Manage user's subscription"""
    # Get user's current subscription if any with error handling
    try:
        subscription = current_user.get_active_subscription()
    except Exception as e:
        logging.error(f"Error getting user subscription: {str(e)}")
        subscription = None
        flash("Error loading subscription information. Please try again later.", "danger")
    
    # Create forms
    subscription_form = SubscriptionForm()
    fee_waiver_form = FeeWaiverForm()
    
    if request.method == 'POST':
        # Handle subscription form submission
        if 'subscribe_submit' in request.form and subscription_form.validate_on_submit():
            # If user already has an active subscription, don't create a new one
            if subscription:
                flash('You already have an active subscription', 'warning')
                return redirect(url_for('subscriptions.my_subscription'))
            
            # Create a new subscription (payment will be handled later)
            new_subscription = Subscription.create_subscription(
                user_id=current_user.id,
                subscription_type=subscription_form.subscription_type.data,
                price=50.00  # Default $50/month price
            )
            
            # Flash success message and redirect to payment page
            flash('Subscription created! Proceed to payment to activate your premium features.', 'success')
            return redirect(url_for('subscriptions.payment', subscription_id=new_subscription.id))
        
        # Handle fee waiver form submission
        elif 'waiver_submit' in request.form and fee_waiver_form.validate_on_submit():
            # If no subscription exists, create one first
            if not subscription:
                subscription = Subscription.create_subscription(current_user.id)
            
            # Validate the income input
            income_str = fee_waiver_form.annual_income.data
            if income_str:
                # Remove commas and dollar signs
                income_str = income_str.replace(',', '').replace('$', '')
                
                try:
                    # Parse income and household size
                    annual_income = float(income_str)
                    household_size = int(fee_waiver_form.household_size.data)
                    
                    # Calculate fee waiver percentage based on poverty guidelines
                    waiver_percentage = calculate_fee_waiver_percentage(annual_income, household_size)
                    
                    # Get poverty threshold for reference
                    poverty_threshold = get_poverty_threshold(household_size)
                    poverty_percentage = (annual_income / poverty_threshold) * 100
                    
                    # Apply for fee waiver with income information
                    subscription.apply_fee_waiver(
                        reason=fee_waiver_form.reason.data,
                        annual_income=annual_income,
                        household_size=household_size
                    )
                    db.session.commit()
                    
                    # Prepare flash message with details about the waiver eligibility
                    if waiver_percentage == 100:
                        message = (f'Your income is {poverty_percentage:.1f}% of the poverty guideline for your household size, '
                                  f'which qualifies you for a 100% fee waiver. Your application has been submitted for review.')
                    elif waiver_percentage > 0:
                        message = (f'Your income is {poverty_percentage:.1f}% of the poverty guideline for your household size, '
                                  f'which may qualify you for a {waiver_percentage}% fee waiver. Your application has been submitted for review.')
                    else:
                        message = ('Based on the information provided, you may not qualify for a fee waiver. '
                                  'However, your application has been submitted for review.')
                    
                    flash(message, 'success')
                except ValueError:
                    # Handle invalid income input
                    flash('Please enter a valid number for annual income.', 'danger')
                    return redirect(url_for('subscriptions.my_subscription'))
            else:
                # Apply for fee waiver without income information
                subscription.apply_fee_waiver(reason=fee_waiver_form.reason.data)
                db.session.commit()
                flash('Your fee waiver application has been submitted. You will be notified when it is reviewed.', 'success')
            
            return redirect(url_for('subscriptions.my_subscription'))
    
    return render_template('subscription.html', 
                          subscription=subscription,
                          subscription_form=subscription_form,
                          fee_waiver_form=fee_waiver_form)

@subscriptions_bp.route('/payment/<int:subscription_id>', methods=['GET'])
@login_required
def payment(subscription_id):
    """Process payment for a subscription"""
    # Get subscription and verify it belongs to the current user
    subscription = Subscription.query.get_or_404(subscription_id)
    if subscription.user_id != current_user.id:
        abort(403)
    
    # Check if subscription is already paid or has an approved fee waiver
    if subscription.fee_waiver_approved:
        flash('Your fee waiver has been approved. You already have premium access.', 'info')
        return redirect(url_for('subscriptions.my_subscription'))
    
    # Display payment page
    return render_template('payment.html', subscription=subscription)

@subscriptions_bp.route('/cancel-subscription', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel a user's subscription"""
    subscription = current_user.get_active_subscription()
    if not subscription:
        flash('You do not have an active subscription to cancel', 'warning')
        return redirect(url_for('subscriptions.my_subscription'))
    
    # Cancel the subscription
    subscription.cancel()
    db.session.commit()
    
    flash('Your subscription has been canceled', 'success')
    return redirect(url_for('subscriptions.my_subscription'))

# Admin fee waiver management routes
@subscriptions_bp.route('/admin/fee-waivers', methods=['GET', 'POST'])
@login_required
def manage_fee_waivers():
    """Admin page to review and manage fee waiver applications"""
    # Only moderators can access this page
    if not current_user.is_moderator():
        abort(403)
    
    # Handle form submission if present
    if request.method == 'POST':
        form = WaiverReviewForm(request.form)
        
        if form.validate_on_submit():
            subscription_id = request.form.get('subscription_id')
            if not subscription_id:
                flash('Missing subscription ID', 'danger')
                return redirect(url_for('subscriptions.manage_fee_waivers'))
            
            subscription = Subscription.query.get_or_404(int(subscription_id))
            
            if form.decision.data == 'approve':
                # Use the selected waiver percentage
                waiver_percentage = int(form.waiver_percentage.data)
                
                # Approve with the specified percentage
                subscription.approve_fee_waiver(
                    reviewer_id=current_user.id,
                    waiver_percentage=waiver_percentage
                )
                
                # Record review notes if provided
                if form.notes.data:
                    subscription.fee_waiver_notes = form.notes.data
                
                db.session.commit()
                
                # Flash success message based on waiver percentage
                if waiver_percentage == 100:
                    message = 'Full fee waiver (100%) has been approved'
                elif waiver_percentage > 0:
                    message = f'Partial fee waiver ({waiver_percentage}%) has been approved'
                else:
                    message = 'Fee waiver has been denied (0% reduction)'
                
                flash(message, 'success')
                
            elif form.decision.data == 'auto':
                # Automatically calculate based on income
                if subscription.annual_income and subscription.household_size:
                    waiver_percentage = calculate_fee_waiver_percentage(
                        subscription.annual_income,
                        subscription.household_size
                    )
                    
                    # Approve with the calculated percentage
                    subscription.approve_fee_waiver(
                        reviewer_id=current_user.id,
                        waiver_percentage=waiver_percentage
                    )
                    
                    # Record review notes if provided
                    if form.notes.data:
                        subscription.fee_waiver_notes = form.notes.data
                    
                    db.session.commit()
                    
                    poverty_threshold = get_poverty_threshold(subscription.household_size)
                    poverty_percentage = (subscription.annual_income / poverty_threshold) * 100
                    
                    message = (f'Automatically approved {waiver_percentage}% fee waiver based on '
                              f'income at {poverty_percentage:.1f}% of poverty line')
                    flash(message, 'success')
                else:
                    flash('Cannot automatically calculate waiver percentage - missing income information', 'danger')
            
            elif form.decision.data == 'deny':
                # Deny the waiver application
                subscription.fee_waiver_approved = False
                subscription.fee_waiver_reviewed_by = current_user.id
                subscription.waiver_percentage = 0
                
                # Record review notes if provided
                if form.notes.data:
                    subscription.fee_waiver_notes = form.notes.data
                
                db.session.commit()
                flash('Fee waiver application has been denied', 'warning')
            
            return redirect(url_for('subscriptions.manage_fee_waivers'))
    
    # Get all pending fee waiver applications with error handling
    try:
        from sqlalchemy import and_, desc
        # Use db.session.query with explicit conditions to avoid attribute access issues
        pending_waivers = db.session.query(Subscription).filter(
            and_(
                Subscription.fee_waiver == True,
                Subscription.fee_waiver_approved == False
            )
        ).join(User).filter(User.id == Subscription.user_id).all()
    except Exception as e:
        logging.error(f"Error getting pending waivers: {str(e)}")
        pending_waivers = []
        flash("Error loading pending waiver requests. Please try again later.", "danger")
    
    # Get recently approved waivers with error handling
    try:
        # Use db.session.query with explicit conditions to avoid attribute access issues
        approved_waivers = db.session.query(Subscription).filter(
            and_(
                Subscription.fee_waiver == True,
                Subscription.fee_waiver_approved == True
            )
        ).join(User).filter(User.id == Subscription.user_id).order_by(desc(Subscription.updated_at)).limit(10).all()
    except Exception as e:
        logging.error(f"Error getting approved waivers: {str(e)}")
        approved_waivers = []
        flash("Error loading approved waiver history. Please try again later.", "danger")
    
    # Create form for each pending waiver
    waiver_forms = {}
    for waiver in pending_waivers:
        form = WaiverReviewForm()
        
        # Pre-calculate suggested waiver percentage
        if waiver.annual_income and waiver.household_size:
            suggested_percentage = calculate_fee_waiver_percentage(waiver.annual_income, waiver.household_size)
            form.waiver_percentage.default = str(suggested_percentage)
            
            # Set decision to 'auto' if income information is available
            form.decision.default = 'auto'
        else:
            # Default to 100% waiver if no income info
            form.waiver_percentage.default = '100'
            form.decision.default = 'approve'
        
        form.process()
        waiver_forms[waiver.id] = form
    
    return render_template('manage_waivers.html', 
                          pending_waivers=pending_waivers, 
                          approved_waivers=approved_waivers,
                          waiver_forms=waiver_forms,
                          poverty_guidelines=POVERTY_GUIDELINES,
                          get_poverty_threshold=get_poverty_threshold,
                          calculate_fee_waiver_percentage=calculate_fee_waiver_percentage)

@subscriptions_bp.route('/admin/approve-waiver/<int:subscription_id>', methods=['POST'])
@login_required
def approve_waiver(subscription_id):
    """Quick approve a fee waiver application (100% waiver)"""
    # Only moderators can approve waivers
    if not current_user.is_moderator():
        abort(403)
    
    # Get the subscription
    subscription = Subscription.query.get_or_404(subscription_id)
    
    # Approve the waiver with 100% reduction
    subscription.approve_fee_waiver(
        reviewer_id=current_user.id,
        waiver_percentage=100
    )
    db.session.commit()
    
    flash('Fee waiver has been approved with 100% reduction', 'success')
    return redirect(url_for('subscriptions.manage_fee_waivers'))