/**
 * API Client with Tunnel-Aware Endpoint Configuration
 * Supports Cloudflared tunnel, local development, and fallback endpoints
 */

class APIClient {
  constructor() {
    this.baseURL = this.getBaseURL();
    this.timeout = parseInt(process.env.REACT_APP_API_TIMEOUT || '30000');
    this.token = localStorage.getItem('auth_token');
  }

  /**
   * Determine the appropriate API endpoint
   * Priority: Cloudflared Tunnel > Local > Fallback
   */
  getBaseURL() {
    // Check if running in production (APK or web)
    const env = process.env.REACT_APP_ENV || 'development';
    
    if (env === 'production') {
      // Use Cloudflared tunnel endpoint
      return process.env.REACT_APP_BACKEND_URL || 'https://kodakclout-prod.workers.dev';
    }
    
    // Development: use local backend
    return process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  }

  /**
   * Set authentication token
   */
  setToken(token) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  /**
   * Clear authentication token
   */
  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  /**
   * Make HTTP request with retry logic
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}/api${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config = {
      method: options.method || 'GET',
      headers,
      timeout: this.timeout,
      ...options,
    };

    if (options.body) {
      config.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        if (response.status === 401) {
          this.clearToken();
          window.location.href = '/login';
        }
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Request Failed: ${endpoint}`, error);
      throw error;
    }
  }

  /**
   * Authentication endpoints
   */
  auth = {
    register: (data) => this.request('/auth/register', { method: 'POST', body: data }),
    login: (data) => this.request('/auth/login', { method: 'POST', body: data }),
    logout: () => this.request('/auth/logout', { method: 'POST' }),
    verify: () => this.request('/auth/verify', { method: 'GET' }),
  };

  /**
   * Wallet endpoints
   */
  wallet = {
    getBalance: () => this.request('/wallet', { method: 'GET' }),
    getConfig: () => this.request('/wallet/config', { method: 'GET' }),
    deposit: (data) => this.request('/wallet/deposit', { method: 'POST', body: data }),
    withdraw: (data) => this.request('/wallet/withdraw', { method: 'POST', body: data }),
    getTransactions: () => this.request('/wallet/transactions', { method: 'GET' }),
  };

  /**
   * Game endpoints
   */
  games = {
    placeBet: (data) => this.request('/games/bet', { method: 'POST', body: data }),
    getHistory: (limit = 50) => this.request(`/games/history?limit=${limit}`, { method: 'GET' }),
    getLive: (limit = 20) => this.request(`/games/live?limit=${limit}`, { method: 'GET' }),
  };

  /**
   * Provably Fair endpoints
   */
  provablyFair = {
    getInfo: () => this.request('/provably-fair', { method: 'GET' }),
    rotateSeed: (data) => this.request('/provably-fair/rotate', { method: 'POST', body: data }),
    verify: (data) => this.request('/provably-fair/verify', { method: 'POST', body: data }),
  };

  /**
   * Chat endpoints
   */
  chat = {
    getMessages: (limit = 50) => this.request(`/chat/messages?limit=${limit}`, { method: 'GET' }),
    sendMessage: (data) => this.request('/chat/send', { method: 'POST', body: data }),
    sendTip: (data) => this.request('/chat/tip', { method: 'POST', body: data }),
    makeItRain: (data) => this.request('/chat/rain', { method: 'POST', body: data }),
  };

  /**
   * VIP endpoints
   */
  vip = {
    getStatus: () => this.request('/vip/status', { method: 'GET' }),
    claimRakeback: () => this.request('/vip/claim-rakeback', { method: 'POST' }),
    claimLossback: () => this.request('/vip/claim-lossback', { method: 'POST' }),
  };

  /**
   * Leaderboard endpoints
   */
  leaderboard = {
    getTop: (period = 'all') => this.request(`/leaderboard?period=${period}`, { method: 'GET' }),
  };

  /**
   * Referral endpoints
   */
  referral = {
    getInfo: () => this.request('/referral/info', { method: 'GET' }),
    redeem: (data) => this.request('/referral/redeem', { method: 'POST', body: data }),
  };

  /**
   * KodakGP endpoints
   */
  kodakgp = {
    getRates: () => this.request('/kodakgp/rates', { method: 'GET' }),
    createOrder: (data) => this.request('/kodakgp/order', { method: 'POST', body: data }),
    requestService: (data) => this.request('/kodakgp/service', { method: 'POST', body: data }),
    getOrders: () => this.request('/kodakgp/orders', { method: 'GET' }),
  };
}

// Export singleton instance
export default new APIClient();
