#Creating a Streamlit App with Filters

import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
import numpy as np


# Function to connect to SQLite database
def get_data(query, params=None):
    conn = mysql.connector.connect(
          host="localhost",
          user="root",
          password="hopePraise8gt",
          database = "guvi_db"
    )
    
    if params:
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Streamlit App Title
st.set_page_config(page_title="Traffic Violations Insight System", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Project Introduction", "Traffic Violation - Filter/Search","Heatmap View",'View summary statistics', "EDA Report","Univariate","Bivariate","Multivariate", "Creator Info"])

# -------------------------------- PAGE 1: Introduction --------------------------------
if page == "Project Introduction":
    st.title("🌦️ Traffic Violation Analysis")
    st.subheader("📊 A Streamlit App for Exploring growing Traffic Trends")
    st.write("""
    This project analyzes weather data from different cities using MySQL database.
    It provides visualizations for various parameters.
    
    **Features:**
    - View and filter Traffic by city, date, or month.
    - Illustrates about various traffic violations
    - Generate dynamic visualizations.
    - Run predefined SQL queries to explore insights.
    
    **Database Used:** `guvi_db.mysql`
    """)

# ---------- PAGE 2: Traffic Data Visualization ----------

elif page == "Traffic Violations Visualization":
    st.title("Traffic Violations Visualization")
    
    violations_df = get_data("SELECT DISTINCT `Violation Type` FROM guvi_db.Traffic_Violations")
    
    if violations_df.empty:
        st.error("No violation types found. Check if table `guvi_db.Traffic_Violations` has data.")
        st.stop()
    
    selected_violation = st.selectbox("Select Violation Type", violations_df['Violation Type'].tolist(), key="violation_select")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", key="start_date")
    with col2:
        end_date = st.date_input("End Date", key="end_date")
    
    query = """
        SELECT `Date of Stop`, `Violation Type`, COUNT(*) as violation_count
        FROM guvi_db.Traffic_Violations
        WHERE `Violation Type` = %s 
        AND DATE(`Date of Stop`) >= %s 
        AND DATE(`Date of Stop`) <= %s
        GROUP BY `Date of Stop`, `Violation Type`
        ORDER BY violation_count DESC
        LIMIT 1000000
    """
    
    df = get_data(query, (selected_violation, str(start_date), str(end_date)))
    
    st.write(f"Rows found: {len(df)}")
    
    if not df.empty:
        st.write("### Traffic Violation Data")
        st.dataframe(df, width='stretch')
        
        fig, ax = plt.subplots(figsize=(12,5))
        sns.barplot(data=df, x='Date of Stop', y='violation_count', ax=ax)
        plt.xticks(rotation=45)
        plt.title(f"Violations for {selected_violation}")
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("No data available for selected filters.")

# ---------- PAGE 2: Traffic Violation - Filter/Search ----------
elif page == "Traffic Violation - Filter/Search":
    st.title("Traffic Violation - Filter/Search")
    
    # 1. Fetch all filter options first - keep this at top
    violations_df = get_data("SELECT DISTINCT `Violation Type` FROM guvi_db.Traffic_Violations")
    vehicle_types_df = get_data("SELECT DISTINCT `VehicleType` FROM guvi_db.Traffic_Violations")
    Race_df = get_data("SELECT DISTINCT `Race` FROM guvi_db.Traffic_Violations")
    Gender_df = get_data("SELECT DISTINCT `Gender` FROM guvi_db.Traffic_Violations")
    Geolocation_df = get_data("SELECT DISTINCT `Geolocation` FROM guvi_db.Traffic_Violations WHERE Geolocation not in ('(0.0, 0.0)')")
    date_range = get_data("SELECT MIN(DATE(`Date of Stop`)) as min_d, MAX(DATE(`Date of Stop`)) as max_d FROM guvi_db.Traffic_Violations")
    
    # 2. PUT ALL FILTERS IN SIDEBAR 
    with st.sidebar:
        st.header("🔍 Filters")
        
        violations = ["All"] + violations_df['Violation Type'].tolist()
        selected_violation = st.selectbox("Violation Type", violations, key="v")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date_range['min_d'][0], key="s")
        with col2:
            end_date = st.date_input("End Date", value=date_range['max_d'][0], key="e")
        
        vehicles = ["All"] + vehicle_types_df['VehicleType'].tolist()
        selected_vehicle = st.selectbox("Vehicle Type", vehicles, key="veh")
        
        races = ["All"] + Race_df['Race'].tolist()
        selected_Race = st.selectbox("Race", races, key="r")
        
        genders = ["All"] + Gender_df['Gender'].tolist()
        selected_Gender = st.selectbox("Gender", genders, key="g")
        
        geos = ["All"] + Geolocation_df['Geolocation'].tolist()
        selected_Geolocation = st.selectbox("Geolocation", geos, key="geo")
    
    # 3. Build dynamic query - keep this in main area
    query = """
        SELECT `Date of Stop`, `Violation Type`, `VehicleType`, `Race`, `Gender`, `Geolocation`
        FROM guvi_db.Traffic_Violations
        WHERE 1=1
    """
    params = []
    
    if selected_violation!= "All":
        query += " AND `Violation Type` = %s"
        params.append(selected_violation)
    
    query += " AND DATE(`Date of Stop`) BETWEEN %s AND %s"
    params.extend([str(start_date), str(end_date)])
    
    if selected_vehicle!= "All":
        query += " AND `VehicleType` = %s"
        params.append(selected_vehicle)
    
    if selected_Race!= "All":
        query += " AND `Race` = %s"
        params.append(selected_Race)
    
    if selected_Gender!= "All":
        query += " AND `Gender` = %s"
        params.append(selected_Gender)
    
    if selected_Geolocation!= "All":
        query += " AND `Geolocation` = %s"
        params.append(selected_Geolocation)
    
    query += " LIMIT 10000"
    
    # 4. Show results in main area - more space now
    df = get_data(query, tuple(params))
    if not df.empty:
        st.write(f"Rows found: {len(df)}")
        st.dataframe(df, width="stretch", height=500)
    else:
        st.warning("No data available for selected filters.")


