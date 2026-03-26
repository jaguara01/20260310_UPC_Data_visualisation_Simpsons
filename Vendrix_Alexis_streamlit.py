import streamlit as st
import pandas as pd
import altair as alt
import os

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="The Simpsons: Visual Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 2. CUSTOM FUNCTIONS
# ==========================================
# Custom functions to render titles with CSS

def pink_subheader(text):
    """Custom function to render a subheader in Donut Pink."""
    st.markdown(f"<h3 style='color: #F14A9C;'>{text}</h3>", unsafe_allow_html=True)

def simpsons_title(text):
    """Custom function to render a title in Simpsons yellow and black."""
    st.markdown(
        f"""
        <h1 style='
            color: #FED41D; 
            -webkit-text-stroke: 2px #000000; 
            font-family: "Arial Black", Impact, sans-serif;
            font-weight: 900;
        '>{text}</h1>
        """,
        unsafe_allow_html=True,
    )

# ==========================================
# 3. ALTAIR CHART THEME
# ==========================================

# Creates and registers a custom Altair theme based on 'The Simpsons' color palette.
# The @alt.theme.register decorator automatically applies this styling globally to all 
# charts in the app, eliminating the need to format each chart individually.

@alt.theme.register("simpsons", enable=True)
def simpsons_theme():
    simpsons_palette = ["#009DDC", "#F05E23", "#F14A9C", "#D1B271", "#4C76B6"]
    return alt.theme.ThemeConfig(
        background="transparent",
        view={"stroke": "transparent"},
        range={
            "category": simpsons_palette,
            "heatmap": ["#009DDC", "#FFFFFF", "#F14A9C"],
        },
        title={
            "font": "sans-serif",
            "color": "#F14A9C",
            "fontSize": 18,
            "anchor": "start",
        },
        axis={
            "labelColor": "#333333",
            "titleColor": "#F14A9C",
            "gridColor": "#D0D0D0",
        },
    )



# ==========================================
# 4. DATA LOADING
# ==========================================
# Loads the pre-cleaned Simpsons dataset into a Pandas DataFrame.
# Using Streamlit's @st.cache_data decorator ensures this file is only read 
# from the disk once. On subsequent dashboard interactions, it loads 
# instantly from memory, keeping the app highly performant
@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "simpsons_episodes_clean.csv")
    df = pd.read_csv(csv_path)
    return df

df = load_data()

# ==========================================
# 5. MAIN TITLE
# ==========================================
simpsons_title("The Simpsons viewer dashboard")

# ==========================================
# 6. SIDEBAR
# ==========================================
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/0/0d/Simpsons_FamilyPicture.png",
        width=200,
    )

with st.sidebar:
    #st.markdown("---")
    #st.markdown("### Key Metrics:")
    
    pink_subheader("🍩 Key Metrics:")
    st.metric("Total Episodes", len(df))
    st.metric("Average Rating", f"{df['imdb_rating'].mean():.1f}")
    st.metric("Average Viewers (M)", f"{df['us_viewers_in_millions'].mean():.1f}")



with st.sidebar:
    st.markdown("---")
    #st.markdown("### About:")
    pink_subheader("🍩 About:")
    st.write("**Author:** Alexis Vendrix")
    st.write("**Course:** Data Visualization MDS/MEI")
    st.write(
        "This dashboard answers analytical questions regarding the evolution of *The Simpsons* episodes' ratings and viewership over time in the US."
    )

x_var = 'season:O'
x_title = 'Season Number'


# ====================================================================================
# 7.1 FIRST ROW
# ====================================================================================
col_rate, col_correlation = st.columns(2,gap="large")

# ====================================================================================
# 7.1.1 Evolution of Rating
# ====================================================================================

# Design Decisions:

# Chart Choice (Boxplot vs. Line Chart): 
# Simply plotting the average rating per season via a standard line chart hides a lot of information in the data. 
# A Boxplot was chosen because it reveals the variance. 
# It allows the viewer to instantly see not just the median quality, 
# but the spread—proving whether a season was consistently average, 
# or a highly volatile mix of brilliant masterpieces and terrible flops.


