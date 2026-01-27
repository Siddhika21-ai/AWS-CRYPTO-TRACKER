# AWS Cryptocurrency Price Tracker

A scalable, real-time cryptocurrency price tracking application built with Flask and designed for AWS deployment.

## 🚀 Features

### Core Functionality
- **Real-time Price Tracking**: Live cryptocurrency prices from CoinGecko API
- **User Authentication**: Secure login/signup system for users and admins
- **Watchlist Management**: Add/remove cryptocurrencies from personal watchlists
- **Price Alerts**: Set custom price notifications (above/below thresholds)
- **Search Functionality**: Find cryptocurrencies by name or symbol
- **Detailed Analytics**: Market statistics and historical data

### User Roles
- **Guest**: Browse homepage and about page
- **Registered User**: Full access to dashboard, crypto market, search, watchlists, and alerts
- **Administrator**: Platform analytics, user management, and system monitoring

### AWS Integration Ready
- **Amazon EC2**: Web server deployment
- **Amazon DynamoDB**: Data persistence and caching
- **AWS SNS**: Email notifications for price alerts
- **AWS IAM**: Secure authentication and authorization
- **AWS CloudWatch**: System monitoring and logging

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Local Setup

1. **Clone/Download the project**
   ```bash
   cd /path/to/project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:5000`

### Dependencies
- Flask==2.3.3 - Web framework
- requests==2.31.0 - HTTP client for API calls
- beautifulsoup4==4.12.2 - HTML parsing
- boto3==1.34.0 - AWS SDK
- python-dotenv==1.0.0 - Environment variables
- flask-sqlalchemy==3.0.5 - Database ORM
- werkzeug==2.3.7 - WSGI utilities

## 📱 Usage Guide

### For Users

1. **Sign Up**: Create a new account
2. **Login**: Access your personalized dashboard
3. **Explore Features**:
   - **Dashboard**: View market overview and your watchlist
   - **Crypto Market**: Browse all cryptocurrencies with real-time prices
   - **Search**: Find specific cryptocurrencies
   - **Watchlist**: Manage your favorite coins
   - **Price Alerts**: Set notifications for price movements

### For Administrators

1. **Admin Signup**: Create an admin account
2. **Admin Login**: Access the admin dashboard
3. **Manage Platform**:
   - View user statistics and analytics
   - Monitor market performance
   - Check AWS service status
   - Access system metrics

## 🏗️ Project Structure

```
aws_capstone_project_deployment-main/
├── app.py                 # Main Flask application
├── crypto_service.py       # Cryptocurrency data service
├── requirements.txt        # Python dependencies
├── static/
│   └── style.css         # Styling and UI components
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── login.html       # User login
│   ├── signup.html      # User registration
│   ├── dashboard.html   # User dashboard
│   ├── crypto_market.html # Cryptocurrency market
│   ├── crypto_search.html # Search functionality
│   ├── crypto_details.html # Coin details
│   ├── price_alerts.html  # Price alerts management
│   ├── create_alert.html  # Create new alert
│   ├── admin_login.html   # Admin login
│   ├── admin_signup.html  # Admin registration
│   ├── admin_dashboard.html # Admin dashboard
│   └── about.html        # About page
└── venv/                # Virtual environment
```

## 🔧 API Integration

### CoinGecko API
- **Endpoint**: `https://api.coingecko.com/api/v3`
- **Features**:
  - Real-time price data
  - Market statistics
  - Historical price data
  - Cryptocurrency search
- **Rate Limiting**: 10-50 requests per minute (free tier)

### Data Caching
- Market data cached for 2 minutes
- Reduces API calls and improves performance
- Automatic refresh on page reload

## 🌐 AWS Deployment Guide

### EC2 Setup
1. Launch EC2 instance (t2.micro or larger)
2. Configure security groups (HTTP, HTTPS, SSH)
3. Install Python and dependencies
4. Deploy application code
5. Set up process manager (systemd)

### DynamoDB Integration
1. Create DynamoDB tables:
   - `users` - User accounts
   - `watchlists` - User watchlists
   - `alerts` - Price alerts
   - `market_data` - Cached market data

### SNS Configuration
1. Create SNS topic for notifications
2. Configure email subscriptions
3. Set up Lambda functions for alert processing

### IAM Roles
1. Create IAM role for EC2 instance
2. Attach policies for DynamoDB and SNS access
3. Configure least-privilege permissions

## 🔒 Security Features

- Session-based authentication
- Input validation and sanitization
- CSRF protection
- Secure password handling (in production, use bcrypt)
- AWS IAM integration for cloud services

## 📊 Monitoring & Analytics

### Application Metrics
- User registration and activity
- API usage statistics
- Price alert performance
- Error tracking and logging

### AWS CloudWatch
- Application performance monitoring
- Resource utilization tracking
- Custom metrics and alerts
- Log aggregation and analysis

## 🚀 Performance Optimizations

- Data caching to reduce API calls
- Efficient database queries
- Responsive design for mobile devices
- Lazy loading for large datasets
- CDN integration for static assets

## 🧪 Testing

### Manual Testing
1. User registration and login flow
2. Cryptocurrency search functionality
3. Watchlist add/remove operations
4. Price alert creation and management
5. Admin dashboard functionality

### API Testing
```bash
# Test cryptocurrency prices endpoint
curl -X GET "http://127.0.0.1:5000/api/crypto/prices" \
  -H "Cookie: session=<your-session-cookie>"
```

## 🐛 Troubleshooting

### Common Issues

1. **API Rate Limits**: If you hit rate limits, the app will fall back to cached data
2. **Session Issues**: Clear browser cookies if login/logout doesn't work
3. **Template Errors**: Check for proper session variable usage in templates
4. **Import Errors**: Ensure all dependencies are installed correctly

### Debug Mode
The application runs in debug mode by default. For production:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## 📈 Future Enhancements

- **Mobile App**: React Native or Flutter application
- **WebSocket Integration**: Real-time price updates without page refresh
- **Machine Learning**: Price prediction algorithms
- **Portfolio Tracking**: Investment performance analytics
- **Social Features**: Community discussions and sharing
- **Advanced Charts**: Technical analysis tools

## 📄 License

This project is part of an AWS Capstone demonstration. For educational purposes only.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review AWS documentation for cloud services
- Consult CoinGecko API documentation

---

**Note**: This is a demonstration project for AWS Capstone purposes. Production deployment requires additional security considerations, scalability planning, and proper AWS resource configuration.
