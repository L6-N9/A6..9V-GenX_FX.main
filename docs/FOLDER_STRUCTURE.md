# GenX FX Trading Platform - Folder Structure

## 📁 Project Architecture

```
GenX_FX/
├── 📱 frontend/                    # React Frontend Application
│   ├── src/
│   │   ├── components/            # Reusable UI components
│   │   ├── pages/                 # Route pages
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── services/              # API service calls
│   │   ├── utils/                 # Utility functions
│   │   └── types/                 # TypeScript type definitions
│   ├── public/                    # Static assets
│   └── package.json
│
├── 🚀 backend/                     # Python FastAPI Backend
│   ├── api/                       # API layer
│   │   ├── routers/               # API route handlers
│   │   ├── middleware/            # Authentication & CORS
│   │   ├── models/                # Pydantic request/response models
│   │   └── main.py                # FastAPI application entry point
│   │
│   ├── core/                      # Core trading logic
│   │   ├── indicators/            # Technical analysis indicators
│   │   ├── patterns/              # Chart pattern recognition
│   │   ├── strategies/            # Trading strategies
│   │   ├── execution/             # Order execution engine
│   │   └── risk_management.py     # Risk management system
│   │
│   ├── services/                  # Business logic services
│   │   ├── ai_service.py          # AI/ML prediction services
│   │   ├── market_data.py         # Real-time market data feeds
│   │   ├── news_service.py        # News aggregation & sentiment
│   │   ├── social_sentiment.py    # Social media sentiment analysis
│   │   └── notification_service.py # Discord/Telegram notifications
│   │
│   ├── ai_models/                 # Machine Learning Models
│   │   ├── ensemble_model.py      # Ensemble ML models
│   │   ├── market_predictor.py    # Market prediction algorithms
│   │   ├── sentiment_analyzer.py  # Sentiment analysis models
│   │   └── trained_models/        # Serialized model files (.joblib)
│   │
│   └── utils/                     # Utility functions
│       ├── database.py            # Database connections
│       ├── logger.py              # Logging configuration
│       └── config.py              # Application configuration
│
├── 🤖 expert_advisors/             # MetaTrader Expert Advisors
│   ├── mt4/                       # MT4 Expert Advisors (.mq4)
│   ├── mt5/                       # MT5 Expert Advisors (.mq5)
│   └── includes/                  # Shared MQL libraries
│
├── 📊 data/                        # Data storage & management
│   ├── historical/                # Historical market data
│   ├── models/                    # Trained model storage
│   ├── logs/                      # Application logs
│   └── cache/                     # Cached data files
│
├── 🔧 scripts/                     # Automation & utility scripts
│   ├── setup/                     # Environment setup scripts
│   ├── deployment/                # Deployment automation
│   ├── data_collection/           # Data collection scripts
│   └── maintenance/               # System maintenance scripts
│
├── 🧪 tests/                       # Test suites
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   ├── e2e/                       # End-to-end tests
│   └── fixtures/                  # Test data fixtures
│
├── 📋 docs/                        # Documentation
│   ├── api/                       # API documentation
│   ├── deployment/                # Deployment guides
│   ├── user_guides/               # User documentation
│   └── technical/                 # Technical specifications
│
├── 🚢 deployment/                  # Deployment configuration
│   ├── docker/                    # Docker configurations
│   │   ├── Dockerfile.backend     # Backend container
│   │   ├── Dockerfile.frontend    # Frontend container
│   │   └── docker-compose.yml     # Multi-service orchestration
│   ├── kubernetes/                # Kubernetes manifests
│   ├── terraform/                 # Infrastructure as code
│   └── scripts/                   # Deployment scripts
│
├── 🔐 config/                      # Configuration files
│   ├── environments/              # Environment-specific configs
│   │   ├── development.env
│   │   ├── staging.env
│   │   └── production.env
│   ├── nginx/                     # Nginx configuration
│   └── ssl/                       # SSL certificates
│
└── 📄 root files                   # Project root files
    ├── README.md                  # Main project documentation
    ├── CHANGELOG.md               # Version history
    ├── LICENSE                    # Project license
    ├── .gitignore                 # Git ignore rules
    ├── .env.example               # Environment template
    ├── requirements.txt           # Python dependencies
    ├── package.json               # Node.js dependencies
    └── docker-compose.yml         # Development orchestration
```

## 🎯 Key Components

### Frontend (React + TypeScript)
- **Modern React**: Hooks, Context API, React Query
- **TypeScript**: Full type safety
- **Tailwind CSS**: Utility-first styling
- **Real-time**: WebSocket integration for live data
- **Charts**: TradingView charts integration

### Backend (Python + FastAPI)
- **FastAPI**: High-performance async API
- **WebSocket**: Real-time data streaming
- **AI/ML**: Scikit-learn, TensorFlow integration
- **Market Data**: Multi-exchange data feeds
- **Social Sentiment**: Reddit, Twitter analysis

### Trading Engine
- **Multi-Exchange**: Binance, Bybit, Coinbase support
- **Risk Management**: Position sizing, stop-losses
- **Backtesting**: Historical strategy validation
- **Live Trading**: Automated execution engine

### Infrastructure
- **Docker**: Containerized deployment
- **Kubernetes**: Scalable orchestration
- **Nginx**: Load balancing & SSL termination
- **PostgreSQL**: Primary database
- **Redis**: Caching & session storage

## 🚀 Quick Navigation

| Component | Location | Purpose |
|-----------|----------|---------|
| **API Endpoints** | `/backend/api/routers/` | REST API routes |
| **Trading Logic** | `/backend/core/` | Core trading algorithms |
| **AI Models** | `/backend/ai_models/` | ML prediction models |
| **Frontend UI** | `/frontend/src/components/` | React components |
| **Expert Advisors** | `/expert_advisors/` | MT4/MT5 trading bots |
| **Configuration** | `/config/` | Environment settings |
| **Documentation** | `/docs/` | Project documentation |

## 📈 Development Workflow

1. **Local Development**: Use `docker-compose.yml` for full stack
2. **Testing**: Run tests in `/tests/` directory
3. **Deployment**: Use `/deployment/` scripts and configs
4. **Monitoring**: Logs in `/data/logs/`, metrics via API
5. **Documentation**: Update `/docs/` for new features

## 🔄 Data Flow

```
Market Data → WebSocket → Backend Services → AI Models → Trading Signals → Frontend Dashboard
     ↓              ↓              ↓              ↓              ↓
Social Media → Sentiment Analysis → Risk Management → Order Execution → Notifications
```

This structure provides:
- **Separation of Concerns**: Clear boundaries between components
- **Scalability**: Easy to scale individual services
- **Maintainability**: Logical organization for development
- **Deployment Flexibility**: Multiple deployment options
- **Testing**: Comprehensive test coverage structure