# The trendline overlay: 
# The Donut Pink LOESS (Locally Estimated Scatterplot Smoothing) regression line was overlaid to guide the viewer's eye. 
# It cuts through the season-to-season noise to undeniably highlight the evolution of the ratings.

# Y-Axis Zooming (domain=[4, 10]): 
# Because The Simpsons IMDb ratings rarely drop below 4.0, we will zoom in on the Y-axis to make the variations more visible.
# This is justified by the article given in the class that states that: 
# "Moreover, existing guidelines for the design of line graphs
# and scatterplots focus on making the overall trend as visible
# (and decodable with the least error) as possible [7, 15, 35, 37].
# These optimizations to chart aspect ratio typically assume that
# the chart covers the range of the data, rather than necessarily
# beginning at 0."


# Color Strategy: 
# The chart uses a "Background/Foreground" cognitive hierarchy. 
# The Marge Blue boxplots act as the dense background data, while the thick, 
# bright Donut Pink line brings the analytical conclusion right to the front.



with col_rate:
    pink_subheader("IMDB Rating evolution over time")
    #st.markdown("*Comment:*")

    # Layer 1: The Boxplot (Distribution)
    # extent='min-max' forces the whiskers to show the absolute highest and lowest 
    # rated episodes of the season, rather than hiding them as statistical outliers.
    # The Y-axis is locked between 4 and 10 to prevent wasted empty space at the bottom.
    base_boxplot_ratings = alt.Chart(df).encode(
        x=alt.X(x_var, title=x_title,axis=alt.Axis(labelAngle=0))
    )
    bp_ratings = base_boxplot_ratings.mark_boxplot(extent='min-max', color='#009DDC').encode(
        y=alt.Y('imdb_rating:Q', title='IMDB Rating', scale=alt.Scale(domain=[4, 10]))
    )

    # Layer 2: The Trendline (Macro-Pattern)
    # transform_loess calculates a locally weighted polynomial regression.
    # This smooths out the season-to-season noise to show the true historical trend.
    trend_bp_ratings = base_boxplot_ratings.transform_loess(
        'season', 'imdb_rating'
    ).mark_line(color='#F14A9C', strokeWidth=3).encode(
        y='imdb_rating:Q'
    )

    # Combine and Configure: Layer the charts and apply global font sizing for readability.
    chart_r = (bp_ratings + trend_bp_ratings).properties(height=350).configure_axis(
    labelFontSize=16, # The numbers/ticks on the axes
    titleFontSize=18  # The main axis titles
    ).configure_legend(
        labelFontSize=16, # The text next to the color swatches
        titleFontSize=18  # The main legend title
    )
    
    st.altair_chart(chart_r, use_container_width=True)

# ====================================================================================
# 7.1.2 Correlation
# ====================================================================================
# 
# Design Decisions:

# Chart Choice (Scatter Plot): 
# To prove whether higher viewership correlates with higher rating, 
# a scatter plot is the definitive standard. It plots two continuous, quantitative variables against each other, 
# exposing the exact shape, direction, and density of the relationship.

# Overplotting mitigation (opacity=0.8): 
# With hundreds of episodes plotted in a confined space, data points inevitably overlap. 
# By setting the circle opacity to 80%, the chart utilizes visual density. When multiple episodes cluster in the same area, 
# the overlapping transparent blue dots multiply to create a deeper, darker blue hue, instantly showing the viewer where the heaviest concentration of data lies.

# The Regression line as a visual anchor: 
# While human eyes are decent at spotting general clusters, they are notoriously bad at estimating exact mathematical slopes. 
# The thick, Donut Pink regression line removes the guesswork. 
# It serves as an immediate visual summary of the calculated 'r' value, proving the exact trajectory of the relationship.

