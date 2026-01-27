import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from typing import Dict, List, Optional

class CryptoDataService:
    def __init__(self):
        self.coinmarketcap_url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing"
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self.crypto_compare_url = "https://min-api.cryptocompare.com/data/v2"
        
    def get_top_cryptocurrencies(self, limit: int = 100) -> List[Dict]:
        """Get top cryptocurrencies by market cap using CoinGecko (free API)"""
        try:
            # Add delay to prevent rate limiting
            time.sleep(0.5)
            url = f"{self.coingecko_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': 'false'
            }
            
            response = requests.get(url, params=params, timeout=10)
            # Add delay to prevent rate limiting
            time.sleep(0.5)
            response.raise_for_status()
            
            data = response.json()
            # Add delay to prevent rate limiting
            time.sleep(0.5)
            return self._format_coingecko_data(data)
            
        except requests.RequestException as e:
            print(f"Error fetching cryptocurrency data: {e}")
            # Check if it's a rate limit error
            if "429" in str(e) or "Too Many Requests" in str(e):
                print("API rate limit reached, using fallback data")
                return self._get_fallback_data()
            return self._get_fallback_data()
    
    def _format_coingecko_data(self, data: List[Dict]) -> List[Dict]:
        """Format CoinGecko data to standard format"""
        formatted = []
        
        for coin in data:
            image_data = coin.get('image')
            
            if isinstance(image_data, dict):
                thumb = image_data.get('thumb', '')
                large = image_data.get('large', '')
            else:
                thumb = image_data or ''
                large = image_data or ''
            
            formatted.append({
                'id': coin.get('id'),
                'symbol': coin.get('symbol', '').upper(),
                'name': coin.get('name', ''),
                'rank': coin.get('market_cap_rank', 0),
                
                'thumb': thumb,
                'image': large,
                
                'price': coin.get('current_price', 0),
                'market_cap': coin.get('market_cap', 0),
                'volume_24h': coin.get('total_volume', 0),
                'change_24h': coin.get('price_change_percentage_24h', 0),
                
                'high_24h': coin.get('high_24h', 0),
                'low_24h': coin.get('low_24h', 0),
                
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return formatted
    
    def search_cryptocurrency(self, query: str) -> List[Dict]:
        """Search for cryptocurrencies by name or symbol"""
        try:
            url = f"{self.coingecko_url}/search"
            params = {'query': query}
            
            response = requests.get(url, params=params, timeout=10)
            # Add delay to prevent rate limiting
            time.sleep(0.5)
            response.raise_for_status()
            
            data = response.json()
            coins = data.get('coins', [])[:10]  # Limit to 10 results
            
            formatted = []
            for coin in coins:
                # Use basic search data with reasonable defaults
                formatted.append({
                    'id': coin['id'],
                    'symbol': coin['symbol'].upper(),
                    'name': coin['name'],
                    'market_cap_rank': coin.get('market_cap_rank', 0),
                    'thumb': coin.get('thumb', ''),
                    'large': coin.get('large', ''),
                    'price': 0.01,  # Default price to avoid showing 0
                    'market_cap': coin.get('market_cap_rank', 0) * 1000000,  # Estimate market cap
                    'volume_24h': 1000000,  # Default volume
                    'change_24h': 0.0  # Default change
                })
            
            return formatted
            
        except requests.RequestException as e:
            print(f"Error searching cryptocurrency: {e}")
            return []
    
    def get_cryptocurrency_details(self, coin_id: str) -> Optional[Dict]:
        """Get detailed information for a specific cryptocurrency"""
        try:
            url = f"{self.coingecko_url}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false',
                'sparkline': 'false'
            }
            
            response = requests.get(url, params=params, timeout=10)
            # Add delay to prevent rate limiting
            time.sleep(0.5)
            response.raise_for_status()
            
            data = response.json()
            
            return {
    'id': data['id'],
    'symbol': data['symbol'].upper(),
    'name': data['name'],
    'description': data['description'].get('en', ''),
    'image': data['image']['large'],

    'price': data['market_data']['current_price']['usd'],
    'market_cap': data['market_data']['market_cap']['usd'],
    'volume_24h': data['market_data']['total_volume']['usd'],
    'change_24h': data['market_data']['price_change_percentage_24h'],
    'high_24h': data['market_data']['high_24h']['usd'],
    'low_24h': data['market_data']['low_24h']['usd'],

    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}
                    
        except requests.RequestException as e:
            print(f"Error fetching cryptocurrency details: {e}")
            # Check if it's a rate limit error
            if "429" in str(e) or "Too Many Requests" in str(e):
                print("API rate limit reached for details, using fallback")
                # Try to find in fallback data
                fallback_data = self._get_fallback_data()
                for coin in fallback_data:
                    if coin['id'] == coin_id:
                        return coin
                return None
            return None
    
    def get_price_history(self, coin_id: str, days: int = 7) -> List[Dict]:
        """Get historical price data for a cryptocurrency"""
        try:
            url = f"{self.coingecko_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily' if days > 1 else 'hourly'
            }
            
            response = requests.get(url, params=params, timeout=10)
            # Add delay to prevent rate limiting
            time.sleep(0.5)
            response.raise_for_status()
            
            data = response.json()
            prices = data.get('prices', [])
            
            formatted = []
            for price_point in prices:
                timestamp = price_point[0] / 1000  # Convert milliseconds to seconds
                formatted.append({
                    'timestamp': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                    'price': price_point[1]
                })
            
            return formatted
            
        except requests.RequestException as e:
            print(f"Error fetching price history: {e}")
            # Check if it's a rate limit error
            if "429" in str(e) or "Too Many Requests" in str(e):
                print("API rate limit reached for price history, returning empty data")
                return []
            return []
    
    def _get_fallback_data(self) -> List[Dict]:
        """Fallback data when API is unavailable"""
        return [
            {
                'id': 'bitcoin',
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'price': 45000.00,
                'market_cap': 880000000000,
                'volume_24h': 25000000000,
                'change_24h': 2.5,
                'rank': 1,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image': '',
                'high_24h': 46000.00,
                'low_24h': 44000.00
            },
            {
                'id': 'ethereum',
                'symbol': 'ETH',
                'name': 'Ethereum',
                'price': 2800.00,
                'market_cap': 336000000000,
                'volume_24h': 15000000000,
                'change_24h': 3.2,
                'rank': 2,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image': '',
                'high_24h': 2900.00,
                'low_24h': 2700.00
            },
            {
                'id': 'tether',
                'symbol': 'USDT',
                'name': 'Tether',
                'price': 1.00,
                'market_cap': 83000000000,
                'volume_24h': 40000000000,
                'change_24h': 0.1,
                'rank': 3,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image': '',
                'high_24h': 1.01,
                'low_24h': 0.99
            },
            {
                'id': 'binancecoin',
                'symbol': 'BNB',
                'name': 'BNB',
                'price': 320.00,
                'market_cap': 49000000000,
                'volume_24h': 1200000000,
                'change_24h': -1.5,
                'rank': 4,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image': '',
                'high_24h': 325.00,
                'low_24h': 315.00
            },
            {
                'id': 'solana',
                'symbol': 'SOL',
                'name': 'Solana',
                'price': 105.00,
                'market_cap': 45000000000,
                'volume_24h': 2000000000,
                'change_24h': 4.8,
                'rank': 5,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image': '',
                'high_24h': 108.00,
                'low_24h': 102.00
            },
            {
                'id': 'cardano',
                'symbol': 'ADA',
                'name': 'Cardano',
                'price': 0.55,
                'market_cap': 19000000000,
                'volume_24h': 500000000,
                'change_24h': 2.1,
                'rank': 6,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image': '',
                'high_24h': 0.56,
                'low_24h': 0.54
            },
            {
                'id': 'xrp',
                'symbol': 'XRP',
                'name': 'XRP',
                'price': 0.62,
                'market_cap': 34000000000,
                'volume_24h': 1200000000,
                'change_24h': -0.8,
                'rank': 7,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image': '',
                'high_24h': 0.63,
                'low_24h': 0.61
            },
            {
                'id': 'polkadot',
                'symbol': 'DOT',
                'name': 'Polkadot',
                'price': 8.50,
                'market_cap': 11000000000,
                'volume_24h': 300000000,
                'change_24h': 1.2,
                'rank': 8,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image': '',
                'high_24h': 8.65,
                'low_24h': 8.35
            },
            {
                'id': 'dogecoin',
                'symbol': 'DOGE',
                'name': 'Dogecoin',
                'price': 0.085,
                'market_cap': 12000000000,
                'volume_24h': 800000000,
                'change_24h': 5.5,
                'rank': 9,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image': '',
                'high_24h': 0.087,
                'low_24h': 0.083
            },
            {
                'id': 'avalanche-2',
                'symbol': 'AVAX',
                'name': 'Avalanche',
                'price': 38.00,
                'market_cap': 14000000000,
                'volume_24h': 400000000,
                'change_24h': -2.1,
                'rank': 10,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image': '',
                'high_24h': 38.80,
                'low_24h': 37.20
            }
        ]

# Global instance
crypto_service = CryptoDataService()
