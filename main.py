import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import h3  

weather_data = pd.read_csv('data/weather-manhattan-meteo.csv', 
                          skiprows=2,  # Skip the first two rows
                          delimiter=',',  
                          low_memory=False)  

collision_data = pd.read_csv('data/motor_vehicle_collisions_-_crashes_20250320.csv',
                            low_memory=False)  

# Format date columns for both datasets
original_time_col = weather_data.columns[0]
weather_data['date'] = pd.to_datetime(weather_data.iloc[:, 0])

collision_data['date'] = pd.to_datetime(collision_data['CRASH DATE'])

manhattan_collisions = collision_data[collision_data['BOROUGH'] == 'MANHATTAN']

manhattan_collisions_with_coords = manhattan_collisions.dropna(subset=['LATITUDE', 'LONGITUDE'])

# Group Manhattan collisions by date to get daily counts and injury/fatality data
daily_manhattan = manhattan_collisions.groupby('date').agg({
    'CRASH DATE': 'count',  # Count of collisions
    'NUMBER OF PERSONS INJURED': 'sum',  # Sum of injuries
    'NUMBER OF PERSONS KILLED': 'sum'    # Sum of fatalities
}).reset_index()

# Rename columns for clarity
daily_manhattan.rename(columns={
    'CRASH DATE': 'collision_count',
    'NUMBER OF PERSONS INJURED': 'injuries_count',
    'NUMBER OF PERSONS KILLED': 'fatalities_count'
}, inplace=True)

# Merge the datasets on the date column with inner join to only include matching dates
merged_df = pd.merge(weather_data, daily_manhattan, on='date', how='inner')

# Rename the original time column to 'date' and drop the temporary date column
merged_df.rename(columns={original_time_col: 'date_str'}, inplace=True)
merged_df = merged_df.drop(columns=['date'])
merged_df.rename(columns={'date_str': 'date'}, inplace=True)

# Convert date to datetime for filtering
merged_df['date'] = pd.to_datetime(merged_df['date'])

# Filter data to include only complete years (2013-2024)
filtered_df = merged_df[(merged_df['date'] >= '2013-01-01') & (merged_df['date'] <= '2024-12-31')]

print(f"Weather data date range: {weather_data['date'].min()} to {weather_data['date'].max()}")
print(f"Manhattan collision data date range: {daily_manhattan['date'].min()} to {daily_manhattan['date'].max()}")
print(f"Filtered data date range: {filtered_df['date'].min()} to {filtered_df['date'].max()}")
print(f"Total days in filtered dataset: {len(filtered_df)}")

# Save the filtered merged dataset
filtered_df.to_csv('data/weather_collision_merged_2013_2024.csv', index=False)
print("Filtered dataset saved to 'data/weather_collision_merged_2013_2024.csv'")

# ---- Visualization: Time Series of Accidents by Year ----

# Extract year from date
filtered_df['year'] = filtered_df['date'].dt.year

# Group by year and sum the collision counts
yearly_accidents = filtered_df.groupby('year').agg({
    'collision_count': 'sum',
    'injuries_count': 'sum',
    'fatalities_count': 'sum'
}).reset_index()

# Create a time series line graph for yearly accidents with gradient color
fig = go.Figure()

colors = [
    (95, 47, 143),    # Brighter dark purple (lowest)
    (130, 44, 149),   # Brighter purple
    (178, 54, 144),   # Brighter magenta-purple
    (222, 73, 131),   # Brighter dark pink
    (255, 90, 104),   # Brighter red
    (255, 128, 76),   # Brighter orange-red
    (255, 177, 58),   # Brighter orange
    (255, 231, 65),   # Brighter yellow-orange (highest)
]

# Normalize the collision counts for color mapping
min_count = yearly_accidents['collision_count'].min()
max_count = yearly_accidents['collision_count'].max()

# Create a scatter trace with gradient color
for i in range(len(yearly_accidents) - 1):
    # Get the current and next year's data
    current_year = yearly_accidents.iloc[i]
    next_year = yearly_accidents.iloc[i + 1]
    
    # Normalize the current year's count for color selection
    normalized_count = (current_year['collision_count'] - min_count) / (max_count - min_count)
    color_idx = min(int(normalized_count * len(colors)), len(colors) - 1)
    
    # Get RGB color
    r, g, b = colors[color_idx]
    line_color = f'rgb({r},{g},{b})'
    
    # Add a line segment between current and next year
    fig.add_trace(go.Scatter(
        x=[current_year['year'], next_year['year']],
        y=[current_year['collision_count'], next_year['collision_count']],
        mode='lines',
        line=dict(color=line_color, width=4),
        showlegend=False,
        hoverinfo='skip'
    ))