# In-Chart Annotation: 
# Instead of burying the Pearson correlation coefficient ($r$) in a paragraph of text below the chart, 
# it is embedded directly into the chart's canvas using mark_text. 
# This keeps the user's eyes completely focused on the data and visually ties the mathematical value (Pink text) directly to the physical line (Pink stroke).

# Rich, Formatted Tooltips: 
# Because scatter plots strip away the identity of the data points (turning episodes into anonymous dots), highly formatted tooltips were implemented. 
# This elevates the visualization from a static image to an interactive exploratory tool, allowing the user to hover over extreme outliers 
# and instantly discover exactly which episode caused the anomaly without looking at a raw data table.

 
with col_correlation:
    corr_value = df['us_viewers_in_millions'].corr(df['imdb_rating'])
    pink_subheader(f"Correlation between ratings and viewers")
    #st.markdown("*Comment:*")
    
    # Base Chart: Establish the X and Y axes that all subsequent layers will share.
    # Locking the Y-axis domain [4, 10] prevents empty space, as IMDb ratings rarely drop below 4.
    base_scatter = alt.Chart(df).encode(
        x=alt.X('us_viewers_in_millions:Q', title='Viewers (M)'),
        y=alt.Y('imdb_rating:Q', title='IMDB Rating', scale=alt.Scale(domain=[4, 10]))
    )
    # Layer 1: The Data Points (Scatter)
    # Opacity is set to 0.8 to handle "overplotting" (when dots stack on top of each other).
    # Custom tooltips are heavily formatted for a user-friendly hover experience.
    scatter_dots = base_scatter.mark_circle(size=60, opacity=0.8, color='#009DDC').encode(
        tooltip=[
            alt.Tooltip('title:N', title='Episode Title'),
            alt.Tooltip('season:O', title='Season #'),
            alt.Tooltip('number_in_season:O', title='Episode #'),
            alt.Tooltip('us_viewers_in_millions:Q', title='Viewers (M)', format='.2f'),
            alt.Tooltip('imdb_rating:Q', title='Rating'),
            alt.Tooltip('original_air_date:T', title='Aired On', format='%B %d, %Y')
            
        ]
    )
    
    # Layer 2: The Trendline
    # transform_regression automatically calculates and draws the line of best fit,
    # providing visual proof of the mathematical correlation.
    regression_line = base_scatter.transform_regression(
        'us_viewers_in_millions', 'imdb_rating'
    ).mark_line(color='#F14A9C', strokeWidth=3)

    # Layer 3: Dynamic Text Annotation Setup
    # Calculates the exact X/Y coordinates to place the 'r' value cleanly in the top right.
    text_df = pd.DataFrame({
        'x': [df['us_viewers_in_millions'].max()],
        'y': [9.5], 
        'label': [f"corr = {corr_value*100:.0f}%"]
    })
    
    # text mark with correlation value
    text_annotation = alt.Chart(text_df).mark_text(
        align='right',     # Aligns the text to the right so it doesn't get cut off
        fontSize=20,       # Make it nice and readable
        fontWeight='bold',
        color='#F14A9C'    # Donut pink to match the regression line!
    ).encode(
        x='x:Q',
        y='y:Q',
        text='label:N'
    )
    
    # Combine and Configure: Flatten all 3 layers and apply global font sizes
    chart3 = (scatter_dots + regression_line + text_annotation).properties(
        height=350, 
    ).configure_axis(
    labelFontSize=16, # The numbers/ticks on the axes
    titleFontSize=18  # The main axis titles
    ).configure_legend(
        labelFontSize=16, # The text next to the color swatches
        titleFontSize=18  # The main legend title
    )
    st.altair_chart(chart3, use_container_width=True)

# ====================================================================================
# 7.2 SECOND ROW
# ====================================================================================
col_view, col_weekday = st.columns(2,gap="large")

# ====================================================================================
# 7.2.1 Viewership evolution over time
# ====================================================================================

# Chart Choice (Dual-Metric Boxplot): 
# When analyzing viewership over multiple decades, averages are deceiving. 
# A single highly anticipated episode (like a season premiere or Super Bowl lead-in) 
# can heavily skew a season's average. Using a boxplot reveals the true spread of the data. 
# It allows the viewer to immediately see both the baseline viewership and the massive outlier events for each season.

