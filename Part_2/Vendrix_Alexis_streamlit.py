"""
The Simpsons: Character Dialogue Analytics - Part 2
Author: Alexis Vendrix
Date: May 31 2026

Interactive exploration of character dialogue patterns across episodes and seasons.
"""

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# ============================================================================
# 1. PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Simpsons Dialogue Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 2. CUSTOM FUNCTIONS
# ==========================================
# Custom functions to render titles with CSS - same as part 1


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


# ============================================================================
# CUSTOM THEME & COLORS
# ============================================================================
@alt.theme.register("simpsons_dialogue", enable=True)
def simpsons_dialogue_theme():
    return alt.theme.ThemeConfig(
        view={"stroke": "transparent"},
        range={
            "category": [
                "#FFD90F",
                "#009DDC",
                "#F14E28",
                "#FF69B4",
                "#93C47D",
                "#493D26",
                "#445491",
                "#709139",
                "#EEDAB0",
                "#32499F",
            ],
        },
        title={
            "font": "sans-serif",
            "color": "#333333",
            "fontSize": 18,
            "anchor": "start",
        },
        axis={
            "labelColor": "#333333",
            "titleColor": "#333333",
            "gridColor": "#D0D0D0",
            "labelFontSize": 12,
            "titleFontSize": 14,
        },
    )


character_colors = {
    "Homer Simpson": "#FFD90F",
    "Marge Simpson": "#009DDC",
    "Bart Simpson": "#F14E28",
    "Lisa Simpson": "#FF69B4",
    "C. Montgomery Burns": "#93C47D",
    "Moe Szyslak": "#493D26",
    "Seymour Skinner": "#445491",
    "Ned Flanders": "#709139",
    "Grampa Simpson": "#EEDAB0",
    "Chief Wiggum": "#32499F",
}


# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def load_data():
    dialogue_cleaned = pd.read_csv("Part_2/dialogue_cleaned.csv")
    dialogue_cleaned["season"] = dialogue_cleaned["season"].astype(int)
    dialogue_cleaned["number_in_season"] = dialogue_cleaned["number_in_season"].astype(
        int
    )
    # Derive timestamp_sec from timestamp_in_ms if not already exported
    if "timestamp_sec" not in dialogue_cleaned.columns:
        dialogue_cleaned["timestamp_sec"] = (
            (dialogue_cleaned["timestamp_in_ms"] / 1000).round(0).astype(int)
        )
    return dialogue_cleaned


dialogue_cleaned = load_data()

# Aggregate statistics
character_stats = (
    dialogue_cleaned.groupby("raw_character_text")
    .agg({"word_count": "sum", "sentence_count": "sum", "episode_id": "nunique"})
    .reset_index()
)
character_stats.columns = [
    "character_name",
    "total_words",
    "total_sentences",
    "episodes_appeared",
]
character_stats["words_per_sentence"] = (
    character_stats["total_words"] / character_stats["total_sentences"]
).round(2)
character_stats = character_stats.sort_values("total_sentences", ascending=False)

top_characters = character_stats["character_name"].head(10).tolist()


# ==========================================
# 5. MAIN TITLE
# ==========================================
simpsons_title("The Simpsons dialogue dashboard")


# ============================================================================
# SIDEBAR: word counts/sentence count swich, about, author
# ============================================================================
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/0/0d/Simpsons_FamilyPicture.png",
        width=200,
    )
    st.markdown("---")


with st.sidebar:
    pink_subheader("Select a metric:")
    # 2. Metric Selection UI
    metric_choice = st.radio(
        "Switch between total words spoken or number of speaking lines",
        ["Word Count", "Sentence Count"],
        horizontal=True,
        # help="Switch between total words spoken or number of speaking lines",
    )

with st.sidebar:
    st.markdown("---")
    # st.markdown("### About:")
    pink_subheader("🍩 About:")
    st.write("**Author:** Alexis Vendrix")
    st.write("**Course:** Data Visualization MDS/MEI")
    st.write(
        "This dashboard explores the dialogue of *The Simpsons*: who speaks the most, "
        "how each character's word count evolves across seasons, and how two characters "
        "compare within a chosen season, episode, and even moment-by-moment within an episode."
    )


# ============================================================================
# QUESTION 1 & 2: TOGGLE BETWEEN WORD & SENTENCE COUNT
# ============================================================================
pink_subheader("Character Dialogue Distribution & Evolution")

character_select = alt.selection_point(
    name="char_select",
    fields=["character_name"],
    on="click",
    toggle="true",
    value=None,
)