# Add markers on top of the gradient line
fig.add_trace(go.Scatter(
    x=yearly_accidents['year'],
    y=yearly_accidents['collision_count'],
    mode='markers+text',
    marker=dict(
        size=12,
        color=[f'rgb({colors[min(int((val - min_count) / (max_count - min_count) * len(colors)), len(colors) - 1)][0]}, '
               f'{colors[min(int((val - min_count) / (max_count - min_count) * len(colors)), len(colors) - 1)][1]}, '
               f'{colors[min(int((val - min_count) / (max_count - min_count) * len(colors)), len(colors) - 1)][2]})' 
               for val in yearly_accidents['collision_count']],
        line=dict(color='white', width=1)
    ),
    text=[f"{int(val):,}" for val in yearly_accidents['collision_count']],
    textposition="top center",
    textfont=dict(color='white', size=10),
    name='Total Collisions',
    hovertemplate='Year: %{x}<br>Collisions: %{y:,}<extra></extra>'
))

fig.update_layout(
    title=dict(
        text='<b>Total Manhattan Traffic Collisions by Year (2013-2024)</b>',
        font=dict(color='white', size=24, family='Arial Black'),
        x=0.5,  # Center the title
        y=0.95  # Adjust vertical position
    ),
    xaxis_title=None,  # Remove the "Year" title
    yaxis_title=None,
    template='plotly_dark',
    hovermode='x unified',
    xaxis=dict(
        tickmode='linear',
        tick0=yearly_accidents['year'].min(),
        dtick=1,
        gridcolor='#333333',
        zerolinecolor='#333333'
    ),
    yaxis=dict(
        gridcolor='#333333',
        zerolinecolor='#333333'
    ),
    paper_bgcolor='#1e1e1e',
    plot_bgcolor='#1e1e1e',
    font=dict(color='white')
)

# Fix the annotation update method name
# Add annotations for significant changes or trends
max_year = yearly_accidents.loc[yearly_accidents['collision_count'].idxmax()]
min_year = yearly_accidents.loc[yearly_accidents['collision_count'].idxmin()]

fig.add_annotation(
    x=max_year['year'],
    y=max_year['collision_count'],
    text=f"Highest",
    showarrow=True,
    arrowhead=1,
    ax=0,
    ay=-40
)

fig.add_annotation(
    x=min_year['year'],
    y=min_year['collision_count'],
    text=f"Lowest",
    showarrow=True,
    arrowhead=1,
    ax=-75,   # Move it to the left
    ay=-40
)

# Add COVID lockdown annotation
fig.add_annotation(
    x=2020,
    y=yearly_accidents.loc[yearly_accidents['year'] == 2020, 'collision_count'].values[0],
    text="Major decrease due to COVID-19 lockdowns",
    showarrow=True,
    arrowhead=1,
    ax=150,
    ay=-100,
    font=dict(color="white", size=12),
    bgcolor="rgba(0,0,0,0.7)",
    bordercolor="white",
    borderwidth=1
)

fig.show()

fig.write_html("visuals/manhattan_yearly_collisions_2013_2024.html")
print("Yearly collisions visualization saved to 'manhattan_yearly_collisions_2013_2024.html'")

# ---- Visualization: Dynamic Weather Conditions Analysis with Year Selector ----

# Update weather condition categories based on WMO code 4677
weather_categories = {
    'Clear': [0, 1, 2, 3],  # Cloud development, dissolving, unchanged, forming
    'Haze/Smoke': [4, 5, 6],  # Visibility reduced by smoke, haze, dust in suspension
    'Dust/Sand': [7, 8, 9],  # Dust/sand raised by wind, dust whirls, dust/sandstorm
    'Fog/Mist': [10, 11, 12, 28, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49],  # Mist, fog patches, fog
    'Lightning': [13, 17],  # Lightning visible, thunderstorm without precipitation
    'Precipitation': [14, 15, 16, 18, 19],  # Precipitation not reaching ground, distant, nearby, squalls, funnel clouds
    'Drizzle': [20, 21, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59],  # Drizzle (not freezing) and combinations
    'Rain': [22, 24, 25, 27, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 80, 81, 82, 91, 92],  # Rain, freezing rain, showers
    'Snow': [23, 26, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 83, 84, 85, 86, 87, 88, 93, 94],  # Snow, snow grains, ice pellets
    'Thunderstorm': [29, 95, 96, 97, 98, 99]  # Thunderstorm with/without precipitation
}

