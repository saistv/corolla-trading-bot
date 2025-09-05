# 🚗 Toyota Corolla Trading Bot

**Simple, reliable, gets the job done.**

## Philosophy
- **Reliable > Fancy**
- **Working > Perfect** 
- **Simple > Complex**
- **Profitable > Beautiful**

## 6-Week Development Plan

### Week 1: Get Data Flowing ✓
- [x] IBKR connection
- [x] Live NQ data feed
- [x] Basic logging

### Week 2: Calculate Indicators ✅ 
- [x] ATF (1m and 15m) - Manual calculations
- [x] SQZMOM (Squeeze Momentum) 
- [x] LuxAlgo S/R levels (Pivot detection)
- [x] 5-factor confluence strategy
- [ ] Validate against TradingView (Week 3)

### Week 3: Generate Signals ✅
- [x] 5-factor confluence logic implemented
- [x] Signal validation with strength scoring
- [x] Momentum window timing (6-candle window)
- [ ] TradingView parity testing

### Week 4: Execute Trades
- [ ] Paper trading
- [ ] Stop loss management
- [ ] Position tracking

### Week 5: Stability Testing
- [ ] 48-hour continuous run
- [ ] Error handling
- [ ] Performance optimization

### Week 6: Production Ready
- [ ] Monitoring dashboard
- [ ] Email alerts
- [ ] Auto-restart service
- [ ] Documentation

## Quick Start

```bash
cd corolla-trading-bot
pip install -r requirements.txt
python run.py
```

Dashboard: http://localhost:5000

## Success Metrics
- **Week 4**: First paper trade executes
- **Week 6**: 99% uptime over 1 week
- **Month 2**: Profitability check
- **Month 3**: Production ready

Keep it simple. Make it work. Ship it.