# Dynamic Logic based on UI selection
if metric_choice == "Word Count":
    x_col, agg_col, title_label = "total_words", "word_count", "Words Spoken"
else:
    x_col, agg_col, title_label = "total_sentences", "sentence_count", "Speaking Lines"

# Shared Color Scale to keep charts consistent
color_scale = alt.Scale(
    domain=list(character_colors.keys()), range=list(character_colors.values())
)

# --- CHART 1: BAR CHART ---
chart_data_q1 = character_stats[
    character_stats["character_name"].isin(top_characters)
].sort_values(x_col, ascending=False)

chart_q1 = (
    alt.Chart(chart_data_q1)
    .mark_bar()
    .encode(
        y=alt.Y("character_name:N", sort="-x", title=None),
        x=alt.X(f"{x_col}:Q", title=title_label),
        color=alt.Color("character_name:N", scale=color_scale, legend=None),
        opacity=alt.condition(character_select, alt.value(1), alt.value(0.3)),
        tooltip=["character_name:N", f"{x_col}:Q"],
    )
    .add_params(character_select)
    .properties(height=400, title="Top 10 characters")
)

col_q1, col_q2 = st.columns([2, 3])

with col_q1:
    q1_event = st.altair_chart(
        chart_q1,
        use_container_width=True,
        on_select="rerun",
        key="q1_chart",
    )

try:
    selected_q1 = [
        p.get("character_name")
        for p in q1_event.selection.get("char_select", [])
        if p.get("character_name")
    ]
except AttributeError:
    selected_q1 = []

# --- CHART 2: TIME SERIES ---
char_season_data = (
    dialogue_cleaned[dialogue_cleaned["raw_character_text"].isin(top_characters)]
    .groupby(["season", "raw_character_text"])[agg_col]
    .sum()
    .reset_index()
    .rename(columns={"raw_character_text": "character_name", agg_col: "value"})
)

base_q2 = alt.Chart(char_season_data).encode(
    x=alt.X("season:Q", title="Season", axis=alt.Axis(format="d")),
    y=alt.Y("value:Q", title=title_label),
    color=alt.Color("character_name:N", scale=color_scale, legend=None),
)

# Opacity reacts to whatever was selected in chart_q1
if selected_q1:
    line_opacity = alt.condition(
        alt.FieldOneOfPredicate(field="character_name", oneOf=selected_q1),
        alt.value(1),
        alt.value(0.1),
    )
else:
    line_opacity = alt.value(1)

line_chart = base_q2.mark_line(point={"size": 60}).encode(
    opacity=line_opacity,
    tooltip=["character_name:N", "season:Q", "value:Q"],
)

chart_q2 = line_chart.properties(
    height=400,
    title=f"{title_label} over seasons - click on a character of the bar chart to have a focused view",
)

with col_q2:
    st.altair_chart(chart_q2, use_container_width=True)

st.markdown("---")


# ============================================================================
# QUESTION 3: EPISODE HEATMAP + CHARACTER PAIR COMPARISON
# ============================================================================
pink_subheader(
    f"Comparison of {title_label} between two characters for a specific episode"
)

# Per-episode totals across all characters
episode_totals = (
    dialogue_cleaned.groupby(["season", "number_in_season"])[agg_col]
    .sum()
    .reset_index()
    .rename(columns={agg_col: "total"})
)
episode_totals["label"] = episode_totals.apply(
    lambda r: f"s{int(r['season']):02d}e{int(r['number_in_season']):02d}", axis=1
)

# Altair selection bound to a click on a heatmap cell
episode_select = alt.selection_point(
    name="episode_select",
    fields=["season", "number_in_season"],
    on="click",
    toggle=False,
    empty=False,
    value=[{"season": 1, "number_in_season": 1}],
)

# Square cell sizing
cell_size = 24
n_seasons = int(episode_totals["season"].nunique())
max_episode = int(episode_totals["number_in_season"].max())
chart_width = max_episode * cell_size
chart_height = n_seasons * 1.3 * cell_size


base_q5 = alt.Chart(episode_totals).encode(
    x=alt.X(
        "number_in_season:O",
        title="Episode # in Season",
        axis=alt.Axis(labelAngle=0),
    ),
    y=alt.Y("season:O", title="Season", sort="ascending"),
)

