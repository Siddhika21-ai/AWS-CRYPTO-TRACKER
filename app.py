# Hello I am Teja this is a sample templete code for AWS Capstone project
# Hello again
# I am testing git push and pull

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from crypto_service import crypto_service
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# In-memory database (dictionary)
users = {}
admin_users = {}

# In-memory crypto data storage
user_watchlists = {}

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
        
        print(f"DEBUG: Username: {username}, Password: {password}")
        
        # Validate password strength
        is_valid, message = validate_password(password)
        print(f"DEBUG: Password valid: {is_valid}, Message: {message}")
        
        if not is_valid:
            flash(message, 'error')
            print(f"DEBUG: Flashed error message: {message}")
            return render_template('signup.html')
        
        if username in users:
            flash("User already exists!", 'error')
            print(f"DEBUG: Flashed user exists message")
            return render_template('signup.html')
        
        users[username] = password
        flash("Account created successfully! Please login.", 'success')
        print(f"DEBUG: Flashed success message")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))  # ✅ HOME first

        return "Invalid credentials!"

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
        
        print(f"DEBUG: Admin Username: {username}, Password: {password}")
        
        # Validate password strength
        is_valid, message = validate_password(password)
        print(f"DEBUG: Admin password valid: {is_valid}, Message: {message}")
        
        if not is_valid:
            flash(message, 'error')
            print(f"DEBUG: Flashed admin error message: {message}")
            return render_template('admin_signup.html')
        
        if username in admin_users:
            flash("Admin already exists!", 'error')
            print(f"DEBUG: Flashed admin exists message")
            return render_template('admin_signup.html')
        
        admin_users[username] = password
        flash("Admin account created successfully! Please login.", 'success')
        print(f"DEBUG: Flashed admin success message")
        return redirect(url_for('admin_login'))
    return render_template('admin_signup.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in admin_users and admin_users[username] == password:
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        return "Invalid admin credentials!"
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
    
    # Update market data if needed (cache for 2 minutes)
    if not market_data or not last_api_update or \
       (datetime.now() - last_api_update).seconds > 120:
        market_data = crypto_service.get_top_cryptocurrencies(50)
        last_api_update = datetime.now()
    
    user_watchlist_items = user_watchlists.get(session['username'], [])
    watchlist_data = [coin for coin in market_data if coin['id'] in user_watchlist_items]
    
    return render_template('crypto_market.html', 
                         cryptocurrencies=market_data[:20],
                         watchlist=watchlist_data,
                         watchlist_items=user_watchlist_items,
                         username=session['username'])

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

@app.route('/crypto/<coin_id>')
def crypto_details(coin_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    coin_details = crypto_service.get_cryptocurrency_details(coin_id)
    price_history = crypto_service.get_price_history(coin_id, 7)
    
    if not coin_details:
        return "Cryptocurrency not found!", 404
    
    in_watchlist = coin_id in user_watchlists.get(session['username'], [])
    
    return render_template('crypto_details.html',
                         coin=coin_details,
                         price_history=price_history,
                         in_watchlist=in_watchlist,
                         username=session['username'])

@app.route('/watchlist/add/<coin_id>', methods=['POST'])
def add_to_watchlist(coin_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user_watchlists.setdefault(username, [])

    if coin_id not in user_watchlists[username]:
        user_watchlists[username].append(coin_id)
        flash("Added to watchlist ✅")

    return redirect(request.referrer or url_for('crypto_market'))

@app.route('/watchlist/remove/<coin_id>', methods=['POST'])
def remove_from_watchlist(coin_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    if coin_id in user_watchlists.get(username, []):
        user_watchlists[username].remove(coin_id)
        flash("Removed from watchlist ❌")

    return redirect(request.referrer or url_for('crypto_market'))
    
@app.route('/alerts')
def alerts_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_alerts = price_alerts.get(session['username'], [])
    return render_template('price_alerts.html',
                         alerts=user_alerts,
                         username=session['username'])

@app.route('/alerts/create', methods=['GET', 'POST'])
def create_alert():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        coin_id = request.form.get('coin_id')
        coin_name = request.form.get('coin_name')
        alert_type = request.form.get('alert_type')  # 'above' or 'below'
        target_price = float(request.form.get('target_price'))
        
        username = session['username']
        if username not in price_alerts:
            price_alerts[username] = []
        
        alert = {
            'id': len(price_alerts[username]) + 1,
            'coin_id': coin_id,
            'coin_name': coin_name,
            'alert_type': alert_type,
            'target_price': target_price,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'active': True
        }
        
        price_alerts[username].append(alert)
        return redirect(url_for('alerts_page'))
    
    # Get top 20 coins for selection
    top_coins = crypto_service.get_top_cryptocurrencies(20)
    return render_template('create_alert.html',
                         coins=top_coins,
                         username=session['username'])

@app.route('/watchlist')
def watchlist_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    global market_data, last_api_update
    
    # Get fresh market data
    if not market_data or not last_api_update or \
       (datetime.now() - last_api_update).seconds > 120:
        market_data = crypto_service.get_top_cryptocurrencies(50)
        last_api_update = datetime.now()
    
    user_watchlist_items = user_watchlists.get(session['username'], [])
    watchlist_data = [coin for coin in market_data if coin['id'] in user_watchlist_items]
    
    return render_template('watchlist.html',
                         watchlist=watchlist_data,
                         username=session['username'])

@app.route('/alerts/toggle/<int:alert_id>', methods=['POST'])
def toggle_alert(alert_id):
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    username = session['username']
    if username in price_alerts:
        for alert in price_alerts[username]:
            if alert['id'] == alert_id:
                alert['active'] = not alert['active']
                return jsonify({'success': True, 'active': alert['active']})
    
    return jsonify({'error': 'Alert not found'}), 404

@app.route('/alerts/delete/<int:alert_id>', methods=['POST'])
def delete_alert_route(alert_id):
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    username = session['username']
    if username in price_alerts:
        price_alerts[username] = [alert for alert in price_alerts[username] if alert['id'] != alert_id]
        return jsonify({'success': True, 'message': 'Alert deleted successfully'})
    
    return jsonify({'error': 'Alert not found'}), 404

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
    
    # Get fresh market data
    if not market_data or not last_api_update or \
       (datetime.now() - last_api_update).seconds > 120:
        market_data = crypto_service.get_top_cryptocurrencies(10)
        last_api_update = datetime.now()
    
    user_watchlist_items = user_watchlists.get(session['username'], [])
    watchlist_data = [coin for coin in market_data if coin['id'] in user_watchlist_items]
    
    # Get user's alerts
    user_alerts_list = price_alerts.get(session['username'], [])
    active_alerts = [alert for alert in user_alerts_list if alert.get('active', True)]
    
    return render_template(
        'dashboard.html',
        username=session['username'],
        top_cryptocurrencies=market_data[:5],
        watchlist=watchlist_data,
        alerts_count=len(active_alerts),
        market_stats={
            'total_market_cap': sum(coin['market_cap'] for coin in market_data),
            'total_volume_24h': sum(coin['volume_24h'] for coin in market_data),
            'positive_changes': len([c for c in market_data if c.get('change_24h', 0) > 0]),
            'negative_changes': len([c for c in market_data if c.get('change_24h', 0) < 0])
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
    
    # Admin analytics
    total_users = len(users)
    total_watchlists = sum(len(watchlist) for watchlist in user_watchlists.values())
    total_alerts = sum(len(alerts) for alerts in price_alerts.values())
    
    return render_template('admin_dashboard.html', 
                         username=session['admin'],
                         total_users=total_users,
                         total_watchlists=total_watchlists,
                         total_alerts=total_alerts,
                         market_data=market_data[:10],
                         market_stats={
                             'total_coins': len(market_data),
                             'avg_change_24h': sum(c.get('change_24h', 0) for c in market_data) / len(market_data) if market_data else 0,
                             'top_gainer': max(market_data, key=lambda x: x.get('change_24h', 0)) if market_data else None,
                             'top_loser': min(market_data, key=lambda x: x.get('change_24h', 0)) if market_data else None
                         },
                         user_actions=user_watchlists,
                         all_users=users,
                         price_alerts=price_alerts)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
