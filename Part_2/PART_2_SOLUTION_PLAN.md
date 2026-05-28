# Part_2 Solution Plan: Simpsons Character Dialogue Analytics

## Project Overview

Part_2 extends Part_1 by analyzing **character dialogue patterns** across episodes and seasons. Instead of episode ratings and viewership, we're exploring which characters speak the most, how their speech volume evolves, and comparing dialogue between character pairs. This requires **interactive visualizations** with **cross-filtering** to enable exploratory analysis.

## Core Questions & Visualization Strategy

### **Question 1: Character Word Distribution**
*"What are the characters that issue more words, and how are the word numbers distributed?"*

**Visualization Choice: Horizontal Bar Chart + Summary Stats**
- **Why**: A sorted bar chart quickly reveals the top speakers and word count ranges
- **Design**:
  - Y-axis: Character names (sorted descending by word count)
  - X-axis: Total word count (log scale optional to show range)
  - Color: Consistent character color mapping (reuse across all charts)
  - Top 15-20 characters to avoid clutter
- **Interaction**: Click/hover on bar → highlights character across all charts (cross-selection)
- **Alternative considered**: Treemap (rejected - harder to compare exact values)

### **Question 5: Character Sentence Distribution** 
*"Same as Q1 but regarding sentences, not words"*

**Visualization Choice: Horizontal Bar Chart (parallel to Q1)**
- Mirror of Q1 but for sentence counts
- Same color scheme for character consistency
- Reveals speaking frequency patterns (more sentences = more frequent speaker; fewer sentences/more words per sentence = longer-winded character)
- Place side-by-side with Q1 for easy comparison

**Layout Strategy**: Dual bar charts (top of dashboard) - establishes character identity and comparative hierarchy

---

### **Question 2: Character Evolution Over Time**
*"How have the word numbers among the characters evolved throughout the available seasons?"*

**Visualization Choice: Multi-line Chart with Season Slider**
- **Why**: Line charts show temporal trends; multiple lines compare several characters
- **Design**:
  - X-axis: Season number (continuous)
  - Y-axis: Total words per season
  - Line per character (limited to top 5-8 speakers to avoid spaghetti)
  - Color: Consistent with character colors from Q1
  - Opacity: Filtered characters appear ghosted/faded
- **Interaction**: 
  - Season slider (alt.binding_range) at top to filter data dynamically
  - Character selection via click on legend items
  - Selecting character in Q1 bar chart → auto-highlights that line
