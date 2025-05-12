"""
Stripe integration for premium subscription handling
"""
import os
import json
import logging
from datetime import datetime
import stripe
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import current_user, login_required
from models import db, User, Subscription

# Initialize Stripe with API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Premium price for $50/month subscription
PREMIUM_PRICE_USD = 5000  # in cents (50.00 USD)

# Constants for subscription types
SUBSCRIPTION_TYPE_PREMIUM = 'premium'

# Create blueprint
stripe_bp = Blueprint('stripe', __name__)

@stripe_bp.route('/subscribe')
@login_required
def stripe_subscription():
    """Display the subscription page with Stripe checkout"""
    return render_template('stripe_subscription.html')

@stripe_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create a Stripe checkout session for premium subscription"""
    try:
        # Get the domain URL for success/cancel redirects
        domain_url = request.host_url.rstrip('/')
        
        # Create the checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Due Process AI Premium Subscription',
                            'description': 'Monthly subscription for premium features',
                        },
                        'unit_amount': PREMIUM_PRICE_USD,
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=domain_url + url_for('stripe.subscription_success') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + url_for('stripe.subscription_cancel'),
            client_reference_id=str(current_user.id),  # To identify the user in webhook
            metadata={
                'user_id': str(current_user.id),
                'user_email': current_user.email
            }
        )
        
        if checkout_session and hasattr(checkout_session, 'url') and checkout_session.url:
            return redirect(checkout_session.url)
        else:
            return redirect(url_for('stripe.stripe_subscription'))
    except Exception as e:
        logging.error(f"Error creating checkout session: {str(e)}")
        flash("Failed to create checkout session. Please try again.", "danger")
        return redirect(url_for('stripe.stripe_subscription'))


@stripe_bp.route('/subscription-success')
@login_required
def subscription_success():
    """Handle successful subscription"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash("Invalid session ID", "danger")
        return redirect(url_for('stripe.stripe_subscription'))
    
    try:
        # Retrieve the session to get subscription details
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        subscription_id = checkout_session.subscription
        
        # Update user's subscription status in database
        if subscription_id:
            subscription = Subscription.query.filter_by(user_id=current_user.id).first()
            
            if not subscription:
                # Create new subscription record
                subscription = Subscription(
                    user_id=current_user.id,
                    stripe_subscription_id=subscription_id,
                    status='active',
                    subscription_type=SUBSCRIPTION_TYPE_PREMIUM,
                    price_usd=PREMIUM_PRICE_USD / 100  # Convert cents to dollars
                )
                db.session.add(subscription)
            else:
                # Update existing subscription record
                subscription.stripe_subscription_id = subscription_id
                subscription.status = 'active'
                subscription.subscription_type = SUBSCRIPTION_TYPE_PREMIUM
                subscription.price_usd = PREMIUM_PRICE_USD / 100
                subscription.start_date = datetime.utcnow()
            
            db.session.commit()
            
            flash("Thank you for subscribing to Premium! Your account has been upgraded.", "success")
            return render_template('subscription_success.html')
        else:
            flash("Subscription ID not found", "danger")
            return redirect(url_for('stripe.stripe_subscription'))
    except Exception as e:
        logging.error(f"Error processing subscription success: {str(e)}")
        flash("Error processing subscription. Please contact support.", "danger")
        return redirect(url_for('stripe.stripe_subscription'))


@stripe_bp.route('/subscription-cancel')
@login_required
def subscription_cancel():
    """Handle cancelled subscription checkout"""
    flash("Your subscription process was cancelled. You can try again anytime.", "info")
    return render_template('subscription_cancel.html')


@stripe_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    # This endpoint should be configured in Stripe dashboard with your webhook secret
    # For testing, we'll skip signature verification
    
    try:
        # Parse the JSON payload manually to handle the None case
        json_data = json.loads(payload) if payload else None
        if json_data:
            event = stripe.Event.construct_from(
                json_data, stripe.api_key
            )
        else:
            # Handle empty payload
            logging.error("Empty Stripe webhook payload")
            return jsonify({'status': 'error'}), 400
    except ValueError as e:
        # Invalid payload
        logging.error(f"Invalid Stripe payload: {str(e)}")
        return jsonify({'status': 'error'}), 400
    
    # Handle the event
    if event.type == 'customer.subscription.updated':
        subscription = event.data.object
        handle_subscription_updated(subscription)
    elif event.type == 'customer.subscription.deleted':
        subscription = event.data.object
        handle_subscription_cancelled(subscription)
    
    return jsonify({'status': 'success'})


def handle_subscription_updated(stripe_subscription):
    """Process subscription update webhook"""
    try:
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=stripe_subscription.id
        ).first()
        
        if subscription:
            subscription.status = stripe_subscription.status
            db.session.commit()
            logging.info(f"Updated subscription {stripe_subscription.id} status to {stripe_subscription.status}")
    except Exception as e:
        logging.error(f"Error handling subscription update: {str(e)}")


def handle_subscription_cancelled(stripe_subscription):
    """Process subscription cancellation webhook"""
    try:
        subscription = Subscription.query.filter_by(
            stripe_subscription_id=stripe_subscription.id
        ).first()
        
        if subscription:
            subscription.status = 'cancelled'
            subscription.end_date = datetime.utcnow()
            db.session.commit()
            logging.info(f"Cancelled subscription {stripe_subscription.id}")
    except Exception as e:
        logging.error(f"Error handling subscription cancellation: {str(e)}")


@stripe_bp.route('/manage-subscription')
@login_required
def manage_subscription():
    """Redirect user to Stripe Customer Portal to manage their subscription"""
    try:
        subscription = Subscription.query.filter_by(user_id=current_user.id, status='active').first()
        
        if not subscription or not subscription.stripe_subscription_id:
            flash("No active subscription found", "warning")
            return redirect(url_for('stripe.stripe_subscription'))
        
        # Get Stripe customer ID (in a real implementation, you'd store this)
        stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
        
        # Extract the customer ID as a string
        if hasattr(stripe_subscription, 'customer'):
            customer_obj = stripe_subscription.customer
            # If it's already a string
            if isinstance(customer_obj, str):
                customer_id = customer_obj
            # If it's another type with string representation
            else:
                try:
                    # Try to convert to string
                    customer_id = str(customer_obj)
                except Exception as e:
                    logging.error(f"Error extracting customer ID: {str(e)}")
                    flash("Unable to process customer information", "warning")
                    return redirect(url_for('cases.dashboard'))
        else:
            flash("Unable to retrieve customer information", "warning")
            return redirect(url_for('cases.dashboard'))
        
        # Create a billing portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=request.host_url.rstrip('/') + url_for('cases.dashboard')
        )
        
        # Redirect to the portal
        if portal_session and hasattr(portal_session, 'url') and portal_session.url:
            return redirect(portal_session.url)
        
        # Fallback if we can't get the customer ID or session URL
        flash("Unable to create management portal session", "warning")
        return redirect(url_for('cases.dashboard'))
    except Exception as e:
        logging.error(f"Error creating customer portal session: {str(e)}")
        flash("Failed to access subscription management. Please contact support.", "danger")
        return redirect(url_for('cases.dashboard'))