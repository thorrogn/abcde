<<<<<<< HEAD
# Disaster Management Information System

A comprehensive real-time disaster monitoring and information system that aggregates data from multiple sources including GDACS, ReliefWeb, and weather APIs to provide timely alerts and emergency information.

## 🌟 Features

- **Real-time Disaster Monitoring**: Live data from GDACS and ReliefWeb
- **Interactive Map**: Visual representation of disasters and alerts
- **Weather Integration**: Current weather conditions and alerts
- **Location-based Alerts**: Customizable location monitoring
- **Emergency Contacts**: Quick access to emergency services
- **News Feed**: Latest disaster-related news
- **Social Media Integration**: Real-time social media reports
- **API Monitoring**: System health and status monitoring

## 🏗️ Architecture

### Backend (Python Flask)
- **Flask API Server**: RESTful API with CORS support
- **Data Aggregation**: Combines data from multiple disaster sources
- **Background Processing**: Periodic data fetching and caching
- **Prometheus Metrics**: System monitoring and metrics
- **Weather Integration**: Ambee API for weather data

### Frontend (React TypeScript)
- **React 18**: Modern React with TypeScript
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality UI components
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. **Start the backend server:**
   \`\`\`bash
   chmod +x start_backend.sh
   ./start_backend.sh
   \`\`\`

   Or manually:
   \`\`\`bash
   cd Backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   \`\`\`

2. **Backend will be available at:**
   - API: `http://localhost:5000/api`
   - Health Check: `http://localhost:5000/api/health`
   - Metrics: `http://localhost:5000/metrics`

### Frontend Setup

1. **Start the frontend server:**
   \`\`\`bash
   chmod +x start_frontend.sh
   ./start_frontend.sh
   \`\`\`

   Or manually:
   \`\`\`bash
   cd Frontend
   npm install
   npm run dev
   \`\`\`

2. **Frontend will be available at:**
   - Application: `http://localhost:5173`

## 📡 API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `GET /api/status` - System status and data counts
- `GET /api/disasters` - Combined disaster data from all sources
- `GET /api/gdacs` - GDACS disaster alerts
- `GET /api/reliefweb` - ReliefWeb disaster data
- `GET /api/weather?lat={lat}&lng={lng}` - Weather data for coordinates

### Response Format
\`\`\`json
{
  "success": true,
  "data": [...],
  "count": 10,
  "last_updated": "2024-01-01T12:00:00Z"
}
\`\`\`

## 🔧 Configuration

### Backend Configuration

**GDACS Configuration** (`Backend/gdacs_config.yaml`):
\`\`\`yaml
gdacs_url: "https://www.gdacs.org/xml/rss.xml"
relevant_fields:
  - title
  - description
  - pubDate
  - link
  - alertlevel
  - country
  - coordinates
max_alerts_to_process: 20
\`\`\`

**ReliefWeb Configuration** (`Backend/reliefweb_config.yaml`):
\`\`\`yaml
api:
  scheme: "https"
  host: "api.reliefweb.int"
  path: "/v1/disasters"
  appname: "disaster-management-app"

query:
  limit: 20
  profile: "full"
  sort:
    - "date:desc"
  filters:
    status: "current"

output:
  fields:
    - name
    - description
    - date
    - country
    - type
\`\`\`

### Frontend Configuration

Update the API base URL in `Frontend/src/services/disasterApi.ts`:
\`\`\`typescript
const API_BASE_URL = 'http://localhost:5000/api';
\`\`\`

## 🌍 Data Sources

1. **GDACS (Global Disaster Alert and Coordination System)**
   - Real-time disaster alerts
   - Global coverage
   - Multiple disaster types

2. **ReliefWeb**
   - Humanitarian information
   - Disaster reports
   - Country-specific data

3. **Ambee Weather API**
   - Current weather conditions
   - Location-based weather data
   - Weather alerts

## 📊 Monitoring

### Prometheus Metrics
Access metrics at `http://localhost:5000/metrics`:
- HTTP request counts and latency
- Data source availability
- System health indicators

### System Status
Check system status at `http://localhost:5000/api/status`:
- Data source counts
- Last update timestamps
- Service availability

## 🛠️ Development

### Backend Development
\`\`\`bash
cd Backend
source venv/bin/activate
python app.py
\`\`\`

### Frontend Development
\`\`\`bash
cd Frontend
npm run dev
\`\`\`

### Building for Production
\`\`\`bash
# Frontend
cd Frontend
npm run build

# Backend (using gunicorn)
cd Backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
\`\`\`

## 🔒 Security Considerations

- API keys are stored in backend configuration
- CORS is enabled for development (configure for production)
- Rate limiting should be implemented for production use
- Environment variables should be used for sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API status at `/api/health`
- Review logs in the backend console
- Ensure all dependencies are installed
- Verify network connectivity for external APIs

## 🔄 Updates

The system automatically fetches new data:
- Disaster data: Every 5 minutes
- Weather data: Every 15 minutes
- Frontend refreshes: Every 5 minutes (configurable)
=======
# abcde
>>>>>>> 7624ba770223ceecbf2374933c04bf215756058d