- **Alternative considered**: Small multiples (rejected - inefficient space, can't compare easily)
- **Improvement**: LOESS smoothing to show trend through noise

---

### **Question 3: Character Pair Comparison (Per Season & Episode)**
*"Compare word distribution for a pair of characters, for a selected season and episode"*

**Visualization Choice: Dual Side-by-Side Layouts**

#### **3a) Season-level Comparison: Grouped Bar Chart**
- **Design**:
  - X-axis: Episode number within season
  - Y-axis: Word count
  - Two bars per episode (one per character)
  - Color: One color per character
  - Season selector dropdown (alt.binding_select)
- **Interaction**:
  - Dropdown to select season
  - Character selection updates which pair is shown
  - Selecting two characters triggers this view

#### **3b) Episode-level Comparison: Detailed View**
- **Design**:
  - Single episode, specific comparison breakdown
  - Text or small table showing: character name, word count, sentence count, avg words/sentence
  - Episode selector: slider or dropdown
- **Interaction**: 
  - Season selection filters available episodes
  - Episode selection populates detailed stats

**Cross-interaction**: Selecting characters in Q1 or hovering in Q2 → auto-populates comparison view

---

### **Question 4: Episode-Level Comparison** 
*"Compare word distribution over a concrete episode"*

**Visualization Choice: Stacked Bar Chart + Detailed Breakdown**
- **Design**:
  - X-axis: Seasons (or selected episode range)
  - Y-axis: Stacked word count per character
  - Color-coded by character
  - Top 8-10 characters (others grouped as "Other")
- **Interaction**:
  - Hover over segment → highlight that character across all charts
  - Legend click → include/exclude character from stack
- **Alternative considered**: 100% stacked bar (rejected - absolute counts matter more than proportions here)

---

## Data Structure & Feature Engineering

### **Required Columns**
```
season          (int)
episode_num     (int)
character_name  (string)
word_count      (int)
sentence_count  (int)
```

### **Computed Features**
```
words_per_sentence = word_count / sentence_count
total_words_per_character = sum(word_count) grouped by character
total_sentences_per_character = sum(sentence_count) grouped by character
words_per_season_per_character = sum grouped by (season, character)
```

### **Data Cleaning Considerations**
- Remove/consolidate character name variations (e.g., "Homer", "Homer Simpson", "Homer Jay Simpson")
- Handle missing/null values (filter out episodes with incomplete dialogue data)
- Possibly merge minor characters with < 20 total words into "Other" for cleaner visualizations
- Normalize spacing/punctuation in dialogue data

---

## Interaction Patterns (Inspired by Tutorial)

### **1. Cross-Selection (Primary)**
A **single character selection** state shared across all charts:
```python
character_select = alt.selection_point(
    fields=['character_name'],
    bind=alt.binding_radio(options=..., name='Character:'),  # or dropdown
    empty=False
)

# All charts use:
color = alt.condition(character_select, 
                      alt.Color('character_name:N'), 
                      alt.value('lightgray'))
```

**Effect**: Selecting "Homer" highlights Homer in Q1, Q2, Q5 bars; activates comparison mode for Q3/Q4

### **2. Multi-Selection for Pair Comparison**
Secondary parameter for two-character pair:
```python
character_pair = alt.selection_point(
    fields=['character_name'],
    bind=... # Allow clicking on legend to select pair
)
```

### **3. Slider-Based Filters**
- **Season slider** (Q2, Q3a): `alt.binding_range(min=1, max=34, step=1)`
- **Episode slider** (Q3b, Q4): `alt.binding_range(min=1, max=730, step=1)`

### **4. Dropdown Menus** (Optional)
- Character selection dropdown (alternative to radio buttons if space-constrained)
- Season/Episode selectors (alternative to sliders)

---

## Dashboard Layout (Streamlit Single-Page)

```
┌─────────────────────────────────────────────────────────┐
│  TOP SECTION: CHARACTER IDENTITY                        │
│ ┌──────────────────┬──────────────────────────────────┐ │
│ │ Q1: Top 20       │ Q5: Top 20 Characters by        │ │
│ │ Characters by    │ Sentence Count (parallel view)  │ │
│ │ Word Count       │                                  │ │
│ │ (Sorted bar)     │ Reveals: "Chatty vs Quiet"      │ │
│ └──────────────────┴──────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ CHARACTER SELECTOR (Radio buttons or dropdown)           │
│ ▯ Homer  ▯ Marge  ▯ Bart  ▯ Lisa  ▯ Maggie  ...        │
├─────────────────────────────────────────────────────────┤
│ MIDDLE SECTION: TEMPORAL & COMPARATIVE ANALYSIS         │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ Q2: Character Evolution Over Seasons                │ │
│ │ (Multi-line chart, top 5-8 chars)                   │ │
│ │ [Slider: Season ▬▬●▬▬ 15]                           │ │
│ └──────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ COMPARISON SECTION (Triggered by character selection)   │
│ ┌──────────────────┬──────────────────────────────────┐ │
│ │ Q3a: Season Pair │ Q3b: Episode Stats               │ │
│ │ Comparison       │ [Slider: Episode ▬▬●▬▬]         │ │
│ │ (Grouped bars)   │                                  │ │
│ │ [Dropdown: S15]  │ Character 1: W=3400, S=250 ...  │ │
│ └──────────────────┴──────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ BOTTOM SECTION: FULL DIALOGUE LANDSCAPE                 │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ Q4: Stacked Bar Chart (All Seasons + Top Characters)│ │
│ │ Shows: Dialogue dominance per season over time      │ │
│ └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Rationale**:
- **Top**: Establishes *what* (character identity)
- **Middle**: Shows *when* (temporal evolution)
- **Comparison**: Enables *comparison* between specific characters
- **Bottom**: Provides *context* (overall dialogue landscape)
- All charts are **vertically stacked** to minimize scrolling (≤2x screen height)

---

## Color & Design Consistency

### **Character Color Scheme**
Assign **fixed colors** to top characters (consistent across all charts):
- Homer: #FDB750 (yellow - iconic)
- Marge: #00F502 (green - hair)
- Bart: #FF7F00 (orange)
- Lisa: #FF1493 (pink/magenta)
- Mr. Burns: #8B0000 (dark red)
- Moe: #6495ED (cornflower blue)
- Ned: #DAA520 (goldenrod)
- *Others*: Gray or pastel palette

**Why**: Reusing character colors across visualizations creates **instant cognitive recognition** (e.g., "yellow always means Homer")

### **Interaction Visual Feedback**
- **Selected characters**: Full opacity, bold
- **Unselected characters**: Gray, 0.2 opacity
- **Hover/mouseover**: Tooltip with exact counts

---

## Technical Implementation Notes

### **Altair Techniques to Leverage**
1. **`alt.selection_point()`** with `fields=['character_name']` → cross-chart highlighting
2. **`alt.condition()`** → opacity/color changes based on selection
3. **`alt.binding_range()`, `alt.binding_radio()`, `alt.binding_select()`** → UI controls
4. **`transform_filter()`** → filter data based on slider/dropdown values
5. **`transform_aggregate()`** → group by character, season, episode
6. **Layered charts** → combine bars with lines (e.g., trend overlay)
7. **`alt.hconcat()`, `alt.vconcat()`** → arrange side-by-side and stacked

### **Streamlit Integration**
- Load cleaned CSV once at app startup
- Each visualization reads from same dataframe
- Use `st.title()`, `st.markdown()` for section headers
- Display design rationale (200 words per question) in expandable sections (`st.expander()`)
- Add "About" section with author name

---

## Expected Data Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| **Sparse dialogue data** (some episodes missing character data) | Filter episodes with null character_name or word_count |
| **Character name variants** | Normalize in cleaning script (e.g., "Homer Simpson" → "Homer") |
| **Too many minor characters** (1000+ unique names) | Merge characters with <50 total words into "Other" category |
| **Uneven data distribution** (some characters speak 10x more than others) | Use log scale for word count axis if needed; separate views for top vs rest |
| **Interaction bloat** (too many sliders/dropdowns) | Limit to 2-3 primary selectors; auto-populate secondary views from primary selection |

---

## Implementation Roadmap

1. **Data Cleaning** (Offline, no notebook required per spec)
   - Extract character, word count, sentence count per episode
   - Normalize character names
   - Generate aggregates (per-character totals, per-season per-character)

2. **Jupyter Notebook** (Design & Exploration)
   - Implement each visualization (Q1, Q2, Q3a/b, Q4, Q5)
   - Test interactions on small subsets
   - Document design decisions (200 words per visualization)
   - Screenshot final versions for reference

3. **Streamlit App** (Production)
   - Assemble all charts with shared character selection
   - Connect UI controls (sliders, dropdowns, radio buttons)
   - Verify cross-interactions work as expected
   - Optimize performance (pre-aggregate data, filter before chart rendering)

---

## Success Criteria

✅ **Functionality**:
- All 5 questions answerable via visualization
- Character selection triggers updates in ≥3 other charts (cross-interaction requirement)
- No blank/NaN charts from filter interactions

✅ **Design**:
- Character colors consistent across all views
- Single page with minimal scrolling
- 200-word design rationale per visualization

✅ **Robustness**:
- Default values sensible (e.g., slider starts at Season 10, defaults to top 8 characters)
- No hard-coded filenames; works with relative paths
- Streamlit app runs with `streamlit run app_name.py` without errors

---

## Extra Features (Optional, for Higher Marks)

- **Search box** (inspired by Gapminder tutorial): Search for character by name
- **Timeline animation**: Play through seasons automatically (Streamlit slider update)
- **Word cloud per character**: Show most common words spoken by selected character
- **Dialogue heatmap**: Seasons vs characters (like Part_1 viewership heatmap)
- **Episode details**: Click on bar → popover with episode name, date, character script count
- **Summary stats**: Display global KPIs (total words, total episodes, top character, etc.)