# Create a new column for weather category
def categorize_weather(code):
    for category, codes in weather_categories.items():
        if code in codes:
            return category
    return 'Other'

# Add weather category to the filtered dataframe
filtered_df['weather_category'] = filtered_df['weather_code (wmo code)'].apply(categorize_weather)

# Clear any previous traces and create a completely new figure
fig2 = make_subplots(rows=1, cols=2, 
                    column_widths=[0.7, 0.3],
                    subplot_titles=('', ''))

# Update colors for all weather categories
colors = {
    'Clear': '#de4993',          # Magenta-purple
    'Haze/Smoke': '#5f2f8f',     # Dark purple
    'Dust/Sand': '#822c95',      # Purple
    'Fog/Mist': '#9a3a8f',       # Light purple
    'Lightning': '#b54a87',      # Pink-purple
    'Precipitation': '#cf5a7f',  # Pink
    'Drizzle': '#5f2f8f',        # Salmon
    'Rain': '#FF804C',           # Coral
    'Snow': '#9a3a8f',           # Orange-red
    'Thunderstorm': '#ff9a5f',   # Orange
    'Other': '#ff7a6f'           # Light orange
}

# Process data for all years (2013-2024)
years = sorted(filtered_df['year'].unique())

# Create empty lists to store traces for each year
year_traces = {}

# First, create all traces for all years
for year in years:
    year_traces[year] = []
    
    # Filter data for this specific year only
    year_data = filtered_df[filtered_df['year'] == year].copy()
    
    # Extract month from date for this year's data
    year_data['month'] = year_data['date'].dt.month
    
    # Group by month and weather category for this year
    weather_monthly = year_data.groupby(['month', 'weather_category']).agg({
        'collision_count': 'sum'
    }).reset_index()
    
    # Calculate totals by weather category for this year
    weather_totals = year_data.groupby('weather_category').agg({
        'collision_count': 'sum'
    }).reset_index()
    
    # Sort by total collisions descending
    weather_totals = weather_totals.sort_values('collision_count', ascending=False)
    
    # Add traces for monthly data (lines)
    for category in sorted(weather_totals['weather_category'].unique()):
        category_data = weather_monthly[weather_monthly['weather_category'] == category]
        
        # Create a complete month range (1-12) with zeros for missing months
        all_months = pd.DataFrame({'month': range(1, 13)})
        category_data = pd.merge(all_months, category_data, on='month', how='left').fillna(0)
        category_data = category_data.sort_values('month')
        
        # Add the trace with visibility set to False (except for 2024 which is default)
        trace_idx = len(fig2.data)
        fig2.add_trace(
            go.Scatter(
                x=category_data['month'],
                y=category_data['collision_count'],
                mode='lines+markers',
                name=f"{category} ({year})",  
                line=dict(color=colors.get(category, 'white'), width=4),
                marker=dict(size=8),
                visible=(year == 2024),  
                legendgroup=f"{category}_{year}",  
                hovertemplate=f"<b>{category}</b><br>Collisions: %{{y}}<br>Month: %{{x}}<extra></extra>",
                hoverlabel=dict(bgcolor='rgba(0,0,0,0.8)', font=dict(color='white'))  
            ),
            row=1, col=1
        )
        year_traces[year].append(trace_idx)
    
    # Add bar chart for totals
    for i, (_, row) in enumerate(weather_totals.iterrows()):
        category = row['weather_category']
        trace_idx = len(fig2.data)
        fig2.add_trace(
            go.Bar(
                x=[category],
                y=[row['collision_count']],
                name=f"{category} ({year})",  
                marker_color=colors.get(category, 'white'),
                text=row['collision_count'],
                textposition='auto',
                textfont=dict(color='white'),
                visible=(year == 2024),  
                legendgroup=f"{category}_{year}",  
                showlegend=False,
                hovertemplate=f"<b>{category}</b><br>Total: %{{y}}<extra></extra>",
                hoverlabel=dict(bgcolor='rgba(0,0,0,0.8)', font=dict(color='white'))  
            ),
            row=1, col=2
        )
        year_traces[year].append(trace_idx)