# ---------- PAGE 2: Filter violations ----------

elif page == "Filter violations":
    st.title("Filter violations")

   #Violation Type 
    violations_df = get_data("SELECT DISTINCT `Violation Type` FROM guvi_db.Traffic_Violations")
    if violations_df.empty:
        st.error("No violation types found. Check if table `guvi_db.Traffic_Violations` has data.")
        st.stop()
    selected_violation = st.selectbox("Select Violation Type", violations_df['Violation Type'].tolist(), key="violation_select")
    
    
    #col1, col2 = st.columns(2)
    #with col1:
    #    start_date = st.date_input("Start Date", key="start_date")
    #with col2:
    #    end_date = st.date_input("End Date", key="end_date")
   
    # Fetch Start and End Date
    date_range = get_data("SELECT MIN(DATE(`Date of Stop`)) as min_d, MAX(DATE(`Date of Stop`)) as max_d FROM guvi_db.Traffic_Violations")
    start_date = st.date_input("Start Date", value=date_range['min_d'][0], key="start_date")
    end_date = st.date_input("End Date", value=date_range['max_d'][0], key="end_date")

    #VehicleType = get_data("SELECT DISTINCT `VehicleType` FROM guvi_db.Traffic_Violations")

    #Vehicle Type
    vehicle_types_df = get_data("SELECT DISTINCT `VehicleType` FROM guvi_db.Traffic_Violations")
    if vehicle_types_df.empty:
        st.error("No vehicle types found.")
        st.stop()
    #selected_vehicle = st.selectbox("Select Vehicle Type", vehicle_types_df['VehicleType'].tolist(), key="vehicle_select")

    vehicle_types = ["All"] + vehicle_types_df['VehicleType'].tolist()
    selected_vehicle = st.selectbox("Select Vehicle Type", vehicle_types, key="vehicle_select")

    #Race
    Race_df = get_data("SELECT DISTINCT `Race` FROM guvi_db.Traffic_Violations")
    if Race_df.empty:
        st.error("No Race found.")
        st.stop()
    #selected_Race = st.selectbox("Select Race", Race_df['Race'].tolist(), key="Race_select")
    races = ["All"] + Race_df['Race'].tolist()
    selected_Race = st.selectbox("Select Race", races, key="Race_select")

   #Gender
    Gender_df = get_data("SELECT DISTINCT `Gender` FROM guvi_db.Traffic_Violations")
    if Gender_df.empty:
        st.error("No Gender found.")
        st.stop()
    #selected_Gender = st.selectbox("Select Gender", Gender_df['Gender'].tolist(), key="Gender_select")
    genders = ["All"] + Gender_df['Gender'].tolist()
    selected_Gender = st.selectbox("Select Gender", genders, key="Gender_select")

    #Geolocation
    Geolocation_df = get_data("SELECT DISTINCT `Geolocation` FROM guvi_db.Traffic_Violations where Geolocation not in ('(0.0, 0.0)')")
    if Geolocation_df.empty:
        st.error("No Geolocation found.")
        st.stop()
    #selected_Geolocation = st.selectbox("Select Geolocation", Geolocation_df['Geolocation'].tolist(), key="Geolocation_select")
    geos = ["All"] + Geolocation_df['Geolocation'].tolist()
    selected_Geolocation = st.selectbox("Select Geolocation", geos, key="Geolocation_select")

    query = """
        SELECT `Date of Stop`, `Violation Type`, `vehicletype`,`Race`,`Gender`,`Geolocation`
        FROM guvi_db.Traffic_Violations
        WHERE `Violation Type` = %s 
        AND DATE(`Date of Stop`) BETWEEN %s AND %s 
    """
    params = [selected_violation, str(start_date), str(end_date)]

    if selected_vehicle!= "All":
        query += " AND `VehicleType` = %s"
        params.append(selected_vehicle)

    if selected_Race!= "All":
        query += " AND `Race` = %s"
        params.append(selected_Race)

    if selected_Gender!= "All":
        query += " AND `Gender` = %s"
        params.append(selected_Gender)

    if selected_Geolocation!= "All":
        query += " AND `Geolocation` = %s"
        params.append(selected_Geolocation)

    query += " LIMIT 10000"

    df = get_data(query, tuple(params))

    #df = get_data(query, (selected_violation, str(start_date), str(end_date), selected_vehicle , selected_Race, selected_Gender, selected_Geolocation))
    if not df.empty:
    
        st.write(f"Rows found: {len(df)}")
        st.write("### Traffic Violation Data")
        st.dataframe(df, width='stretch')
    else:
        st.warning("No data available for selected filters.")


