import React, { useState, useEffect } from 'react';
import { Coins, TrendingUp, TrendingDown, ArrowRight, CheckCircle, Clock, AlertCircle, Copy, Check } from 'lucide-react';
import { toast } from 'sonner';

const KodakGPPro = ({ api, user, selectedCurrency, refreshWallet }) => {
  const [activeTab, setActiveTab] = useState('buy');
  const [rates, setRates] = useState(null);
  const [amount, setAmount] = useState(100);
  const [usdValue, setUsdValue] = useState(0);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('crypto');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchRates();
    if (user) fetchOrders();
  }, [user]);

  useEffect(() => {
    if (rates) {
      const rate = activeTab === 'buy' ? rates.buy_rate : rates.sell_rate;
      setUsdValue((amount * rate).toFixed(2));
    }
  }, [amount, activeTab, rates]);

  const fetchRates = async () => {
    try {
      const res = await api.get('/kodakgp/rates');
      setRates(res.data);
    } catch (err) {
      console.error('Failed to fetch rates:', err);
    }
  };

  const fetchOrders = async () => {
    try {
      const res = await api.get('/kodakgp/orders');
      setOrders(res.data);
    } catch (err) {
      console.error('Failed to fetch orders:', err);
    }
  };

  const handleOrder = async () => {
    if (!user) {
      toast.error('Please login first');
      return;
    }
    if (amount <= 0) {
      toast.error('Invalid amount');
      return;
    }

    setLoading(true);
    try {
      const res = await api.post('/kodakgp/order', {
        order_type: activeTab,
        amount_gp: amount * 1000000,
        payment_method: paymentMethod,
        currency: selectedCurrency
      });

      toast.success(`${activeTab === 'buy' ? 'Buy' : 'Sell'} order placed! Reference: ${res.data.order_id}`);
      setAmount(100);
      fetchOrders();
      refreshWallet();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Order failed');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="status-icon success" />;
      case 'pending':
        return <Clock className="status-icon pending" />;
      case 'failed':
        return <AlertCircle className="status-icon error" />;
      default:
        return <Clock className="status-icon" />;
    }
  };

  return (
    <div className="kodakgp-pro">
      {/* Header */}
      <div className="kodakgp-header-pro">
        <div className="header-left">
          <Coins size={48} className="header-icon" />
          <div>
            <h1>KodakGP Exchange</h1>
            <p>Professional OSRS Gold Trading</p>
          </div>
        </div>
        <div className="header-stats">
          {rates && (
            <>
              <div className="stat-card">
                <TrendingUp size={20} className="icon buy" />
                <div>
                  <div className="stat-label">Buy Rate</div>
                  <div className="stat-value">${rates.buy_rate}/M</div>
                </div>
              </div>
              <div className="stat-card">
                <TrendingDown size={20} className="icon sell" />
                <div>
                  <div className="stat-label">Sell Rate</div>
                  <div className="stat-value">${rates.sell_rate}/M</div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Main Trading Section */}
      <div className="trading-section">
        {/* Tabs */}
        <div className="trading-tabs">
          <button
            className={`tab ${activeTab === 'buy' ? 'active' : ''}`}
            onClick={() => setActiveTab('buy')}
          >
            <TrendingUp size={20} />
            BUY GOLD
          </button>
          <button
            className={`tab ${activeTab === 'sell' ? 'active' : ''}`}
            onClick={() => setActiveTab('sell')}
          >
            <TrendingDown size={20} />
            SELL GOLD
          </button>
        </div>

        {/* Trading Card */}
        <div className="trading-card">
          <div className="trading-form">
            {/* Amount Input */}
            <div className="form-group">
              <label>Amount (Millions)</label>
              <div className="input-with-buttons">
                <button
                  className="quick-btn"
                  onClick={() => setAmount(50)}
                >
                  50M
                </button>
                <button
                  className="quick-btn"
                  onClick={() => setAmount(100)}
                >
                  100M
                </button>
                <button
                  className="quick-btn"
                  onClick={() => setAmount(500)}
                >
                  500M
                </button>
                <button
                  className="quick-btn"
                  onClick={() => setAmount(1000)}
                >
                  1B
                </button>
              </div>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(parseInt(e.target.value) || 0)}
                placeholder="Enter amount in millions"
                min="1"
              />
            </div>

            {/* USD Conversion */}
            <div className="conversion-display">
              <div className="conversion-item">
                <span className="label">{amount}M GP</span>
                <ArrowRight size={20} />
                <span className="value">${usdValue}</span>
              </div>
            </div>

            {/* Payment Method */}
            <div className="form-group">
              <label>Payment Method</label>
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
              >
                <option value="crypto">Cryptocurrency</option>
                <option value="paypal">PayPal</option>
                <option value="bank">Bank Transfer</option>
              </select>
            </div>

            {/* Order Summary */}
            <div className="order-summary">
              <div className="summary-row">
                <span>Gold Amount:</span>
                <span className="value">{amount}M</span>
              </div>
              <div className="summary-row">
                <span>Rate:</span>
                <span className="value">
                  ${activeTab === 'buy' ? rates?.buy_rate : rates?.sell_rate}/M
                </span>
              </div>
              <div className="summary-row total">
                <span>Total Value:</span>
                <span className="value">${usdValue}</span>
              </div>
            </div>

            {/* CTA Button */}
            <button
              className="btn btn-primary btn-large btn-full"
              onClick={handleOrder}
              disabled={loading || !rates}
            >
              {loading ? 'Processing...' : `${activeTab === 'buy' ? 'BUY' : 'SELL'} NOW`}
            </button>

            {/* Disclaimer */}
            <div className="disclaimer">
              <AlertCircle size={16} />
              <p>
                ⚠️ Cloutscape RSPS-GP only. NOT affiliated with Jagex. 
                For entertainment purposes only. Processing time: 5-30 minutes.
              </p>
            </div>
          </div>

          {/* Info Panel */}
          <div className="info-panel">
            <h3>How It Works</h3>
            <div className="steps">
              <div className="step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h4>Select Amount</h4>
                  <p>Choose how much gold you want to buy or sell</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h4>Choose Payment</h4>
                  <p>Select your preferred payment method</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h4>Confirm Order</h4>
                  <p>Review and submit your order</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h4>Complete</h4>
                  <p>Receive your gold or payment within 30 minutes</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Active Orders */}
      {orders.length > 0 && (
        <div className="active-orders">
          <h2>Your Orders</h2>
          <div className="orders-grid">
            {orders.map((order) => (
              <div key={order.id} className={`order-card status-${order.status}`}>
                <div className="order-header">
                  <div className="order-id">
                    <span className="label">Order ID:</span>
                    <span className="value">{order.id}</span>
                    <button
                      className="copy-btn"
                      onClick={() => copyToClipboard(order.id)}
                    >
                      {copied ? <Check size={16} /> : <Copy size={16} />}
                    </button>
                  </div>
                  {getStatusIcon(order.status)}
                </div>

                <div className="order-details">
                  <div className="detail-row">
                    <span className="label">Type:</span>
                    <span className={`value ${order.type}`}>
                      {order.type === 'buy' ? 'BUY' : 'SELL'}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Amount:</span>
                    <span className="value">{order.amount_gp / 1000000}M GP</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Value:</span>
                    <span className="value">${order.usd_value}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Status:</span>
                    <span className={`status-badge status-${order.status}`}>
                      {order.status.toUpperCase()}
                    </span>
                  </div>
                </div>

                {order.status === 'pending' && (
                  <div className="order-action">
                    <Clock size={16} />
                    <span>Processing... Check back soon</span>
                  </div>
                )}
                {order.status === 'completed' && (
                  <div className="order-action success">
                    <CheckCircle size={16} />
                    <span>Order completed successfully</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Benefits */}
      <div className="benefits-section">
        <h2>Why Choose KodakGP?</h2>
        <div className="benefits-grid">
          <div className="benefit-card">
            <div className="benefit-icon">⚡</div>
            <h3>Lightning Fast</h3>
            <p>5-30 minute processing times</p>
          </div>
          <div className="benefit-card">
            <div className="benefit-icon">💎</div>
            <h3>Best Rates</h3>
            <p>Competitive buy/sell spreads</p>
          </div>
          <div className="benefit-card">
            <div className="benefit-icon">🔒</div>
            <h3>Secure</h3>
            <p>Military-grade encryption</p>
          </div>
          <div className="benefit-card">
            <div className="benefit-icon">🤝</div>
            <h3>Professional</h3>
            <p>Trusted by thousands of degens</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KodakGPPro;