dropdown_buttons = []
for year in years:
    visible_array = [False] * len(fig2.data)
    
    for trace_idx in year_traces[year]:
        visible_array[trace_idx] = True
    
    # Create
    button = dict(
        method="update",
        label=str(year),
        args=[
            {"visible": visible_array},
            {"title.text": f"<b>Manhattan Traffic Collisions by Weather Condition ({year})</b>"}
        ]
    )
    dropdown_buttons.append(button)

# dropdown styles
fig2.update_layout(
    updatemenus=[
        dict(
            active=years.index(2024),  
            buttons=dropdown_buttons,
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.25,  
            xanchor="left",
            y=1.15,
            yanchor="top",
            bgcolor="#333333",
            font=dict(color="white"),
            bordercolor="#666666",  
            borderwidth=1  
        )
    ]
)

for button in dropdown_buttons:
    button["label"] = f"<b>{button['label']}</b>"  # Make labels bold for better visibility

# Update the label position 
fig2.add_annotation(
    x=0.11,  
    y=1.12,
    xref="paper",
    yref="paper",
    text="Select Year:",
    showarrow=False,
    font=dict(size=14, color="white"),
    align="right"
)

# Update layout with dark mode
fig2.update_layout(
    title=dict(
        text='<b>Manhattan Traffic Collisions by Weather Condition (2024)</b>',
        font=dict(color='white', size=24, family='Arial Black'),
        x=0.5,
        y=0.95
    ),
    template='plotly_dark',
    height=600,
    legend_title="Weather Condition",
    hovermode='x unified',
    paper_bgcolor='#1e1e1e',
    plot_bgcolor='#1e1e1e',
    font=dict(color='white'),
    margin=dict(t=120)  
)

# Update x-axis with month names
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
fig2.update_xaxes(
    title=None,
    tickmode='array',
    tickvals=list(range(1, 13)),
    ticktext=month_names,
    gridcolor='#333333',
    zerolinecolor='#333333',
    row=1, col=1
)

# Update y-axes
fig2.update_yaxes(
    title='Number of Collisions',
    gridcolor='#333333',
    zerolinecolor='#333333',
    row=1, col=1
)
fig2.update_yaxes(
    title='Total Collisions',
    gridcolor='#333333',
    zerolinecolor='#333333',
    row=1, col=2
)

# Update hover label 
for i in range(len(fig2.data)):
    if hasattr(fig2.data[i], 'hoverlabel'):
        fig2.data[i].hoverlabel = dict(
            bgcolor='rgba(255,255,255,0.9)',  
            font=dict(color='black', size=12),  
            bordercolor='#666666'  
        )

fig2.show()
fig2.write_html("visuals/manhattan_dynamic_weather_collisions.html")
print("Dynamic weather collisions visualization saved to 'visuals/manhattan_dynamic_weather_collisions.html'")

# ---- Visualization: True Hexagonal Binning for 2024 Manhattan Collisions ----

merged_df = pd.read_csv('data/weather_collision_merged_2013_2024.csv')

# Add location data from the original collision dataset
manhattan_collisions_with_coords = manhattan_collisions.dropna(subset=['LATITUDE', 'LONGITUDE'])
location_data = manhattan_collisions_with_coords[['CRASH DATE', 'LATITUDE', 'LONGITUDE']]
location_data['date'] = pd.to_datetime(location_data['CRASH DATE'])

# Merge location data with our weather-collision dataset
merged_df['date'] = pd.to_datetime(merged_df['date'])
merged_with_location = pd.merge(merged_df, location_data, on='date', how='left')

# Filter for initial year data directly
initial_year = 2024  
year_data = merged_with_location[merged_with_location['date'].dt.year == initial_year]
print(f"Number of Manhattan collisions in {initial_year} with valid coordinates: {len(year_data)}")

# Adjust the H3 resolution to create larger hexagons
resolution = 9  

# Convert lat/lon to H3 indices
year_data['h3_index'] = year_data.apply(
    lambda row: h3.latlng_to_cell(row['LATITUDE'], row['LONGITUDE'], resolution), 
    axis=1
)

# Count collisions per hexagon
hex_counts = year_data.groupby('h3_index').size().reset_index(name='count')