# Grouped LOESS Trendlines: 
# Boxplots alone can look visually cluttered across all the seasons. 
# A locally weighted smoothing line (LOESS) was calculated and overlaid for each viewer type independently. 
# This cuts through the episode-to-episode noise to reveal the undeniable macro-narrative: the steep viewership decline during the late 90s, 
# followed by the stabilizing long tail.

# Methodological Transparency (Color Separation): 
# Television viewership measurement fundamentally changed during The Simpsons run, 
# shifting from measuring "Households" to "Individuals." 
# Rather than merging these incompatible metrics into one continuous line, the data was grouped and mapped to a monochromatic Teal color scale. 
# The shared hue communicates that both represent "viewership," but the distinct contrast honestly visually separates the two different measurement methodologies.

# In-Chart Legend Positioning: 
# To maximize the horizontal space available, the legend was moved inside the chart canvas (orient='top-right'). 
# This prevents the chart from being squeezed horizontally, ensuring the boxes remain wide enough to easily interpret.

with col_view:
    pink_subheader("Viewership evolution over time")
    st.markdown("*After Season 11, the measurement metric shifted from counting the total number of households to the number of individual people.*")

    # Layer 1: The Boxplots (Distribution)
    # Using extent='min-max' forces the whiskers to show the absolute highest and lowest 
    # viewed episodes, rather than calculating statistical outliers.
    base_boxplot_viewers = alt.Chart(df).encode(
        x=alt.X(x_var, title=x_title,axis=alt.Axis(labelAngle=0))
    )

    # Color encoding groups the data into 'Households' vs 'Individuals'
    bp_viewers = base_boxplot_viewers.mark_boxplot(extent='min-max').encode(
        y=alt.Y('us_viewers_in_millions:Q', title='Viewers (M)'),
        color=alt.Color(
            'viewers_type:N', 
            title='Viewers Type', 
            legend=alt.Legend(orient='top-right'),
            scale=alt.Scale(
                domain=['Household Viewers (Millions)', 'Individual Viewers (Millions)'],
                range=["#39989f", "#6ccbd2"]        
            )
        )
    )
    # Layer 2: The Trendlines (Macro-Pattern)
    # transform_loess calculates a smoothed regression line.
    # groupby=['viewers_type'] is crucial here: it tells Altair to calculate two separate 
    # trendlines (one for households, one for individuals) instead of mixing them together.
    trend_bp_viewers = base_boxplot_viewers.transform_loess(
        'season', 'us_viewers_in_millions', groupby=['viewers_type']
    ).mark_line(color='#F14A9C', strokeWidth=3).encode(
        y='us_viewers_in_millions:Q',
        detail='viewers_type:N'
    )

    # Combine and Configure: Layer the charts and apply global font sizing for readability.
    chart_v = (bp_viewers + trend_bp_viewers).properties(height=350
    ).configure_axis(
    labelFontSize=16, # The numbers/ticks on the axes
    titleFontSize=18  # The main axis titles
    ).configure_legend(
        labelFontSize=16, # The text next to the color swatches
        titleFontSize=18  # The main legend title
    )
    
    st.altair_chart(chart_v, use_container_width=True)



# ====================================================================================
# 7.2.2 Viewers by airing weekday
# ====================================================================================

# Chart Choice (Bar Chart): 
# For comparing aggregated, discrete categorical data (Days of the Week), 
# the vertical bar chart is the optimal choice. 
# The user can easily compare the lengths of rectangles aligned on a common baseline (0).

# Data filtering: 
# The raw dataset includes episodes aired on random weekdays with very weak occurrences (e.g., Tuesdays or Fridays). 
# However, including these days in a standard average comparison is statistically misleading. 
# A random Tuesday might have only two highly anticipated special episodes, falsely inflating its average above Sunday, 
# which has hundreds of standard episodes anchoring its baseline. 
# By deliberately filtering the dataset to only ['Thursday', 'Sunday'], 
# the chart presents an honest comparison of the show's true historical broadcast nights.

