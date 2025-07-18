import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from modules.data_ingestion import DataIngestion
from modules.data_analysis import DataAnalysis
from modules.visualization import Visualization
from modules.database import DatabaseConnection
from modules.api_integration import APIIntegration
from modules.export import DataExport
from modules.insights import InsightGenerator
from utils.validators import DataValidator
from utils.helpers import format_bytes, get_data_summary

# Configure page
st.set_page_config(
    page_title="DevAnalytics - Data Analytics Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'current_view' not in st.session_state:
    st.session_state.current_view = "Data Import"

def main():
    st.title("📊 DevAnalytics - Data Analytics Tool")
    st.markdown("*Discover insights and trends in your data with integration capabilities*")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    view_options = [
        "Data Import",
        "Data Explorer",
        "Trend Analysis",
        "Visualizations",
        "Insights & Reports",
        "API Integration",
        "Export Data",
        "Documentation"
    ]
    
    selected_view = st.sidebar.selectbox("Select View", view_options, 
                                       index=view_options.index(st.session_state.current_view))
    st.session_state.current_view = selected_view
    
    # Data status in sidebar
    if st.session_state.data is not None:
        st.sidebar.success("✅ Data loaded successfully")
        st.sidebar.info(f"Shape: {st.session_state.data.shape}")
        st.sidebar.info(f"Size: {format_bytes(st.session_state.data.memory_usage(deep=True).sum())}")
    else:
        st.sidebar.warning("⚠️ No data loaded")
    
    # Main content based on selected view
    if selected_view == "Data Import":
        show_data_import()
    elif selected_view == "Data Explorer":
        show_data_explorer()
    elif selected_view == "Trend Analysis":
        show_trend_analysis()
    elif selected_view == "Visualizations":
        show_visualizations()
    elif selected_view == "Insights & Reports":
        show_insights_reports()
    elif selected_view == "API Integration":
        show_api_integration()
    elif selected_view == "Export Data":
        show_export_data()
    elif selected_view == "Documentation":
        show_documentation()

def show_data_import():
    st.header("📥 Data Import")
    
    # Data ingestion options
    data_ingestion = DataIngestion()
    
    tab1, tab2, tab3, tab4 = st.tabs(["CSV Upload", "Database Connection", "API Endpoint", "JSON Upload"])
    
    with tab1:
        st.subheader("Upload CSV File")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                data = data_ingestion.load_csv(uploaded_file)
                st.session_state.data = data
                st.success("✅ CSV file loaded successfully!")
                st.write("**Data Preview:**")
                st.dataframe(data.head())
                st.write("**Data Summary:**")
                st.write(get_data_summary(data))
            except Exception as e:
                st.error(f"❌ Error loading CSV: {str(e)}")
    
    with tab2:
        st.subheader("Database Connection")
        db_type = st.selectbox("Database Type", ["PostgreSQL", "MySQL", "SQLite"])
        
        if db_type == "PostgreSQL":
            # Use environment variables for PostgreSQL connection
            if st.button("Connect to PostgreSQL"):
                try:
                    db_conn = DatabaseConnection()
                    conn = db_conn.connect_postgresql()
                    st.success("✅ Connected to PostgreSQL database")
                    
                    # Show available tables
                    tables = db_conn.get_tables(conn)
                    if tables:
                        selected_table = st.selectbox("Select Table", tables)
                        if st.button("Load Table"):
                            data = db_conn.load_table(conn, selected_table)
                            st.session_state.data = data
                            st.success(f"✅ Table '{selected_table}' loaded successfully!")
                            st.dataframe(data.head())
                    else:
                        st.info("No tables found in the database")
                except Exception as e:
                    st.error(f"❌ Database connection failed: {str(e)}")
        
        elif db_type == "SQLite":
            sqlite_file = st.file_uploader("Upload SQLite file", type="db")
            if sqlite_file:
                try:
                    db_conn = DatabaseConnection()
                    conn = db_conn.connect_sqlite(sqlite_file)
                    st.success("✅ Connected to SQLite database")
                    
                    tables = db_conn.get_tables(conn)
                    if tables:
                        selected_table = st.selectbox("Select Table", tables)
                        if st.button("Load Table"):
                            data = db_conn.load_table(conn, selected_table)
                            st.session_state.data = data
                            st.success(f"✅ Table '{selected_table}' loaded successfully!")
                            st.dataframe(data.head())
                except Exception as e:
                    st.error(f"❌ SQLite connection failed: {str(e)}")
    
    with tab3:
        st.subheader("API Endpoint")
        api_url = st.text_input("API URL")
        api_key = st.text_input("API Key (optional)", type="password")
        
        if st.button("Fetch Data from API"):
            if api_url:
                try:
                    api_integration = APIIntegration()
                    data = api_integration.fetch_from_api(api_url, api_key)
                    st.session_state.data = data
                    st.success("✅ Data fetched from API successfully!")
                    st.dataframe(data.head())
                except Exception as e:
                    st.error(f"❌ API fetch failed: {str(e)}")
            else:
                st.error("Please enter an API URL")
    
    with tab4:
        st.subheader("Upload JSON File")
        json_file = st.file_uploader("Choose a JSON file", type="json")
        
        if json_file is not None:
            try:
                data = data_ingestion.load_json(json_file)
                st.session_state.data = data
                st.success("✅ JSON file loaded successfully!")
                st.dataframe(data.head())
            except Exception as e:
                st.error(f"❌ Error loading JSON: {str(e)}")

def show_data_explorer():
    st.header("🔍 Data Explorer")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please load data first from the Data Import section")
        return
    
    data = st.session_state.data
    
    # Data overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", data.shape[0])
    with col2:
        st.metric("Columns", data.shape[1])
    with col3:
        st.metric("Memory Usage", format_bytes(data.memory_usage(deep=True).sum()))
    with col4:
        st.metric("Missing Values", data.isnull().sum().sum())
    
    # Data filtering and querying
    st.subheader("🔧 Data Filtering")
    
    # Column selection
    selected_columns = st.multiselect("Select Columns", data.columns.tolist(), default=data.columns.tolist())
    
    if selected_columns:
        filtered_data = data[selected_columns]
        
        # Numeric column filtering
        numeric_columns = filtered_data.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_columns:
            st.write("**Numeric Filters:**")
            for col in numeric_columns:
                col_min, col_max = float(filtered_data[col].min()), float(filtered_data[col].max())
                range_values = st.slider(f"{col} Range", col_min, col_max, (col_min, col_max))
                filtered_data = filtered_data[(filtered_data[col] >= range_values[0]) & 
                                            (filtered_data[col] <= range_values[1])]
        
        # Text column filtering
        text_columns = filtered_data.select_dtypes(include=['object']).columns.tolist()
        if text_columns:
            st.write("**Text Filters:**")
            for col in text_columns:
                unique_values = filtered_data[col].unique()
                if len(unique_values) <= 50:  # Show multiselect for categorical data
                    selected_values = st.multiselect(f"{col} Values", unique_values, default=unique_values)
                    filtered_data = filtered_data[filtered_data[col].isin(selected_values)]
                else:  # Show text input for free text
                    search_term = st.text_input(f"Search in {col}")
                    if search_term:
                        filtered_data = filtered_data[filtered_data[col].str.contains(search_term, case=False, na=False)]
        
        # Display filtered data
        st.subheader("📊 Filtered Data")
        st.dataframe(filtered_data)
        
        # Data quality checks
        st.subheader("✅ Data Quality Checks")
        validator = DataValidator()
        quality_report = validator.validate_data(filtered_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Missing Values:**")
            missing_data = filtered_data.isnull().sum()
            st.bar_chart(missing_data[missing_data > 0])
        
        with col2:
            st.write("**Data Types:**")
            dtype_counts = filtered_data.dtypes.value_counts()
            st.bar_chart(dtype_counts)

def show_trend_analysis():
    st.header("📈 Trend Analysis")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please load data first from the Data Import section")
        return
    
    data = st.session_state.data
    data_analysis = DataAnalysis()
    
    # Time series analysis
    st.subheader("⏱️ Time Series Analysis")
    
    # Detect potential date columns
    date_columns = data_analysis.detect_date_columns(data)
    
    if date_columns:
        selected_date_col = st.selectbox("Select Date Column", date_columns)
        numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_columns:
            selected_metric = st.selectbox("Select Metric", numeric_columns)
            
            # Perform time series analysis
            try:
                time_series_data = data_analysis.prepare_time_series(data, selected_date_col, selected_metric)
                
                # Calculate trends
                trends = data_analysis.calculate_trends(time_series_data)
                
                # Display trend metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Trend Direction", trends['direction'])
                with col2:
                    st.metric("Slope", f"{trends['slope']:.4f}")
                with col3:
                    st.metric("R-squared", f"{trends['r_squared']:.4f}")
                
                # Time series visualization
                fig = px.line(time_series_data, x=selected_date_col, y=selected_metric, 
                            title=f"Time Series: {selected_metric}")
                st.plotly_chart(fig, use_container_width=True)
                
                # Seasonal decomposition if applicable
                if len(time_series_data) > 24:  # Need sufficient data points
                    st.subheader("📊 Seasonal Decomposition")
                    decomposition = data_analysis.seasonal_decomposition(time_series_data, selected_metric)
                    if decomposition:
                        st.plotly_chart(decomposition, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Time series analysis failed: {str(e)}")
    else:
        st.info("No date columns detected in the data")
    
    # Statistical analysis
    st.subheader("📊 Statistical Analysis")
    
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_columns:
        selected_cols = st.multiselect("Select Columns for Analysis", numeric_columns, default=numeric_columns[:3])
        
        if selected_cols:
            # Correlation analysis
            correlation_matrix = data_analysis.calculate_correlation(data[selected_cols])
            
            st.write("**Correlation Matrix:**")
            fig = px.imshow(correlation_matrix, text_auto=True, aspect="auto",
                          title="Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True)
            
            # Distribution analysis
            st.write("**Distribution Analysis:**")
            for col in selected_cols:
                fig = px.histogram(data, x=col, title=f"Distribution of {col}")
                st.plotly_chart(fig, use_container_width=True)

def show_visualizations():
    st.header("📊 Visualizations")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please load data first from the Data Import section")
        return
    
    data = st.session_state.data
    viz = Visualization()
    
    # Chart type selection
    chart_type = st.selectbox("Select Chart Type", [
        "Line Chart", "Bar Chart", "Scatter Plot", "Histogram", 
        "Box Plot", "Heatmap", "Pie Chart", "Area Chart"
    ])
    
    # Column selection based on chart type
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = data.select_dtypes(include=['object']).columns.tolist()
    
    if chart_type == "Line Chart":
        x_col = st.selectbox("X-axis", data.columns)
        y_col = st.selectbox("Y-axis", numeric_columns)
        color_col = st.selectbox("Color by (optional)", [None] + categorical_columns)
        
        fig = viz.create_line_chart(data, x_col, y_col, color_col)
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Bar Chart":
        x_col = st.selectbox("X-axis", data.columns)
        y_col = st.selectbox("Y-axis", numeric_columns)
        color_col = st.selectbox("Color by (optional)", [None] + categorical_columns)
        
        fig = viz.create_bar_chart(data, x_col, y_col, color_col)
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Scatter Plot":
        x_col = st.selectbox("X-axis", numeric_columns)
        y_col = st.selectbox("Y-axis", numeric_columns)
        color_col = st.selectbox("Color by (optional)", [None] + categorical_columns)
        size_col = st.selectbox("Size by (optional)", [None] + numeric_columns)
        
        fig = viz.create_scatter_plot(data, x_col, y_col, color_col, size_col)
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Histogram":
        x_col = st.selectbox("Column", numeric_columns)
        bins = st.slider("Number of bins", 10, 100, 30)
        
        fig = viz.create_histogram(data, x_col, bins)
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Box Plot":
        y_col = st.selectbox("Y-axis", numeric_columns)
        x_col = st.selectbox("X-axis (optional)", [None] + categorical_columns)
        
        fig = viz.create_box_plot(data, y_col, x_col)
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Heatmap":
        if len(numeric_columns) > 1:
            selected_cols = st.multiselect("Select Columns", numeric_columns, default=numeric_columns)
            fig = viz.create_heatmap(data[selected_cols])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Need at least 2 numeric columns for heatmap")
    
    elif chart_type == "Pie Chart":
        if categorical_columns:
            col = st.selectbox("Column", categorical_columns)
            fig = viz.create_pie_chart(data, col)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Need categorical columns for pie chart")
    
    elif chart_type == "Area Chart":
        x_col = st.selectbox("X-axis", data.columns)
        y_col = st.selectbox("Y-axis", numeric_columns)
        
        fig = viz.create_area_chart(data, x_col, y_col)
        st.plotly_chart(fig, use_container_width=True)

def show_insights_reports():
    st.header("💡 Insights & Reports")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please load data first from the Data Import section")
        return
    
    data = st.session_state.data
    insight_generator = InsightGenerator()
    
    # Generate automated insights
    st.subheader("🤖 Automated Insights")
    
    if st.button("Generate Insights"):
        with st.spinner("Generating insights..."):
            insights = insight_generator.generate_insights(data)
            st.session_state.analysis_results = insights
    
    if st.session_state.analysis_results:
        insights = st.session_state.analysis_results
        
        # Display key statistics
        st.subheader("📊 Key Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", insights['basic_stats']['total_records'])
        with col2:
            st.metric("Numeric Columns", insights['basic_stats']['numeric_columns'])
        with col3:
            st.metric("Categorical Columns", insights['basic_stats']['categorical_columns'])
        
        # Data quality insights
        st.subheader("✅ Data Quality Insights")
        quality_insights = insights['quality_insights']
        
        if quality_insights['missing_data']:
            st.warning("⚠️ Missing Data Detected")
            missing_df = pd.DataFrame(list(quality_insights['missing_data'].items()), 
                                    columns=['Column', 'Missing Count'])
            st.dataframe(missing_df)
        
        if quality_insights['duplicates'] > 0:
            st.warning(f"⚠️ {quality_insights['duplicates']} duplicate records found")
        
        # Statistical insights
        st.subheader("📈 Statistical Insights")
        if insights['statistical_insights']:
            for insight in insights['statistical_insights']:
                st.info(insight)
        
        # Correlation insights
        st.subheader("🔗 Correlation Insights")
        if insights['correlation_insights']:
            for insight in insights['correlation_insights']:
                st.info(insight)
        
        # Trend insights
        st.subheader("📊 Trend Insights")
        if insights['trend_insights']:
            for insight in insights['trend_insights']:
                st.info(insight)
        
        # Outlier detection
        st.subheader("🎯 Outlier Detection")
        if insights['outlier_insights']:
            for column, outlier_count in insights['outlier_insights'].items():
                if outlier_count > 0:
                    st.warning(f"⚠️ {outlier_count} outliers detected in {column}")

def show_api_integration():
    st.header("🔌 API Integration")
    
    # API documentation
    st.subheader("📚 API Documentation")
    
    st.markdown("""
    ### Data API Endpoints
    
    **Base URL:** `http://localhost:8000/api`
    
    #### Available Endpoints:
    
    - `GET /data/summary` - Get data summary statistics
    - `POST /data/query` - Query data with filters
    - `GET /data/export/{format}` - Export data in specified format
    - `POST /data/insights` - Generate insights for data
    
    #### Example Usage:
    """)
    
    # Code snippets for integration
    st.code("""
# Python example
import requests

# Get data summary
response = requests.get('http://localhost:8000/api/data/summary')
summary = response.json()

# Query data with filters
query_data = {
    "columns": ["column1", "column2"],
    "filters": {
        "column1": {"min": 0, "max": 100}
    }
}
response = requests.post('http://localhost:8000/api/data/query', json=query_data)
filtered_data = response.json()
""", language='python')
    
    st.code("""
// JavaScript example
// Get data summary
fetch('http://localhost:8000/api/data/summary')
  .then(response => response.json())
  .then(data => console.log(data));

// Query data with filters
const queryData = {
  columns: ['column1', 'column2'],
  filters: {
    column1: { min: 0, max: 100 }
  }
};

fetch('http://localhost:8000/api/data/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(queryData)
})
.then(response => response.json())
.then(data => console.log(data));
""", language='javascript')
    
    # API testing interface
    st.subheader("🧪 API Testing Interface")
    
    if st.session_state.data is not None:
        endpoint = st.selectbox("Select Endpoint", [
            "/data/summary",
            "/data/query",
            "/data/export/csv",
            "/data/export/json",
            "/data/insights"
        ])
        
        if endpoint == "/data/summary":
            if st.button("Test Summary Endpoint"):
                from api.data_api import get_data_summary_api
                try:
                    result = get_data_summary_api(st.session_state.data)
                    st.json(result)
                except Exception as e:
                    st.error(f"API Error: {str(e)}")
        
        elif endpoint == "/data/query":
            st.write("**Query Parameters:**")
            available_columns = st.session_state.data.columns.tolist()
            selected_columns = st.multiselect("Columns", available_columns)
            
            if st.button("Test Query Endpoint"):
                from api.data_api import query_data_api
                try:
                    query_params = {"columns": selected_columns}
                    result = query_data_api(st.session_state.data, query_params)
                    st.json(result)
                except Exception as e:
                    st.error(f"API Error: {str(e)}")
        
        elif endpoint in ["/data/export/csv", "/data/export/json"]:
            format_type = endpoint.split('/')[-1]
            if st.button(f"Test Export {format_type.upper()} Endpoint"):
                from api.data_api import export_data_api
                try:
                    result = export_data_api(st.session_state.data, format_type)
                    st.success(f"Export successful! Data size: {len(result)} characters")
                    st.text_area("Export Result (first 1000 chars)", result[:1000])
                except Exception as e:
                    st.error(f"API Error: {str(e)}")
    else:
        st.info("Load data first to test API endpoints")

def show_export_data():
    st.header("📤 Export Data")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please load data first from the Data Import section")
        return
    
    data = st.session_state.data
    exporter = DataExport()
    
    # Export options
    st.subheader("📁 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
        
        # Column selection
        selected_columns = st.multiselect("Select Columns", data.columns.tolist(), 
                                        default=data.columns.tolist())
    
    with col2:
        # Row filtering
        max_rows = st.number_input("Max Rows (0 for all)", min_value=0, value=0)
        
        # Include index
        include_index = st.checkbox("Include Index", value=False)
    
    # Data preview
    export_data = data[selected_columns] if selected_columns else data
    if max_rows > 0:
        export_data = export_data.head(max_rows)
    
    st.subheader("👀 Export Preview")
    st.dataframe(export_data.head())
    
    # Export buttons
    st.subheader("⬇️ Download")
    
    if export_format == "CSV":
        csv_data = exporter.to_csv(export_data, include_index)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="exported_data.csv",
            mime="text/csv"
        )
    
    elif export_format == "JSON":
        json_data = exporter.to_json(export_data)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name="exported_data.json",
            mime="application/json"
        )
    
    elif export_format == "Excel":
        excel_data = exporter.to_excel(export_data, include_index)
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name="exported_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def show_documentation():
    st.header("📖 Documentation")
    
    st.markdown("""
    ## Welcome to DevAnalytics
    
    DevAnalytics is a comprehensive data analytics tool designed for developers and technical teams to discover insights and trends in their data.
    
    ### Features
    
    #### 🔧 Data Integration
    - **CSV Upload**: Upload CSV files directly through the web interface
    - **Database Connections**: Connect to PostgreSQL, MySQL, and SQLite databases
    - **API Integration**: Fetch data from REST APIs with authentication support
    - **JSON Support**: Import JSON data files
    
    #### 📊 Data Analysis
    - **Interactive Exploration**: Filter and query data with intuitive controls
    - **Statistical Analysis**: Correlation analysis, distribution analysis, and trend detection
    - **Time Series Analysis**: Trend calculation and seasonal decomposition
    - **Data Quality Checks**: Missing value detection, duplicate identification
    
    #### 📈 Visualizations
    - **Multiple Chart Types**: Line, bar, scatter, histogram, box plot, heatmap, pie, area
    - **Interactive Charts**: Zoom, pan, hover tooltips powered by Plotly
    - **Customizable**: Select columns, colors, and grouping options
    
    #### 🤖 Automated Insights
    - **Statistical Insights**: Automatic detection of interesting patterns
    - **Correlation Analysis**: Identify relationships between variables
    - **Outlier Detection**: Spot anomalies in your data
    - **Trend Analysis**: Understand data patterns over time
    
    #### 🔌 API Access
    - **RESTful API**: Programmatic access to all functionality
    - **Multiple Formats**: Export data in CSV, JSON, and Excel formats
    - **Code Examples**: Python and JavaScript integration examples
    
    ### Getting Started
    
    1. **Import Data**: Start by uploading a CSV file or connecting to a database
    2. **Explore**: Use the Data Explorer to understand your data structure
    3. **Analyze**: Generate insights and perform trend analysis
    4. **Visualize**: Create charts and graphs to communicate findings
    5. **Export**: Save your results in various formats
    
    ### API Usage
    
    The tool provides a RESTful API for programmatic access. See the API Integration section for detailed examples and endpoints.
    
    ### Data Privacy
    
    All data processing happens locally within your environment. No data is transmitted to external servers.
    
    ### Support
    
    For technical support and feature requests, please refer to the project documentation.
    """)

if __name__ == "__main__":
    main()
