# Hello I am Teja this is a sample templete code for AWS Capstone project
# Hello again
# I am testing git push and pull
import boto3
import os
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from crypto_service import crypto_service
import re



app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# AWS CONFIGURATION
AWS_REGION = "us-east-1"

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

sns = boto3.client(
    "sns",
    region_name=AWS_REGION
)

# DynamoDB Tables (must exist in AWS later)
users_table = dynamodb.Table("Users")
admin_users_table = dynamodb.Table("AdminUsers")
watchlist_table = dynamodb.Table("UserWatchlists")
alerts_table = dynamodb.Table("PriceAlerts")

# SNS Topic ARN (replace later)
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:xxxx:crypto-alerts"

def send_notification(subject, message):
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
    except ClientError as e:
        print("SNS error:", e)




# In-memory database (dictionary)


# In-memory crypto data storage


def validate_password(password):
    """Validate password strength and return all requirements at once"""
    errors = []
    
    if len(password) < 8:
        errors.append("at least 8 characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("one uppercase letter (A-Z)")
    
    if not re.search(r'[a-z]', password):
        errors.append("one lowercase letter (a-z)")
    
    if not re.search(r'\d', password):
        errors.append("one digit (0-9)")
    
    if not re.search(r'[!@#$%^&*()_+=\-\[\]{}|;:"\'<>,.?/]', password):
        errors.append("one special character (!@#$%^&*)")
    
    if errors:
        error_message = "Password must contain: " + ", ".join(errors)
        return False, error_message
    
    return True, "Password is strong"
price_alerts = {}
market_data = []
last_api_update = None

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # ✅ Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('signup.html')

        try:
            # 🔍 Check if user already exists
            response = users_table.get_item(
                Key={'username': username}
            )

            if 'Item' in response:
                flash("User already exists!", 'error')
                return render_template('signup.html')

            # ✅ Save user to DynamoDB
            users_table.put_item(
                Item={
                    'username': username,
                    'password': password,
                    'created_at': datetime.utcnow().isoformat()
                }
            )

            # 🔔 SNS Notification (mentor-style)
            send_notification(
                "New User Signup",
                f"User '{username}' has signed up successfully."
            )

            flash("Account created successfully! Please login.", 'success')
            return redirect(url_for('login'))

        except ClientError as e:
            print("DynamoDB error:", e)
            flash("AWS error occurred. Try again later.", 'error')
            return render_template('signup.html')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            response = users_table.get_item(
                Key={'username': username}
            )

            if 'Item' not in response:
                flash("Invalid credentials!", 'error')
                return render_template('login.html')

            user = response['Item']

            if user['password'] != password:
                flash("Invalid credentials!", 'error')
                return render_template('login.html')

            session['username'] = username

            # 🔔 SNS notification
            send_notification(
                "User Login",
                f"User '{username}' logged in successfully."
            )

            return redirect(url_for('home'))

        except ClientError as e:
            print("Login error:", e)
            flash("AWS error occurred", 'error')
            return render_template('login.html')

    return render_template('login.html')



@app.route('/home')
def home():
    if 'username' in session:
        return render_template(
            'home.html',
            username=session['username']
        )
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 🔐 Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('admin_signup.html')

        try:
            # 🔍 Check admin exists
            response = admin_users_table.get_item(
                Key={'username': username}
            )

            if 'Item' in response:
                flash("Admin already exists!", 'error')
                return render_template('admin_signup.html')

            # ✅ Save admin in DynamoDB
            admin_users_table.put_item(
                Item={
                    'username': username,
                    'password': password,
                    'created_at': datetime.utcnow().isoformat()
                }
            )

            # 🔔 SNS notification
            send_notification(
                "New Admin Signup",
                f"Admin {username} has been registered"
            )

            flash("Admin account created! Please login.", 'success')
            return redirect(url_for('admin_login'))

        except Exception as e:
            print("Admin signup error:", e)
            flash("AWS error occurred", 'error')
            return render_template('admin_signup.html')

    return render_template('admin_signup.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            response = admin_users_table.get_item(
                Key={'username': username}
            )

            if 'Item' in response and response['Item']['password'] == password:
                session['admin'] = username

                # 🔔 SNS notification (optional but recommended)
                send_notification(
                    "Admin Login",
                    f"Admin {username} logged in"
                )

                return redirect(url_for('admin_dashboard'))

            flash("Invalid admin credentials!", 'error')
            return render_template('admin_login.html')

        except Exception as e:
            print("Admin login error:", e)
            flash("AWS error occurred", 'error')
            return render_template('admin_login.html')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# Cryptocurrency Routes
@app.route('/crypto')
def crypto_market():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    global market_data, last_api_update
    
    if not market_data or not last_api_update or \
       (datetime.now() - last_api_update).seconds > 120:
        market_data = crypto_service.get_top_cryptocurrencies(50)
        last_api_update = datetime.now()
    
    from boto3.dynamodb.conditions import Key

    response = watchlist_table.query(
        KeyConditionExpression=Key('username').eq(session['username'])
    )

    user_watchlist_items = [
        item['coin_id'] for item in response.get('Items', [])
    ]

    watchlist_data = [
        coin for coin in market_data if coin['id'] in user_watchlist_items
    ]
    
    return render_template(
        'crypto_market.html',
        cryptocurrencies=market_data[:20],
        watchlist=watchlist_data,
        watchlist_items=user_watchlist_items,
        username=session['username']
    )

@app.route('/crypto/search', methods=['GET', 'POST'])
def crypto_search():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    search_results = []
    query = ''
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            search_results = crypto_service.search_cryptocurrency(query)
    
    return render_template('crypto_search.html', 
                         search_results=search_results,
                         query=query,
                         username=session['username'])

from boto3.dynamodb.conditions import Key

@app.route('/crypto/<coin_id>')
def crypto_details(coin_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    coin_details = crypto_service.get_cryptocurrency_details(coin_id)
    price_history = crypto_service.get_price_history(coin_id, 7)

    if not coin_details:
        return "Cryptocurrency not found!", 404

    # 🔹 FETCH WATCHLIST FROM DYNAMODB
    try:
        response = watchlist_table.query(
            KeyConditionExpression=Key('username').eq(session['username'])
        )
        watchlist_items = [item['coin_id'] for item in response.get('Items', [])]
        in_watchlist = coin_id in watchlist_items

    except Exception as e:
        print("Crypto details watchlist error:", e)
        in_watchlist = False

    return render_template(
        'crypto_details.html',
        coin=coin_details,
        price_history=price_history,
        in_watchlist=in_watchlist,
        username=session['username']
    )


@app.route('/watchlist/add/<coin_id>', methods=['POST'])
def add_to_watchlist(coin_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    try:
        watchlist_table.put_item(
            Item={
                'username': username,
                'coin_id': coin_id,
                'added_at': datetime.utcnow().isoformat()
            }
        )

        flash("Added to watchlist ✅")

    except Exception as e:
        print("Watchlist add error:", e)
        flash("AWS error occurred", 'error')

    return redirect(request.referrer or url_for('crypto_market'))


@app.route('/watchlist/remove/<coin_id>', methods=['POST'])
def remove_from_watchlist(coin_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    try:
        watchlist_table.delete_item(
            Key={
                'username': username,
                'coin_id': coin_id
            }
        )

        flash("Removed from watchlist ❌")

    except Exception as e:
        print("Watchlist remove error:", e)
        flash("AWS error occurred", 'error')

    return redirect(request.referrer or url_for('crypto_market'))

    
@app.route('/alerts')
def alerts_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        response = alerts_table.query(
            KeyConditionExpression=Key('username').eq(session['username'])
        )

        user_alerts = response.get('Items', [])

    except Exception as e:
        print("Fetch alerts error:", e)
        user_alerts = []

    return render_template(
        'price_alerts.html',
        alerts=user_alerts,
        username=session['username']
    )


@app.route('/alerts/create', methods=['GET', 'POST'])
def create_alert():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = session['username']
        coin_id = request.form['coin_id']
        coin_name = request.form['coin_name']
        alert_type = request.form['alert_type']
        target_price = float(request.form['target_price'])

        try:
            # create alert id (timestamp based – AWS safe)
            alert_id = int(datetime.utcnow().timestamp())

            alerts_table.put_item(
                Item={
                    'username': username,
                    'alert_id': alert_id,
                    'coin_id': coin_id,
                    'coin_name': coin_name,
                    'alert_type': alert_type,
                    'target_price': target_price,
                    'active': True,
                    'created_at': datetime.utcnow().isoformat()
                }
            )

            # 🔔 SNS notification (mentor style)
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="Price Alert Created",
                Message=f"{username} created alert for {coin_name} at ${target_price}"
            )

            flash("Price alert created ✅", "success")
            return redirect(url_for('alerts_page'))

        except Exception as e:
            print("Alert create error:", e)
            flash("AWS error while creating alert", "error")

    coins = crypto_service.get_top_cryptocurrencies(20)
    return render_template('create_alert.html', coins=coins)


@app.route('/watchlist')
def watchlist_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    global market_data, last_api_update
    
    if not market_data or not last_api_update or \
       (datetime.now() - last_api_update).seconds > 120:
        market_data = crypto_service.get_top_cryptocurrencies(50)
        last_api_update = datetime.now()
    
    from boto3.dynamodb.conditions import Key

    response = watchlist_table.query(
        KeyConditionExpression=Key('username').eq(session['username'])
    )

    user_watchlist_items = [
        item['coin_id'] for item in response.get('Items', [])
    ]

    watchlist_data = [
        coin for coin in market_data if coin['id'] in user_watchlist_items
    ]
    
    return render_template(
        'watchlist.html',
        watchlist=watchlist_data,
        username=session['username']
    )


@app.route('/alerts/toggle/<int:alert_id>', methods=['POST'])
def toggle_alert(alert_id):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        alerts_table.update_item(
            Key={
                'username': session['username'],
                'alert_id': alert_id
            },
            UpdateExpression="SET active = NOT active",
            ReturnValues="UPDATED_NEW"
        )

        return jsonify({'success': True})

    except Exception as e:
        print("Toggle alert error:", e)
        return jsonify({'error': 'AWS error'}), 500


@app.route('/alerts/delete/<int:alert_id>', methods=['POST'])
def delete_alert_route(alert_id):
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        alerts_table.delete_item(
            Key={
                'username': session['username'],
                'alert_id': alert_id
            }
        )

        return jsonify({
            'success': True,
            'message': 'Alert deleted successfully'
        })

    except Exception as e:
        print("Delete alert AWS error:", e)
        return jsonify({'error': 'AWS error'}), 500

@app.route('/api/crypto/prices')
def api_crypto_prices():
    """API endpoint to get current crypto prices"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    global market_data, last_api_update
    
    if not market_data or not last_api_update or \
       (datetime.now() - last_api_update).seconds > 60:
        market_data = crypto_service.get_top_cryptocurrencies(50)
        last_api_update = datetime.now()
    
    return jsonify({
        'data': market_data[:20],
        'last_updated': last_api_update.strftime('%Y-%m-%d %H:%M:%S') if last_api_update else None
    })

# Enhanced Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    global market_data, last_api_update

    if not market_data or not last_api_update or \
       (datetime.now() - last_api_update).seconds > 120:
        market_data = crypto_service.get_top_cryptocurrencies(10)
        last_api_update = datetime.now()

    # 🔹 FETCH WATCHLIST FROM DYNAMODB
    try:
        watchlist_response = watchlist_table.query(
            KeyConditionExpression=Key('username').eq(session['username'])
        )
        watchlist_items = [item['coin_id'] for item in watchlist_response.get('Items', [])]
    except Exception as e:
        print("Dashboard watchlist error:", e)
        watchlist_items = []

    watchlist_data = [coin for coin in market_data if coin['id'] in watchlist_items]

    # 🔹 FETCH ALERTS COUNT
    try:
        alerts_response = alerts_table.query(
            KeyConditionExpression=Key('username').eq(session['username'])
        )
        active_alerts = [a for a in alerts_response.get('Items', []) if a.get('active', True)]
    except Exception as e:
        print("Dashboard alerts error:", e)
        active_alerts = []

    return render_template(
        'dashboard.html',
        username=session['username'],
        top_cryptocurrencies=market_data[:5],
        watchlist=watchlist_data,
        alerts_count=len(active_alerts),
        market_stats={
            'total_market_cap': sum(c['market_cap'] for c in market_data),
            'total_volume_24h': sum(c['volume_24h'] for c in market_data),
            'positive_changes': len([c for c in market_data if c['change_24h'] > 0]),
            'negative_changes': len([c for c in market_data if c['change_24h'] < 0])
        }
    )



# Guest Dashboard (for non-authenticated users)
@app.route('/guest')
def guest_dashboard():
    """Guest dashboard for viewing cryptocurrency information without login"""
    global market_data
    
    if not market_data:
        market_data = crypto_service.get_top_cryptocurrencies(20)
    
    # Get top 10 coins for guest view
    guest_market_data = market_data[:10]
    
    # Calculate market stats
    market_stats = {
        'total_coins': len(market_data),
        'avg_change_24h': sum(c.get('change_24h', 0) for c in market_data) / len(market_data) if market_data else 0,
        'top_gainer': max(market_data, key=lambda x: x.get('change_24h', 0)) if market_data else None,
        'top_loser': min(market_data, key=lambda x: x.get('change_24h', 0)) if market_data else None
    }
    
    return render_template('guest_dashboard.html',
                         market_data=guest_market_data,
                         market_stats=market_stats)

# Enhanced Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    global market_data

    if not market_data:
        market_data = crypto_service.get_top_cryptocurrencies(50)

    try:
        users = users_table.scan().get('Items', [])
        watchlists = watchlist_table.scan().get('Items', [])
        alerts = alerts_table.scan().get('Items', [])
    except Exception as e:
        print("Admin dashboard AWS error:", e)
        users, watchlists, alerts = [], [], []

    # 🔹 Group watchlists by user
    user_watchlists = {}
    for item in watchlists:
        user_watchlists.setdefault(item['username'], []).append(item['coin_id'])

    # 🔹 Group alerts by user
    user_alerts = {}
    for alert in alerts:
        user_alerts.setdefault(alert['username'], []).append(alert)

    return render_template(
        'admin_dashboard.html',
        username=session['admin'],
        total_users=len(users),
        total_watchlists=len(watchlists),
        total_alerts=len(alerts),
        market_data=market_data[:10],
        market_stats={
            'total_coins': len(market_data),
            'avg_change_24h': sum(c['change_24h'] for c in market_data) / len(market_data),
            'top_gainer': max(market_data, key=lambda x: x['change_24h']),
            'top_loser': min(market_data, key=lambda x: x['change_24h'])
        },
        user_actions=user_watchlists,
        price_alerts=user_alerts
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)