# Get hexagon boundaries and center points
hex_counts['hex_boundary'] = hex_counts['h3_index'].apply(
    lambda h: h3.cell_to_boundary(h)
)
hex_counts['lat'] = hex_counts['h3_index'].apply(
    lambda h: h3.cell_to_latlng(h)[0]
)
hex_counts['lon'] = hex_counts['h3_index'].apply(
    lambda h: h3.cell_to_latlng(h)[1]
)

# Create the hexbin map
fig3 = go.Figure()

# Update the hexagon creation with adjustable opacity
for idx, row in hex_counts.iterrows():
    
    min_count = hex_counts['count'].min()
    max_count = hex_counts['count'].max()
    normalized_count = (row['count'] - min_count) / (max_count - min_count) if max_count > min_count else 0.5
    
    # Calculate opacity based on normalized count
    opacity = 0.50 + (normalized_count * 0.35)

    color_idx = min(int(normalized_count * 10), 9)  # Ensure index is within bounds
    
    # Original color scale
    colors = [
        (95, 47, 143),    # Brighter dark purple
        (130, 44, 149),   # Brighter purple
        (178, 54, 144),   # Brighter magenta-purple
        (222, 73, 131),   # Brighter dark pink
        (255, 90, 104),   # Brighter red
        (255, 128, 76),   # Brighter orange-red
        (255, 177, 58),   # Brighter orange
        (255, 231, 65),   # Brighter yellow-orange
        (255, 255, 121),  # Brighter yellow
        (255, 255, 200)   # Brighter light yellow
    ]
    
    # Apply the calculated opacity to the color
    r, g, b = colors[color_idx]
    color_base = f'rgba({r},{g},{b},{opacity})'
    
    # Add the hexagon polygon
    fig3.add_trace(go.Scattermapbox(
        lat=[coord[0] for coord in row['hex_boundary']] + [row['hex_boundary'][0][0]],
        lon=[coord[1] for coord in row['hex_boundary']] + [row['hex_boundary'][0][1]],
        mode='lines',
        fill='toself',
        fillcolor=color_base,
        line=dict(color='rgba(0,0,0,0)', width=0),
        hoverinfo='text',
        text=f'Collisions: {row["count"]}',
        showlegend=False
    ))

# Update the layout with zoom level 11 and add color legend
fig3.update_layout(
    mapbox=dict(
        style="carto-darkmatter",
        center=dict(lat=40.7831, lon=-73.9712),  
        zoom=11  
    ),
    margin=dict(l=0, r=0, t=70, b=0),
    paper_bgcolor='#1e1e1e',
    plot_bgcolor='#1e1e1e',
    title=dict(
        text='<b>Manhattan Traffic Collision HexMap (2024)</b>',
        font=dict(color='white', size=24, family='Arial Black'),
        x=0.5,
        y=0.99
    ),
    height=1050,
    hovermode='closest'
)

# Update the color legend with descriptive labels instead of numbered levels
for i, color_tuple in enumerate(colors):
    r, g, b = color_tuple
    # Use a fixed opacity for the legend items
    legend_color = f'rgba({r},{g},{b},0.85)'
    
    # Create descriptive labels based on position in the color scale
    if i == 0:
        label = "Lowest"
    elif i == len(colors) - 1:
        label = "Highest"
    elif i == len(colors) // 2:
        label = "Medium"
    elif i < len(colors) // 2:
        label = f"Low-Medium"
    else:
        label = f"Medium-High"
    
    fig3.add_trace(go.Scattermapbox(
        lat=[0],
        lon=[0],
        mode='markers',
        marker=dict(size=10, color=legend_color),
        showlegend=True,
        name=label,
        hoverinfo='name'
    ))

# Add legend title and value ranges
fig3.add_annotation(
    xref="paper", yref="paper",
    x=0.01, y=0.05,
    text=f"Collisions",
    showarrow=False,
    font=dict(color="white", size=14, family="Arial Black"),
    align="left"
)

fig3.add_annotation(
    xref="paper", yref="paper",
    x=0.01, y=0.38,
    text=f"{max_count}",
    showarrow=False,
    font=dict(color="white", size=12),
    align="left"
)

fig3.add_annotation(
    xref="paper", yref="paper",
    x=0.01, y=0.01,
    text=f"{min_count}",
    showarrow=False,
    font=dict(color="white", size=12),
    align="left"
)