heatmap_rect = (
    base_q5.mark_rect(stroke="#FFFEF9", strokeWidth=1)
    .encode(
        color=alt.Color(
            "total:Q",
            title=title_label,
            scale=alt.Scale(scheme="yelloworangered"),
            legend=alt.Legend(orient="right", gradientLength=200),
        ),
        opacity=alt.condition(episode_select, alt.value(1.0), alt.value(0.7)),
        tooltip=[
            alt.Tooltip("season:O", title="Season"),
            alt.Tooltip("number_in_season:O", title="Episode"),
            alt.Tooltip("total:Q", title=title_label, format=","),
        ],
    )
    .add_params(episode_select)
)


heatmap_highlight = base_q5.mark_rect(
    fill=None, stroke="#000000", strokeWidth=2.5
).transform_filter(episode_select)

heatmap = (heatmap_rect + heatmap_highlight).properties(
    width=chart_width,
    height=chart_height,
    title=[
        "Select an episode on the heatmap representing",
        f"the total {title_label} per episode",
    ],
)

# Layout: heatmap on the left, character picker + drill-down bar chart on the right
col_heat, col_right = st.columns([1, 1.5])

# Render the character pickers first (visually on the right) so values are available
# for the drill-down section below.
with col_right:
    st.markdown("**select two characters**")
    sub_a, sub_b = st.columns(2)
    with sub_a:
        char_a = st.selectbox(
            "Character A",
            top_characters,
            index=0,
            key="q5_char_a",
        )
    with sub_b:
        # Exclude whoever is selected as Character A from the B options
        b_options = [c for c in top_characters if c != char_a]
        # Keep the previous Character B selection if it's still available,
        # otherwise default to the first remaining character
        prev_b = st.session_state.get("q5_char_b")
        default_b_idx = b_options.index(prev_b) if prev_b in b_options else 0
        char_b = st.selectbox(
            "Character B",
            b_options,
            index=default_b_idx,
            key="q5_char_b",
        )
    heatmap_chars = [char_a, char_b]

with col_heat:
    heatmap_event = st.altair_chart(
        heatmap,
        use_container_width=False,
        on_select="rerun",
        key="q5_heatmap",
    )