# Direct Data Labeling: 
# Rather than forcing the user's eye to dart back and forth horizontally between the tops of the bars 
# and the Y-axis to guess the values, the exact averages were embedded directly inside the bars. 
# By using a massive font, the visualization instantly proves the core narrative of the data: 
# Thursday's historical average viewership is definitively more than double Sunday's average.

# Tooltip: 
# While the massive data labels give the "quick answer", the tooltips were designed to include the count. 
# This provides technical transparency, allowing curious users to hover and 
# verify exactly how many episodes make up that average.


with col_weekday:

    # Data Transformation: Filter out anomalous days
    # We restrict the dataset to the primary broadcast nights. Other days contain 
    # rare special airings with mathematically misleading averages due to tiny sample sizes.
    main_days = ['Thursday', 'Sunday']
    df_main_days = df[df['weekday_name'].isin(main_days)]
    pink_subheader("Average number of viewers by airing weekday")
    #st.markdown("*Comment:*")

    # Categorical Sorting: Forcing chronological order instead of alphabetical
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Layer 1: The Base Bar Chart
    chart4_bar = alt.Chart(df_main_days).mark_bar(color="#2ec4b6").encode(
        x=alt.X('weekday_name:N', title=None, axis=alt.Axis(labelAngle=0), sort=weekday_order),
        y=alt.Y('mean(us_viewers_in_millions):Q', 
                #title='Avg Viewers (Millions)', 
                title=None,
                axis=alt.Axis(
                    labels=False,  # Hides the numbers
                    ticks=False,   # Hides the little tick marks
                    domain=False,  # Hides the solid vertical line on the left
                    grid=False      # Keeps the horizontal background lines!
                )),

        
        tooltip=[
            alt.Tooltip('weekday_name:N', title='Weekday'),
            alt.Tooltip('mean(us_viewers_in_millions):Q', title='Average viewers (M)', format='.2f'),
            alt.Tooltip('count():Q', title='Number of episodes') 
        ]
    )

    # Layer 2: Direct Data Labels
    base = alt.Chart(df_main_days).transform_aggregate(
    mean_viewers='mean(us_viewers_in_millions)',
    ep_count='count()',
    groupby=['weekday_name']
    ).transform_calculate(
        label_text="format(datum.mean_viewers, '.1f') + ' M'" 
    )

    chart4_text = base.mark_text(
        align="center",
        baseline="bottom",
        dy=72, 
        color="#FFFFFF",
        fontSize=48,
        fontWeight="bold"   
    ).encode(
        x=alt.X('weekday_name:N', sort=weekday_order),
        y=alt.Y('mean_viewers:Q'),
        text=alt.Text('label_text:N')
    )


    # Combine and Configure: Layer the bars and text, apply global font sizing  
    final_bar_chart=(chart4_bar + chart4_text).properties(height=400
    ).configure_axis(
    labelFontSize=16, # The numbers/ticks on the axes
    titleFontSize=18  # The main axis titles
    ).configure_legend(
        labelFontSize=16, # The text next to the color swatches
        titleFontSize=18  # The main legend title
    )
    st.altair_chart(final_bar_chart, use_container_width=True)

# ====================================================================================
# 7.3 THIRD ROW
# ====================================================================================

# ====================================================================================
# 7.3.1 Viewership Patterns per Season
# ====================================================================================

# Design decision - Heatmap and line chart combination: 
# While heatmaps are exceptional at revealing local maximums and minimums, 
# human visual processing struggles to calculate a rate of change across a color gradient. 
# Relying solely on the heatmap forces the user to mentally average the color shifts left-to-right to guess the seasonal momentum, 
# creating an unnecessarily high cognitive load.
# To solve this, a linear regression slope was calculated for each season and explicitly displayed alongside the data. 
# Instead of implicitly asking the user to guess if a season was generally gaining or losing viewers based on fading colors, 
# the trend column provides a definitive, quantitative answer.

