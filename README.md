# Vibration Analysis System for PHM (Prognostics and Health Management)

A comprehensive web-based application for vibration signal analysis and bearing health monitoring, specifically designed for the IEEE PHM 2012 Data Challenge and industrial prognostics applications.

## 🎯 Project Overview

This system provides an integrated platform for:
- **Vibration Signal Processing**: Advanced feature extraction from time, frequency, and wavelet domains
- **PHM Database Management**: Complete integration with IEEE PHM 2012 bearing dataset
- **Real-time Health Monitoring**: Dashboard for equipment health visualization and trending
- **Remaining Useful Life (RUL) Prediction**: Machine learning-based prognostics capabilities
- **Web-based Interface**: Modern Vue.js frontend with interactive charts and analysis tools

## 🏗️ System Architecture

### Backend (FastAPI + Python)
- **API Server**: `backend/main.py` - RESTful API with FastAPI framework
- **Signal Processing**: Legacy analysis modules for comprehensive feature extraction
- **Database**: SQLAlchemy ORM with SQLite for data persistence
- **PHM Integration**: Specialized processors for IEEE PHM 2012 dataset

### Frontend (Vue.js + Element Plus)
- **Dashboard**: Real-time health monitoring and statistics
- **PHM Database**: Browse and analyze IEEE PHM 2012 training data
- **Analysis Tools**: Interactive vibration analysis and RUL prediction
- **Frequency Calculator**: Specialized tools for bearing frequency analysis

### Core Analysis Modules
- `timedomain.py`: Time domain features (RMS, kurtosis, crest factor, etc.)
- `frequencydomain.py`: FFT analysis and spectral features
- `waveletprocess.py`: Wavelet transforms (STFT, CWT, NP4)
- `filterprocess.py`: Advanced filtering and higher-order statistics
- `hilbertransfer.py`: Hilbert transform and envelope analysis
- `harmonic_sildband_table.py`: Harmonic and sideband energy analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- UV package manager (recommended)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd vibration_signals
```

### 2. Start Backend
```bash
# Using UV (recommended)
uv run python run_backend.py

# Or using traditional Python
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Access Application
Open your browser and navigate to: `http://localhost:5173`

The backend API will be running on: `http://localhost:8000`

## 🐳 Docker Deployment

### Using Docker Compose
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d
```

### Individual Services
```bash
# Backend only
docker-compose up backend

# Frontend only
docker-compose up frontend
```

## 📊 IEEE PHM 2012 Integration

### Dataset Overview
- **Training Data**: 6 complete run-to-failure experiments
- **Test Data**: 11 truncated monitoring datasets
- **Sampling**: 25.6 kHz vibration, 0.1 Hz temperature
- **Sensors**: Dual accelerometers (horizontal/vertical), RTD temperature sensor

### Operating Conditions
| Condition | Speed (RPM) | Load (N) | Bearings |
|-----------|-------------|----------|----------|
| 1 | 1800 | 4000 | Bearing1_1, Bearing1_2 |
| 2 | 1650 | 4200 | Bearing2_1, Bearing2_2 |
| 3 | 1500 | 5000 | Bearing3_1, Bearing3_2 |

### Key Features
- **Real Degradation**: Natural bearing deterioration without artificial defects
- **Multiple Failure Modes**: Ball, inner race, outer race, and cage failures
- **High Variability**: Bearing lifetimes range from 1 to 7.47 hours
- **Challenge Scoring**: Asymmetric scoring function for early/late predictions

## 🔧 API Endpoints

### Health Monitoring
- `GET /` - System health check
- `GET /api/results` - Get analysis results
- `GET /api/health-trend/{guide_id}` - Get health trend data

### PHM Database
- `GET /api/phm/training-summary` - PHM training data summary
- `GET /api/phm/analysis-data` - PHM analysis results
- `POST /api/phm/analyze` - Analyze uploaded bearing data
- `POST /api/phm/predict-rul` - Predict remaining useful life

### Analysis
- `POST /api/analyze` - Perform vibration analysis
- `GET /api/guide-specs` - Get linear guide specifications
- `POST /api/guide-specs` - Create new guide specification

## 📁 Project Structure

```
vibration_signals/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API application
│   ├── models.py           # Database models
│   ├── phm_*.py           # PHM-specific processors
│   └── Dockerfile         # Backend container
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── views/         # Vue components
│   │   ├── stores/        # Pinia state management
│   │   └── router/        # Vue router
│   └── Dockerfile         # Frontend container
├── docs/                   # Documentation
├── phm_analysis_results/   # PHM analysis outputs
├── scripts/                # Utility scripts
├── *.py                   # Legacy analysis modules
├── docker-compose.yml     # Multi-service deployment
└── pyproject.toml         # Python dependencies
```

## 🧪 Testing and Development

### Backend Testing
```bash
# Run API tests
python test_timefrequency_api.py

# Test configuration
python backend/test_config.py
```

### Frontend Development
```bash
cd frontend
npm run dev    # Development server
npm run build  # Production build
npm run preview # Preview build
```

### Data Import
```bash
# Import PHM training data
python scripts/import_phm_data.py

# Query PHM database
python scripts/query_phm_data.py
```

## 📈 Analysis Workflow

1. **Data Upload**: Upload CSV files through web interface
2. **Preprocessing**: Automatic signal conditioning and validation
3. **Feature Extraction**: Multi-domain feature computation
4. **Health Assessment**: ML-based health score calculation
5. **RUL Prediction**: Prognostics algorithm application
6. **Visualization**: Interactive charts and trend analysis

## 🔍 Feature Extraction

### Time Domain Features
- Statistical moments (mean, std, skewness, kurtosis)
- Amplitude features (peak, RMS, crest factor)
- Energy-based indicators

### Frequency Domain Features
- FFT-based spectral analysis
- Characteristic frequency detection
- Frequency band energy ratios

### Advanced Features
- Wavelet coefficients and energy distribution
- Hilbert envelope analysis
- Higher-order spectral moments
- Harmonic and sideband energy tracking

## 🛠️ Configuration

### Environment Variables
```bash
DATABASE_URL=sqlite:///./vibration_analysis.db
VITE_API_URL=http://localhost:8000
```

### Backend Configuration
See `backend/CONFIG_README.md` for detailed configuration options.

## 📚 Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [PHM Integration Details](docs/PHM_INTEGRATION_README.md)
- [Project Summary](docs/PROJECT_SUMMARY.md)
- [Training Data Analysis](docs/TRAINING_DATA_ANALYSIS_REPORT.md)
- [Testing Guidelines](docs/TESTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Lin Hung Chuan** - Original analysis modules and algorithm development
- **Development Team** - System integration and web application

## 🙏 Acknowledgments

- IEEE PHM Society for the 2012 Data Challenge dataset
- FEMTO-ST Institute for the PRONOSTIA experimental platform
- Industrial partners for real-world validation datasets

## 📞 Support

For questions and support:
- Create an issue in the repository
- Check the documentation in the `docs/` directory
- Review existing discussions and solutions

---

**Note**: This system is designed for research and industrial applications. Ensure proper validation and testing before deployment in critical systems.