# ---------- PAGE 3: Geo-Heatmap View ----------

elif page == "Heatmap View":
    st.title("🗺️ Geographical Heatmap of Incident Hotspots")
    
    @st.cache_data
    def load_geo_data():
        query = """
        SELECT `Date of Stop`, `Violation Type`, `VehicleType`, `Race`, `Gender`, `Geolocation`
        FROM guvi_db.Traffic_Violations
        WHERE Geolocation IS NOT NULL 
        AND Geolocation!= '(0.0, 0.0)'
        AND Geolocation LIKE '(%, %)'
        """
        df = get_data(query)
        
        # Split to latitude + longitude
        coords = df['Geolocation'].str.strip('()').str.split(',', n=1, expand=True)
        coords.columns = ['latitude', 'longitude']
        df['latitude'] = pd.to_numeric(coords['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(coords['longitude'], errors='coerce')
        df['Date of Stop'] = pd.to_datetime(df['Date of Stop'])
        
        return df.dropna(subset=['latitude', 'longitude'])
    
    df = load_geo_data()
    
    if df.empty:
        st.warning("No geolocation data available")
        st.stop()
    
    min_date = df['Date of Stop'].min().date()
    max_date = df['Date of Stop'].max().date()
    
    # ALL FILTERS IN SIDEBAR
    with st.sidebar:
        st.header("🗺️ Map Filters")
        
        violations = ["All"] + sorted(df['Violation Type'].unique().tolist())
        selected_v = st.selectbox("Violation Type", violations, key="h_v")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=min_date, key="h_s")
        with col2:
            end_date = st.date_input("End Date", value=max_date, key="h_e")
        
        vehicles = ["All"] + sorted(df['VehicleType'].dropna().unique().tolist())
        selected_vehicle = st.selectbox("Vehicle Type", vehicles, key="h_veh")
        
        races = ["All"] + sorted(df['Race'].dropna().unique().tolist())
        selected_race = st.selectbox("Race", races, key="h_r")
        
        genders = ["All"] + sorted(df['Gender'].dropna().unique().tolist())
        selected_gender = st.selectbox("Gender", genders, key="h_g")
    
    # APPLY FILTERS
    filtered_df = df.copy()
    
    if selected_v!= "All":
        filtered_df = filtered_df[filtered_df['Violation Type'] == selected_v]
    
    filtered_df = filtered_df[
        (filtered_df['Date of Stop'].dt.date >= start_date) & 
        (filtered_df['Date of Stop'].dt.date <= end_date)
    ]
    
    if selected_vehicle!= "All":
        filtered_df = filtered_df[filtered_df['VehicleType'] == selected_vehicle]
    
    if selected_race!= "All":
        filtered_df = filtered_df[filtered_df['Race'] == selected_race]
    
    if selected_gender!= "All":
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
    import folium
    from streamlit_folium import st_folium

    # SHOW MAP
    if filtered_df.empty:
        st.warning("No data for selected filters")
    else:
        st.write(f"Total incidents: {len(filtered_df):,}")
        
        # 1. Aggregate + round for speed
        agg_df = filtered_df.copy()
        agg_df['latitude'] = agg_df['latitude'].round(3) # 3 decimals = ~100m precision
        agg_df['longitude'] = agg_df['longitude'].round(3)
        agg_df = agg_df.groupby(['latitude', 'longitude']).size().reset_index(name='count')
        
        # 2. Take top 1000 hotspots only - cleaner map
        agg_df = agg_df.sort_values('count', ascending=False).head(1000)
        
        # 3. Center map
        lat_center = agg_df['latitude'].mean()
        lon_center = agg_df['longitude'].mean()
        
        # 4. Create Folium map
        m = folium.Map(location=[lat_center, lon_center], zoom_start=11, tiles="CartoDB positron")
        
        # 5. Add circle markers - bigger circle = more incidents
        for idx, row in agg_df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=np.sqrt(row['count']) / 5, # scale circle size
                popup=f"Incidents: {row['count']}<br>Lat: {row['latitude']}<br>Lon: {row['longitude']}",
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.6
            ).add_to(m)
        
        # 6. Display in Streamlit
        st_folium(m, width="stretch", height=600)
        st.subheader("Top 10 Hotspot Areas")

        # Add Rank column instead of random index
        top10 = agg_df.sort_values('count', ascending=False).head(10).reset_index(drop=True)
        top10.index = top10.index + 1  # start from 1
        top10.index.name = 'Rank'

        st.dataframe(top10, width="stretch")    