# Micro vs. Macro Analysis: 
# This composite layout bridges two levels of analysis. 
# The heatmap provides the "Micro" view (exposing episode-to-episode volatility and specific outlier events), 
# while the calculated trend column provides the "Macro" view (proving the overall audience trajectory from the premiere to the finale).

# Diverging Color Signals: 
# To make the trend instantly readable, a strict categorical color condition was applied to the text (Teal for positive growth, Pink for audience bleed). 
# This allows stakeholders to scan the right-hand column in seconds and immediately identify which seasons successfully retained their audience 
# without having to read every specific number.


pink_subheader("Viewership patterns per season")
st.markdown("*The trend represents the average change in viewers (in millions) per episode in a season*")

# 1. Composite Layout Setup
# Using Streamlit columns instead of Altair's hconcat bypasses Vega-Lite's rigid width 
# constraints, allowing the heatmap to stretch fluidly while the trend column stays tight.
col_trend, col_heat = st.columns([1.5, 15], gap="small")

# --- LEFT COLUMN: TREND INDICATOR & Y-AXIS ---
with col_trend:
    # Isolate one row per season to prevent text overplotting
    unique_trend_df = df[['season', 'trend_slope']].drop_duplicates(subset=['season'])
    unique_trend_df['trend_slope'] = unique_trend_df['trend_slope']

    # Text Chart Construction
    trend_chart = alt.Chart(unique_trend_df).mark_text(fontWeight='bold', align='center',fontSize=16).encode(
        y=alt.Y('season:O', sort='descending', title='Season number'), 
        
        # The fake X-axis to keep it aligned with the heatmap
        x=alt.X('dummy:O', title='Trend', axis=alt.Axis(
            labels=True,              
            labelColor='transparent', 
            ticks=True,               
            tickColor='transparent',  
            domain=False              
        )),
        # Diverging color logic: Teal for positive growth, Pink for audience decrease
        text=alt.Text('trend_slope:Q', format='+.2f'), 
        color=alt.condition(
            alt.datum.trend_slope > 0,
            alt.value("#2ec4b6"), 
            alt.value("#F14A9C")  
        ),
        tooltip=[
            alt.Tooltip('trend_slope:Q', title='Total Viewers Changed', format='+.2f')
        ]
    ).transform_calculate(
        dummy="' '" 
    ).properties(
        height=alt.Step(18) # Locks the physical row height so it matches the heatmap
    ).configure_axis( 
    labelFontSize=16, # The numbers/ticks on the axes
    titleFontSize=18  # The main axis titles
    )
    
    st.altair_chart(trend_chart, use_container_width=True)

# --- RIGHT COLUMN: THE HEATMAP ---
with col_heat:
    # Heatmap Chart Construction
    chart5 = alt.Chart(df).mark_rect().encode(
        x=alt.X('number_in_season:O', title='Episode number', axis=alt.Axis(labelAngle=0)),

        # Y-axis is disabled here because the left column acts as the master Y-axis
        y=alt.Y('season:O', axis=None, sort='descending'),
        color=alt.Color('us_viewers_in_millions:Q', title='Viewers (M)',
            scale=alt.Scale(scheme='inferno', reverse=True),
        ),
        tooltip=[
            alt.Tooltip('season:N', title='Season number'),
            alt.Tooltip('number_in_season:N', title='Episode number'),
            alt.Tooltip('us_viewers_in_millions:Q', title='Viewers (M)', format='.2f'),
            alt.Tooltip('title:N', title='Episode Title') 
        ]
    ).properties(height=alt.Step(18)# Mathematical guarantee that rows align with the left column
    ).configure_axis(
    labelFontSize=16, # The numbers/ticks on the axes
    titleFontSize=18  # The main axis titles
    ).configure_legend(
        labelFontSize=16, # The text next to the color swatches
        titleFontSize=18  # The main legend title
    )
    
    st.altair_chart(chart5, use_container_width=True)