with col_right:
    # Pull out the clicked cell (if any); fall back to s01e01 on first load
    selected_points = []
    try:
        selected_points = heatmap_event.selection.get("episode_select", [])
    except AttributeError:
        selected_points = []

    if selected_points:
        point = selected_points[0]
        sel_season = int(point.get("season"))
        sel_episode = int(point.get("number_in_season"))
    else:
        sel_season, sel_episode = 1, 1
        st.caption("Showing **s01e01** by default — click any cell to change.")

    if char_a == char_b:
        st.info("Pick two different characters to compare.")
    else:

        drill_data = (
            dialogue_cleaned[
                (dialogue_cleaned["season"] == sel_season)
                & (dialogue_cleaned["number_in_season"] == sel_episode)
                & (dialogue_cleaned["raw_character_text"].isin(heatmap_chars))
            ]
            .groupby("raw_character_text")[agg_col]
            .sum()
            .reset_index()
            .rename(columns={"raw_character_text": "character_name", agg_col: "value"})
        )

        # Ensure both characters appear even if one has 0 lines in this episode
        drill_data = (
            pd.DataFrame({"character_name": heatmap_chars})
            .merge(drill_data, on="character_name", how="left")
            .fillna({"value": 0})
        )

        # ============================================================================
        # QUESTION 3a: Season comparison
        # ============================================================================
        season_drill_data = (
            dialogue_cleaned[
                (dialogue_cleaned["season"] == sel_season)
                & (dialogue_cleaned["raw_character_text"].isin(heatmap_chars))
            ]
            .groupby("raw_character_text")[agg_col]
            .sum()
            .reset_index()
            .rename(columns={"raw_character_text": "character_name", agg_col: "value"})
        )
        season_drill_data = (
            pd.DataFrame({"character_name": heatmap_chars})
            .merge(season_drill_data, on="character_name", how="left")
            .fillna({"value": 0})
        )

        chart_q3_season = (
            alt.Chart(season_drill_data)
            .mark_bar()
            .encode(
                x=alt.X("character_name:N", title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("value:Q", title=title_label),
                color=alt.Color(
                    "character_name:N",
                    scale=alt.Scale(
                        domain=list(character_colors.keys()),
                        range=list(character_colors.values()),
                    ),
                    legend=None,
                ),
                tooltip=[
                    alt.Tooltip("character_name:N", title="Character"),
                    alt.Tooltip("value:Q", title=title_label, format=","),
                ],
            )
            .properties(
                height=250,
                title=f"Season {sel_season}",
            )
        )

        # ============================================================================
        # QUESTION 3b: Episode comparison
        # ============================================================================
        chart_q5 = (
            alt.Chart(drill_data)
            .mark_bar()
            .encode(
                x=alt.X("character_name:N", title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("value:Q", title=title_label),
                color=alt.Color(
                    "character_name:N",
                    scale=alt.Scale(
                        domain=list(character_colors.keys()),
                        range=list(character_colors.values()),
                    ),
                    legend=None,
                ),
                tooltip=[
                    alt.Tooltip("character_name:N", title="Character"),
                    alt.Tooltip("value:Q", title=title_label, format=","),
                ],
            )
            .properties(
                height=250,
                title=f"Episode S{sel_season:02d}E{sel_episode:02d}",
            )
        )

        col_season, col_episode = st.columns(2)
        with col_season:
            st.altair_chart(chart_q3_season, use_container_width=True)
        with col_episode:
            st.altair_chart(chart_q5, use_container_width=True)

        # ── Timeline within the selected episode (detail + brush overview) ──
        timeline_data = (
            dialogue_cleaned[
                (dialogue_cleaned["season"] == sel_season)
                & (dialogue_cleaned["number_in_season"] == sel_episode)
                & (dialogue_cleaned["raw_character_text"].isin(heatmap_chars))
            ]
            .groupby(["timestamp_sec", "raw_character_text"], as_index=False)
            .agg(
                **{
                    agg_col: (agg_col, "sum"),
                    "spoken_words": (
                        "spoken_words",
                        lambda s: " / ".join(s.dropna().astype(str)),
                    ),
                }
            )
            .rename(columns={"raw_character_text": "character_name"})
        )

        timeline_data["time_label"] = timeline_data["timestamp_sec"].apply(
            lambda s: f"{int(s) // 60}min {int(s) % 60:02d}sec"
        )
        # Small horizontal shift per character so grouped bars sit side by side
        # on the quantitative time axis (overlap would occur at the same second)
        char_offsets = {char_a: -0.4, char_b: 0.4}
        timeline_data["x_pos"] = timeline_data["timestamp_sec"] + timeline_data[
            "character_name"
        ].map(char_offsets).fillna(0)

        if not timeline_data.empty:
            timeline_brush = alt.selection_interval(encodings=["x"])

            color_enc = alt.Color(
                "character_name:N",
                scale=alt.Scale(
                    domain=list(character_colors.keys()),
                    range=list(character_colors.values()),
                ),
                legend=None,
            )

            # Format axis labels as "Xmin Ysec" via Vega expression
            time_label_expr = (
                "floor(datum.value/60) + 'min ' + "
                "(datum.value%60 < 10 ? '0' : '') + (datum.value%60) + 'sec'"
            )

            x_domain = [
                float(timeline_data["timestamp_sec"].min()) - 1,
                float(timeline_data["timestamp_sec"].max()) + 1,
            ]

            detail = (
                alt.Chart(timeline_data)
                .mark_bar(size=4)
                .encode(
                    x=alt.X(
                        "x_pos:Q",
                        title="Time in episode",
                        scale=alt.Scale(domain=timeline_brush, nice=False),
                        axis=alt.Axis(
                            labelExpr=time_label_expr,
                            labelOverlap="greedy",
                            labelAngle=-40,
                        ),
                    ),
                    y=alt.Y(f"{agg_col}:Q", title=title_label, stack=None),
                    color=color_enc,
                    tooltip=[
                        alt.Tooltip("time_label:N", title="Time"),
                        alt.Tooltip("character_name:N", title="Character"),
                        alt.Tooltip("spoken_words:N", title="Spoken words"),
                        alt.Tooltip(f"{agg_col}:Q", title=title_label, format=","),
                    ],
                )
                .properties(
                    height=160,
                    title=f"{title_label} over time — brush the strip below to zoom",
                )
            )

            # Lower (overview) — rug of ticks marking where dialogue happens
            # acts purely as the brush anchor below the detail chart
            overview = (
                alt.Chart(timeline_data)
                .mark_tick(thickness=1, color="#666666", opacity=0.6)
                .encode(
                    x=alt.X(
                        "timestamp_sec:Q",
                        title=None,
                        scale=alt.Scale(domain=x_domain, nice=False),
                        axis=alt.Axis(labels=False, ticks=False),
                    ),
                )
                .add_params(timeline_brush)
                .properties(height=18)
            )

            timeline_chart = alt.vconcat(detail, overview, spacing=4).resolve_scale(
                x="independent"
            )
            st.altair_chart(timeline_chart, use_container_width=True)
        else:
            st.caption("No per-minute dialogue data for this episode.")

# st.markdown("---")