# ---------- PAGE 4: View summary statistics ----------
elif page == "View summary statistics":

    import mysql.connector

    st.set_page_config(page_title="Summary Statistics", layout="wide")
    st.title("📊 Summary Statistics")

    # 1. DB connection - use mysql.connector like your Jupyter notebook
    @st.cache_data(ttl=600)
    def run_query(query):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="hopePraise8gt"
        )
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    # 2. Filters - match your columns
    st.sidebar.header("Filters")

    # Year from Date Of Stop
    years = run_query("SELECT DISTINCT YEAR(`Date Of Stop`) as yr FROM guvi_db.Traffic_Violations ORDER BY yr DESC")['yr'].tolist()
    year = st.sidebar.selectbox("Year", years)

    # Agency filter
    agencies = run_query("SELECT DISTINCT Agency FROM guvi_db.Traffic_Violations ORDER BY Agency")['Agency'].tolist()
    agency = st.sidebar.multiselect("Agency", agencies, default=agencies)

    # 3. WHERE clause
    where_clauses = [f"YEAR(`Date Of Stop`) = {year}"]
    if agency:
        agency_str = "','".join([str(a).replace("'", "''") for a in agency])
        where_clauses.append(f"Agency IN ('{agency_str}')")
    where_sql = " AND ".join(where_clauses)

    # 4. KPI Query - fixed for only_full_group_by
    kpi_query = f"""
    SELECT
        COUNT(*) as total_violations,
        SUM(CASE WHEN `Accident` = 'Yes' THEN 1 ELSE 0 END) as accident_count,
        COUNT(DISTINCT CONCAT(ROUND(`Latitude`, 3), ',', ROUND(`Longitude`, 3))) as total_zones
    FROM guvi_db.Traffic_Violations
    WHERE {where_sql}
    """
    kpi_df = run_query(kpi_query)

    # 5. High-risk zones - separate query with HAVING
    high_risk_query = f"""
    SELECT COUNT(*) as high_risk_zones FROM (
        SELECT ROUND(`Latitude`, 3) as lat_r, ROUND(`Longitude`, 3) as lon_r
        FROM guvi_db.Traffic_Violations
        WHERE {where_sql}
        GROUP BY lat_r, lon_r
        HAVING COUNT(*) > 100
    ) z
    """
    high_risk_df = run_query(high_risk_query)

    # Run queries
    kpi_df = run_query(kpi_query) # returns: total_violations, accident_count, total_zones
    high_risk_df = run_query(high_risk_query) # returns: high_risk_zones

    # Display KPIs
    if not kpi_df.empty and kpi_df['total_violations'].iloc[0] > 0:
        col1, col2, col3, col4 = st.columns(4)
        total = kpi_df['total_violations'].iloc[0]
        accidents = kpi_df['accident_count'].iloc[0]
        total_zones = kpi_df['total_zones'].iloc[0]
        
        # high_risk comes from separate df
        high_risk = high_risk_df['high_risk_zones'].iloc[0] if not high_risk_df.empty else 0

        with col1:
            st.metric("Total Violations", f"{total:,}")
        with col2:
            pct = (accidents/total)*100 if total > 0 else 0
            st.metric("Accident Involved", f"{accidents:,}", f"{pct:.1f}%")
        with col3:
            st.metric("High-Risk Zones", f"{high_risk:,}", ">100 violations")
        with col4:
            st.metric("Total Zones", f"{total_zones:,}")
    else:
        st.warning("No data for selected filters")


