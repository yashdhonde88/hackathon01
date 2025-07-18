# JourneyConnect - Hackathon Travel Platform

## Overview

JourneyConnect is a full-stack hackathon website that unifies three essential travel and exploration services: Smart Carpooling, Travel Buddy Finder, and Local History Explorer. Built with Node.js/Express backend and vanilla JavaScript frontend, this platform connects users for shared rides, travel companions, and local historical discoveries.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Vanilla HTML5, CSS3, and JavaScript
- **UI/UX**: Modern, responsive design with smooth scroll animations using Lenis
- **Authentication**: JWT token-based authentication with localStorage persistence
- **Navigation**: Single-page application with dynamic content switching
- **Styling**: CSS Grid and Flexbox for responsive layouts, custom animations

### Backend Architecture
- **Framework**: Node.js with Express.js server
- **API Design**: RESTful API with proper HTTP status codes and error handling
- **Security**: Helmet for security headers, rate limiting, CORS enabled
- **Authentication**: JWT tokens with bcrypt password hashing
- **Database**: SQLite for local development with prepared statements

### Data Storage Solutions
- **Database**: SQLite database with four main tables (users, carpool_rides, travel_plans, historical_sites)
- **Schema**: Properly normalized database schema with foreign key relationships
- **Security**: SQL injection prevention through prepared statements
- **Sample Data**: Pre-populated historical sites for demonstration

## Key Components

### Data Ingestion Module (`modules/data_ingestion.py`)
- **Purpose**: Handle data import from various file formats
- **Supported Formats**: CSV, JSON, Excel, Parquet
- **Features**: File validation, error handling, and format conversion

### Data Analysis Module (`modules/data_analysis.py`)
- **Purpose**: Advanced statistical analysis and data processing
- **Features**: Time series analysis, correlation analysis, PCA, statistical tests
- **Dependencies**: SciPy, statsmodels, scikit-learn

### Visualization Module (`modules/visualization.py`)
- **Purpose**: Create interactive visualizations
- **Library**: Plotly for interactive charts
- **Chart Types**: Line charts, bar charts, scatter plots, histograms, heatmaps

### Database Module (`modules/database.py`)
- **Purpose**: Database connectivity and operations
- **Supported Databases**: PostgreSQL, MySQL, SQLite
- **Features**: Connection pooling, query execution, environment variable support

### API Integration Module (`modules/api_integration.py`)
- **Purpose**: External API data fetching and integration
- **Features**: REST API support, retry mechanisms, authentication handling
- **HTTP Client**: Requests library with retry strategy

### Export Module (`modules/export.py`)
- **Purpose**: Data export in multiple formats
- **Supported Formats**: CSV, JSON, Excel, Parquet, HTML
- **Features**: Customizable export options, formatting controls

### Insights Module (`modules/insights.py`)
- **Purpose**: Automated insight generation and pattern detection
- **Features**: Statistical insights, correlation analysis, outlier detection, trend analysis

## Data Flow

1. **Data Import**: Users upload files or connect to databases through the Data Ingestion module
2. **Data Validation**: Data quality checks performed using the DataValidator utility
3. **Data Processing**: Raw data is processed and analyzed using the Data Analysis module
4. **Visualization**: Processed data is visualized using the Visualization module
5. **Insights Generation**: Automated insights are generated using the Insights module
6. **Export**: Results can be exported in various formats using the Export module

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Plotly**: Interactive visualization library

### Statistical and ML Libraries
- **SciPy**: Scientific computing
- **Statsmodels**: Statistical modeling
- **Scikit-learn**: Machine learning tools

### Database Libraries
- **SQLAlchemy**: SQL toolkit and ORM
- **psycopg2**: PostgreSQL adapter (implied)
- **PyMySQL**: MySQL adapter (implied)

### API and Web Libraries
- **Requests**: HTTP library for API calls
- **urllib3**: HTTP client library

### Export Libraries
- **xlsxwriter**: Excel file creation
- **openpyxl**: Excel file handling (implied)

## Deployment Strategy

### Development Environment
- **Local Development**: Streamlit development server
- **Configuration**: Environment variables for database connections
- **Dependencies**: Requirements managed through pip/conda

### Production Considerations
- **Database Configuration**: Environment variable based configuration for database connections
- **Security**: API key management and secure credential storage
- **Scalability**: Modular architecture allows for easy scaling of individual components
- **Error Handling**: Comprehensive error handling across all modules

### Environment Variables
- `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGPORT`: PostgreSQL connection parameters
- Database credentials should be stored as environment variables for security

### File Structure
- Modular design with separate modules for different functionalities
- Utility functions separated into `utils/` directory
- API endpoints organized in `api/` directory
- Configuration managed through Streamlit's built-in configuration system