# legend position
fig3.update_layout(
    legend=dict(
        orientation="v",
        yanchor="middle",
        y=0.5,
        xanchor="right",
        x=0.99,
        font=dict(color="white"),
        bgcolor="rgba(0,0,0,0.5)"
    )
)

# Add annotations for highest and lowest hexagons
# Find the hexagons with max and min counts
max_hex = hex_counts.loc[hex_counts['count'].idxmax()]
min_hex = hex_counts.loc[hex_counts['count'].idxmin()]

# Add annotation for highest hexagon
fig3.add_trace(go.Scattermapbox(
    lat=[max_hex['lat']],
    lon=[max_hex['lon']],
    mode='markers+text',
    marker=dict(size=15, color='white', symbol='star'),
    text="Highest",
    textposition="top center",
    textfont=dict(color='white', size=14),
    hoverinfo='text',
    hovertext=f'Highest concentration: {max_hex["count"]} collisions',
    name='Highest Concentration',
    showlegend=False
))

# Add annotation for lowest hexagon with collisions
fig3.add_trace(go.Scattermapbox(
    lat=[min_hex['lat']],
    lon=[min_hex['lon']],
    mode='markers+text',
    marker=dict(size=15, color='white', symbol='circle'),
    text="Lowest",
    textposition="top center",
    textfont=dict(color='white', size=14),
    hoverinfo='text',
    hovertext=f'Lowest concentration: {min_hex["count"]} collisions',
    name='Lowest Concentration',
    showlegend=False
))

fig3.show()
fig3.write_html("visuals/manhattan_collision_hexbin_2024.html")
print("Hexbin map saved to 'visuals/manhattan_collision_hexbin_2024.html'")

# Save the merged dataset with location data
# merged_with_location.to_csv('data/weather_collision_location_merged_2013_2024.csv', index=False)
# print("Merged dataset with location data saved to 'data/weather_collision_location_merged_2013_2024.csv'")

# ---- Create a Dashboard with All Three Visualizations ----

def create_dashboard():

    yearly_html = fig.to_html(include_plotlyjs='cdn', full_html=False, config={'displayModeBar': False})
    weather_html = fig2.to_html(include_plotlyjs='cdn', full_html=False, config={'displayModeBar': False})
    hexmap_html = fig3.to_html(include_plotlyjs='cdn', full_html=False, config={'displayModeBar': False})
    
    # Create the dashboard HTML with a completely different approach
    dashboard_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manhattan Traffic Collisions Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #121212;
                color: white;
                overflow: hidden;
            }}
            .dashboard-container {{
                display: flex;
                height: calc(100vh - 60px);
                width: 100%;
            }}
            .left-panel {{
                width: 50%;
                height: 100%;
                display: flex;
                flex-direction: column;
                padding: 10px;
                box-sizing: border-box;
            }}
            .right-panel {{
                width: 50%;
                height: 100%;
                padding: 10px;
                box-sizing: border-box;
            }}
            .viz-container {{
                width: 100%;
                margin-bottom: 10px;
                background-color: #1e1e1e;
                border-radius: 8px;
                overflow: hidden;
                position: relative;
            }}
            .header {{
                background-color: #333;
                padding: 15px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                border-bottom: 1px solid #444;
                height: 60px;
                box-sizing: border-box;
            }}
            .left-panel .viz-container {{
                height: calc(50% - 5px);
            }}
            .right-panel .viz-container {{
                height: 100%;
            }}
            iframe {{
                width: 100%;
                height: 100%;
                border: none;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            Manhattan Traffic Collisions Dashboard
        </div>
        <div class="dashboard-container">
            <div class="left-panel">
                <div class="viz-container">
                    <iframe src="manhattan_yearly_collisions_2013_2024.html"></iframe>
                </div>
                <div class="viz-container">
                    <iframe src="manhattan_dynamic_weather_collisions.html"></iframe>
                </div>
            </div>
            <div class="right-panel">
                <div class="viz-container">
                    <iframe src="manhattan_collision_hexbin_2024.html"></iframe>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

    dashboard_path = 'visuals/manhattan_collisions_dashboard.html'
    with open(dashboard_path, 'w') as f:
        f.write(dashboard_html)
    
    print(f"Dashboard saved to '{dashboard_path}'")
    
    # Open the dashboard in the default web browser
    import webbrowser
    import os
    file_url = 'file://' + os.path.abspath(dashboard_path)
    webbrowser.open(file_url)

create_dashboard()