# ---------- PAGE 3: EDA Report ----------
elif page == "EDA Report":

    st.set_page_config(page_title="EDA Report", layout="wide")
    st.title("📈 EDA Report")

    # DB connection function for this page
    @st.cache_data(ttl=600)
    def run_query(query):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="hopePraise8gt", # change to your MySQL password
            database="guvi_db",
            port=3306
        )
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    st.divider()
    st.subheader("Filters")

    # Filters - same as Summary page so analysis is consistent
    years = run_query("SELECT DISTINCT YEAR(`Date Of Stop`) as yr FROM guvi_db.Traffic_Violations ORDER BY yr DESC")['yr'].tolist()
    year = st.sidebar.selectbox("Select Year", years)

    agencies = run_query("SELECT DISTINCT Agency FROM guvi_db.Traffic_Violations ORDER BY Agency")['Agency'].tolist()
    agency = st.sidebar.multiselect("Select Agency", agencies, default=agencies)

    # Build WHERE clause
    where_clauses = [f"YEAR(`Date Of Stop`) = {year}"]
    if agency:
        agency_str = "','".join([str(a).replace("'", "''") for a in agency])
        where_clauses.append(f"Agency IN ('{agency_str}')")
    where_sql = " AND ".join(where_clauses)

    st.markdown(f"**Analyzing data for:** Year = {year} | Agency = {agency if agency else 'All'}")
    st.divider()

    st.subheader("Structured Analysis")

    # 1. Most Common Violations by Violation Type
    st.markdown("**1. Most Common Violation Types**")
    viol_type_query = f"""
    SELECT `Violation Type`, COUNT(*) as count,
        ROUND(COUNT(*)*100.0 / SUM(COUNT(*)) OVER(), 2) as pct
    FROM guvi_db.Traffic_Violations
    WHERE {where_sql}
    AND `Violation Type` IS NOT NULL 
    AND `Violation Type` != ''
    GROUP BY `Violation Type`
    ORDER BY count DESC
    LIMIT 10
    """
    viol_type_df = run_query(viol_type_query)

    if not viol_type_df.empty:
        col1, col2 = st.columns([2,1])
        with col1:
            st.bar_chart(viol_type_df.set_index('Violation Type')['count'])
        with col2:
            st.dataframe(viol_type_df, use_container_width=True, hide_index=True)
            st.caption("Top 10 Violation Types with %")
    else:
        st.info("No Violation Type data for selected filters")

    # 2. High Incident Areas/Coordinates
    st.markdown("**2. High Incident Areas - Top 20 Zones**")
    hotspot_query = f"""
    SELECT ROUND(`Latitude`, 3) as Latitude, ROUND(`Longitude`, 3) as Longitude, COUNT(*) as violations
    FROM guvi_db.Traffic_Violations
    WHERE {where_sql}
    AND `Latitude` IS NOT NULL AND `Longitude` IS NOT NULL
    GROUP BY Latitude, Longitude
    ORDER BY violations DESC
    LIMIT 20
    """
    hotspot_df = run_query(hotspot_query)
    st.dataframe(hotspot_df, use_container_width=True, hide_index=True)

    # 3. Agency vs Violation Type - Demographics not available, using Agency instead
    st.markdown("**3. Agency vs Violation Types**")
    agency_viol_query = f"""
    SELECT Agency, `Description`, COUNT(*) as count
    FROM guvi_db.Traffic_Violations
    WHERE {where_sql}
    GROUP BY Agency, `Description`
    ORDER BY count DESC
    LIMIT 15
    """
    agency_df = run_query(agency_viol_query)
    if not agency_df.empty:
        pivot_df = agency_df.pivot(index='Agency', columns='Description', values='count').fillna(0)
        st.bar_chart(pivot_df)
    else:
        st.info("No data for Agency vs Violation")

    # 4. Violation frequency by time/day/month
    st.markdown("**4. Violation Frequency by Time**")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        hour_query = f"SELECT HOUR(`Time Of Stop`) as Hour, COUNT(*) as count FROM guvi_db.Traffic_Violations WHERE {where_sql} GROUP BY Hour ORDER BY Hour"
        hour_df = run_query(hour_query)
        st.bar_chart(hour_df.set_index('Hour'))
        st.caption("By Hour of Day")

    with col_b:
        dow_query = f"SELECT DAYNAME(`Date Of Stop`) as Day, COUNT(*) as count FROM guvi_db.Traffic_Violations WHERE {where_sql} GROUP BY Day, DAYOFWEEK(`Date Of Stop`) ORDER BY DAYOFWEEK(`Date Of Stop`)"
        dow_df = run_query(dow_query)
        st.bar_chart(dow_df.set_index('Day'))
        st.caption("By Day of Week")

    with col_c:
        month_query = f"SELECT MONTHNAME(`Date Of Stop`) as Month, COUNT(*) as count FROM guvi_db.Traffic_Violations WHERE {where_sql} GROUP BY Month, MONTH(`Date Of Stop`) ORDER BY MONTH(`Date Of Stop`)"
        month_df = run_query(month_query)
        st.bar_chart(month_df.set_index('Month'))
        st.caption("By Month")

    # 5. Vehicle Types - Using VehicleType column from your schema
    st.markdown("**5. Vehicle Types Often Used in Violations**")
    vehicle_query = f"""
    SELECT `VehicleType`, COUNT(*) as count,
        ROUND(COUNT(*)*100.0 / SUM(COUNT(*)) OVER(), 2) as pct
    FROM guvi_db.Traffic_Violations
    WHERE {where_sql}
    AND `VehicleType` IS NOT NULL 
    AND `VehicleType` != ''
    GROUP BY `VehicleType`
    ORDER BY count DESC
    LIMIT 10
    """
    vehicle_df = run_query(vehicle_query)
    if not vehicle_df.empty:
        col1, col2 = st.columns([2,1])
        with col1:
            st.bar_chart(vehicle_df.set_index('VehicleType')['count'])
        with col2:
            st.dataframe(vehicle_df, use_container_width=True, hide_index=True)
            st.caption("Top 10 Vehicle Types")
    else:
        st.info("No VehicleType data for selected filters")

    # 6. Accidents/Injuries/Damage
    st.markdown("**6. Accidents & Contribution**")
    col_x, col_y = st.columns(2)

    with col_x:
        acc_query = f"SELECT `Accident`, COUNT(*) as count FROM guvi_db.Traffic_Violations WHERE {where_sql} GROUP BY `Accident`"
        acc_df = run_query(acc_query)
        st.bar_chart(acc_df.set_index('Accident'))
        st.caption("Accident Involvement")

    with col_y:
        contrib_query = f"SELECT `Contributed To Accident`, COUNT(*) as count FROM guvi_db.Traffic_Violations WHERE {where_sql} AND `Contributed To Accident` IS NOT NULL GROUP BY `Contributed To Accident`"
        contrib_df = run_query(contrib_query)
        st.bar_chart(contrib_df.set_index('Contributed To Accident'))
        st.caption("Contributed to Accident")

    # 7. Vehicle Type vs Accident Rate - Bonus insight

    acc_veh_query = f"""
    SELECT `VehicleType`, 
        COUNT(*) as total,
        SUM(CASE WHEN `Accident` = 'Yes' THEN 1 ELSE 0 END) as accidents,
        ROUND(SUM(CASE WHEN `Accident` = 'Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*), 2) as accident_pct
    FROM guvi_db.Traffic_Violations
    WHERE {where_sql} AND `VehicleType` IS NOT NULL AND `VehicleType` != ''
    GROUP BY `VehicleType`
    ORDER BY accident_pct DESC
    LIMIT 10
    """
    acc_veh_df = run_query(acc_veh_query)

    import altair as alt

    st.markdown("**7. Accident Rate by Vehicle Type**")

    st.markdown("""
    <style>
    /* Table headers - more specific selector */
    div[data-testid="stDataFrame"] thead tr th {
        font-size: 17px !important;
        font-weight: 800 !important;
        color: #1a1a1a !important;
        background-color: #f0f2f6 !important;
        padding-top: 12px !important;
        padding-bottom: 12px !important;
    }
    /* Table cells */
    div[data-testid="stDataFrame"] tbody tr td {
        font-size: 16px !important;
        color: #262730 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    #st.set_page_config(page_title="Traffic Violation Dashboard", layout="wide")


    if not acc_veh_df.empty:
        max_val = acc_veh_df['accident_pct'].max()
        
        bars = alt.Chart(acc_veh_df).mark_bar(color='#1f77b4').encode(
            y=alt.Y('VehicleType:N', sort='-x', title='Vehicle Type',
                    axis=alt.Axis(labelFontSize=18, titleFontSize=20,labelFontWeight='bold', titleFontWeight='bold',labelLimit=250)),
            x=alt.X('accident_pct:Q', title='Accident %',
                    axis=alt.Axis(labelFontSize=18, titleFontSize=20,labelFontWeight='bold',titleFontWeight='bold'),
                    scale=alt.Scale(domain=[0, max_val*1.4])),
            tooltip=['VehicleType', 'total', 'accidents', alt.Tooltip('accident_pct:Q', format='.2f')]
        )
        
        text = alt.Chart(acc_veh_df).mark_text(
            fontSize=16,
            fontWeight='bold',
            dx=alt.expr('datum.accident_pct > 3 ? -35 : 5'),  # ternary: if >3 then -35 else 5
            align=alt.expr('datum.accident_pct > 3 ? "right" : "left"'),
            color=alt.expr('datum.accident_pct > 3 ? "white" : "black"')
        ).encode(
            y=alt.Y('VehicleType:N', sort='-x'),
            x=alt.X('accident_pct:Q'),
            text=alt.Text('accident_pct:Q', format='.2f')
        )
        
        chart = (bars + text).properties(height=450)
        st.altair_chart(chart, use_container_width=True)

        display_df = acc_veh_df.copy()
        display_df['accident_pct'] = display_df['accident_pct'].map('{:.2f}%'.format)

        # Rename columns for clean headers
        display_df = display_df.rename(columns={
            'VehicleType': 'Vehicle Type',
            'total': 'Total Cases', 
            'accidents': 'Accident Count',
            'accident_pct': 'Accident %'
        })[["Vehicle Type", "Total Cases", "Accident Count", "Accident %"]]

        st.table(display_df)  # st.table instead of st.markdown


        st.markdown("""
        <style>
        /* Target st.table headers */
        table thead tr th {
            font-size: 18px !important;
            font-weight: 800 !important;
            color: #000 !important;
            background-color: #e1e4e8 !important;
            padding: 14px 10px !important;
            border-bottom: 2px solid #999 !important;
        }
        /* Table cells */
        table tbody tr td {
            font-size: 16px !important;
            color: #262730 !important;
            padding: 12px 10px !important;
        }
        </style>
        """, unsafe_allow_html=True)


# ---------- PAGE 5: Univariate ----------
elif page == "Univariate":
    st.title("Univariate Analysis on Columns")       
    column = st.selectbox("Select Column", 
                           ['Agency','SubAgency','Accident','Belts','Personal Injury',
                            'Property Damage','Fatal','Commercial License','HAZMAT',
                            'Commercial Vehicle','Alcohol','Work Zone','Search Conducted',
                            'Search Disposition','Search Outcome','Search Reason',
                            'Search Type','Search Arrest Reason','VehicleType'
                            ])

    query = f"""
    SELECT `{column}`, COUNT(*) as COUNT
    FROM guvi_db.Traffic_Violations
    GROUP BY `{column}`
    ORDER BY COUNT DESC
    """
    df = get_data(query)      
    if not df.empty:
      
        plt.clf()
        fig, ax = plt.subplots(figsize=(14,6))
        
        # Turn off scientific notation + show commas
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

        #sns.violinplot(df, showmedians=True)
        sns.barplot(data=df, x=column, y='COUNT', ax=ax, color='skyblue',linewidth=0,edgecolor='skyblue')
        plt.xticks(rotation=90)
        plt.title(f"Traffic Violations - {column}",fontsize=16,pad=20)
        plt.xlabel(column, fontsize=10)
        plt.ylabel('COUNT', fontsize=10)

        # Add count labels on top of bar
        max_count = df['COUNT'].max()
        for i, v in enumerate(df['COUNT']):
            #ax.text(i, v + v*0.01, f'{v:,}', ha='center', va='bottom', fontsize=6)
            ax.text(i, v + max_count*0.02, f'{v:,}', ha='center', va='bottom',fontsize=8,rotation=90)
        
        plt.ylim(0, max_count * 1.15)  # Add 15% headroom so labels don't get cut

        plt.tight_layout()
        st.pyplot(fig, width='content')
    else:
        st.warning("No data available")

# ---------- PAGE 5: Bivariate ----------

elif page == "Bivariate":
    st.title("Bivariate Analysis")
    st.write("Plot illustrates Vehicle types that contribute to accidents and the root cause based on violation")
    
    query = """
    SELECT `VehicleType`, 
           CASE WHEN `Contributed To Accident` = 1 THEN 'Yes' ELSE 'No' END as Accident,
           `Gender`, COUNT(*) as COUNT
    FROM guvi_db.Traffic_Violations
    WHERE `VehicleType` IS NOT NULL AND `Gender` IN ('M','F')
    GROUP BY `VehicleType`, `Contributed To Accident`, `Gender`
    """
    
    df = get_data(query)
    
    # Top 10 vehicle types only
    top_vehicles = df.groupby('VehicleType')['COUNT'].sum().nlargest(10).index
    df = df[df['VehicleType'].isin(top_vehicles)]
    
    plt.close('all')
    g = sns.FacetGrid(df, col='Gender', height=5, aspect=1.2, sharey=True)
    
    # Map barplot to each facet
    g.map_dataframe(sns.barplot, x='VehicleType', y='COUNT', hue='Accident',
                    palette={'Yes':'tomato', 'No':'skyblue'}, edgecolor='none', linewidth=0, order=top_vehicles)


# Add count labels fixed above x-axis
    def add_labels(data, **kws):
        ax = plt.gca()
        ylim = ax.get_ylim()[1] # Get max y value of that subplot
        y_pos = ylim * 0.05  # 3% above x-axis for all bars
    
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.text(p.get_x() + p.get_width()/2., y_pos,
                    f'{int(height):,}', ha="center", va="bottom", 
                    rotation=90, fontsize=9)

    g.map_dataframe(add_labels)

    # Titles + labels for all facets - MUST come before formatting loop
    g.set_titles("Gender: {col_name}")
    g.set_axis_labels("Vehicle Type", "Count")
    g.fig.suptitle("Accident Count by Vehicle Type & Gender", fontsize=16, y=1.03)

    # Rotate x labels + add commas to y-axis
    for ax in g.axes.flat:
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        ax.tick_params(axis='x', rotation=90, labelsize=9)
        ax.set_xlabel("Vehicle Type", fontsize=11)
        ax.set_ylabel("Count", fontsize=11)

    g.add_legend(title='Accident')
    plt.tight_layout()
    g.fig.subplots_adjust(bottom=0.25, top=0.90)

    # ONLY ONE st.pyplot at the very end
    st.pyplot(g.fig, width='stretch')


# ---------- PAGE 5: Multivariate ----------
elif page == "Multivariate":
    st.title("Violation Type vs Agency Heatmap")
    st.write("##Top 20 Violations")
    
    # Get cross-tab data
    query = """
        SELECT `Description` as Violation, `Agency`, COUNT(*) as COUNT
        FROM guvi_db.Traffic_Violations
        GROUP BY `Description`, `Agency`
     """
    df = get_data(query)
    
    # Convert to pivot table for heatmap
    pivot_df = df.pivot_table(index='Violation', columns='Agency', values='COUNT', aggfunc='sum', fill_value=0)
    
    # Take top 15 violations only, else heatmap gets messy
    pivot_df = pivot_df.loc[pivot_df.sum(axis=1).sort_values(ascending=False).head(20).index]
    
    plt.clf()
    fig, ax = plt.subplots(figsize=(14,10))
    
    # Draw heatmap
    sns.heatmap(pivot_df, annot=True, fmt='g', cmap='YlGnBu', linewidths=0.5, ax=ax)
    
    plt.title("Violation Count by Agency", fontsize=16, pad=30)
    plt.xlabel("Agency", fontsize=12)
    plt.ylabel("Violation Type", fontsize=12)
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    st.pyplot(fig, width='stretch')


# ---------- PAGE 5: Creator Info ----------
elif page == "Creator Info":
    st.title("👨‍💻 Creator of this Project")
    st.write("""
    **Developed by:** CharlieJeba
    **Skills:** Python, SQL, Data Analysis, Streamlit, Pandas
    """)
    st.image("https://via.placeholder.com/150", caption="Your Profile Picture", width=150)