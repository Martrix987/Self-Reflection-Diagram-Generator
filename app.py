"""Self-Reflection Diagram Generator.

Step 1 scaffold:
- Base Streamlit layout and page configuration.
- Sidebar navigation for chart generator sections.
- Placeholder routing blocks for each visualization mode.
"""

import hashlib
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# Navigation options shown in the sidebar.
NAV_OPTIONS = [
    "🕸️ RPG Skill Tree (Radar)",
    "🌊 Time River (Sankey)",
    "🟩 Consistency Heatmap",
]

# Default skills shown when the app is opened for the first time.
DEFAULT_RPG_SKILLS = []

TIME_RIVER_ROOT = "Total Week (168)"

# Starter rows for the weekly time flow editor.
DEFAULT_TIME_RIVER_ROWS = [
    {"Source": TIME_RIVER_ROOT, "Target": "Sleep", "Hours": 56},
    {"Source": TIME_RIVER_ROOT, "Target": "Awake", "Hours": 112},
    {"Source": "Awake", "Target": "Work", "Hours": 40},
    {"Source": "Awake", "Target": "Coding", "Hours": 20},
    {"Source": "Awake", "Target": "Exercise", "Hours": 7},
    {"Source": "Awake", "Target": "Family & Social", "Hours": 15},
    {"Source": "Awake", "Target": "Admin & Chores", "Hours": 10},
    {"Source": "Awake", "Target": "Leisure", "Hours": 20},
]

# Dark-mode friendly accent colors for Sankey nodes.
TIME_RIVER_NODE_COLOR_MAP = {
    TIME_RIVER_ROOT: "#2DD4BF",
    "Awake": "#38BDF8",
    "Sleep": "#818CF8",
    "Work": "#F59E0B",
    "Coding": "#22C55E",
    "Exercise": "#F97316",
    "Family & Social": "#EC4899",
    "Admin & Chores": "#A78BFA",
    "Leisure": "#14B8A6",
}

TIME_RIVER_FALLBACK_COLORS = [
    "#60A5FA",
    "#34D399",
    "#F59E0B",
    "#FB7185",
    "#A78BFA",
    "#2DD4BF",
]

HEATMAP_WINDOW_DAYS = 30
HEATMAP_DONE_COLOR = "#22C55E"
HEATMAP_MISSED_COLOR = "#334155"

# Hide zoom/interaction controls that are not useful in this app context.
PLOTLY_CHART_CONFIG = {
    "displaylogo": False,
    "displayModeBar": False,
    "scrollZoom": False,
}


def _normalize_skill_name(skill_name: str) -> str:
    """Clean user text input by trimming spaces and collapsing repeats."""
    return " ".join(skill_name.strip().split())


def _slider_key_for_skill(skill_name: str) -> str:
    """Return a stable slider key for each skill name."""
    skill_digest = hashlib.md5(skill_name.casefold().encode("utf-8")).hexdigest()
    return f"rpg_score_{skill_digest[:12]}"


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert a hex color code to an rgba() string for link styling."""
    clean_hex = hex_color.lstrip("#")
    red, green, blue = (
        int(clean_hex[0:2], 16),
        int(clean_hex[2:4], 16),
        int(clean_hex[4:6], 16),
    )
    return f"rgba({red}, {green}, {blue}, {alpha})"


def _contrast_text_color(hex_color: str) -> str:
    """Choose a high-contrast text color for a given background.

    Returns either black or white based on the background luminance.
    """
    clean_hex = hex_color.lstrip("#")
    red, green, blue = (
        int(clean_hex[0:2], 16),
        int(clean_hex[2:4], 16),
        int(clean_hex[4:6], 16),
    )

    # Perceived brightness formula.
    brightness = (red * 299 + green * 587 + blue * 114) / 1000
    return "#000000" if brightness > 128 else "#FFFFFF"


def _last_n_days(day_count: int) -> list[date]:
    """Return an ordered list of dates covering the last N days."""
    today = date.today()
    return [
        today - timedelta(days=offset)
        for offset in range(day_count - 1, -1, -1)
    ]


def _render_png_download(
    chart_figure: go.Figure,
    output_file_name: str,
    button_label: str = "Download chart as PNG",
) -> None:
    """Render a PNG download button for a Plotly figure."""
    try:
        png_bytes = chart_figure.to_image(
            format="png",
            width=1200,
            height=900,
            scale=2,
        )
    except (ValueError, RuntimeError) as err:
        # Kaleido can raise RuntimeError if it cannot find Chrome.
        st.warning(
            "PNG export requires the kaleido package and a Chrome/Chromium runtime "
            "(e.g., install Chrome or run `plotly_get_chrome`)."
        )
        st.info(str(err))
    else:
        st.download_button(
            label=button_label,
            data=png_bytes,
            file_name=output_file_name,
            mime="image/png",
            use_container_width=True,
        )


def render_welcome() -> None:
    """Render a clean welcome panel for first-time visitors."""
    st.markdown("### Welcome to your personal reflection studio")

    st.markdown(
        "Track your habits, skills, and time allocation in one place. This tool helps you turn self-reflection data into visual patterns you can explore and improve over time."
    )

    with st.expander("How this tool helps", expanded=False):
        st.markdown(
            "- **RPG Skill Tree (Radar):** Compare strengths across key skills.\n"
            "- **Time River (Sankey):** Visualize where your hours flow.\n"
            "- **Consistency Heatmap:** Spot streaks and habit patterns."
        )


def render_radar_builder() -> None:
    """Render the complete RPG skill tree radar workflow."""
    st.subheader("🕸️ RPG Skill Tree (Radar)")
    st.caption("Score each skill from 1 to 10 to visualize your profile.")

    # Initialize skill list once and keep it across reruns using session state.
    if "rpg_skills" not in st.session_state:
        st.session_state.rpg_skills = DEFAULT_RPG_SKILLS.copy()

    # Default chart appearance controls, stored as session state so they persist across reruns.
    if "rpg_chart_text_size" not in st.session_state:
        st.session_state.rpg_chart_text_size = 14
    if "rpg_chart_background" not in st.session_state:
        st.session_state.rpg_chart_background = "#0F172A"

    # Split the section into input controls and live chart preview.
    input_col, chart_col = st.columns([1, 1.2], gap="large")

    with input_col:
        st.markdown("#### User Inputs")

        # Let users add custom skills dynamically.
        new_skill = st.text_input(
            "Add a custom skill (recommended to atleast add 3 skills)",
            placeholder="Example: Leadership",
        )

        if st.button("Add skill", use_container_width=True):
            cleaned_skill = _normalize_skill_name(new_skill)
            existing = {skill.casefold() for skill in st.session_state.rpg_skills}

            if not cleaned_skill:
                st.warning("Enter a skill name before adding it.")
            elif cleaned_skill.casefold() in existing:
                st.info(f'"{cleaned_skill}" is already in your skill list.')
            else:
                st.session_state.rpg_skills.append(cleaned_skill)
                st.success(f'Added "{cleaned_skill}".')

        # Users can remove only custom skills to preserve the default baseline.
        custom_skills = [
            skill
            for skill in st.session_state.rpg_skills
            if skill not in DEFAULT_RPG_SKILLS
        ]
        skills_to_remove = st.multiselect(
            "Remove custom skills",
            options=custom_skills,
        )
        if st.button("Remove selected skills", use_container_width=True):
            if skills_to_remove:
                st.session_state.rpg_skills = [
                    skill
                    for skill in st.session_state.rpg_skills
                    if skill not in skills_to_remove
                ]
                st.success("Selected skills removed.")
            else:
                st.info("Select at least one custom skill to remove.")

        st.markdown("#### Skill Scores")

        # Build 1-10 sliders dynamically for every active skill.
        skill_scores = {}
        for skill_name in st.session_state.rpg_skills:
            skill_scores[skill_name] = st.slider(
                label=skill_name,
                min_value=1,
                max_value=20,
                value=5,
                key=_slider_key_for_skill(skill_name),
            )


    # Prepare data used by Plotly Express for the radar chart.
    radar_df = pd.DataFrame(
        {
            "Skill": list(skill_scores.keys()),
            "Score": list(skill_scores.values()),
        }
    )

    # Apply previously selected appearance settings.
    chart_text_size = st.session_state.rpg_chart_text_size
    chart_background = st.session_state.rpg_chart_background

    with chart_col:
        st.markdown("#### Chart")

        radar_fig = px.line_polar(
            radar_df,
            r="Score",
            theta="Skill",
            line_close=True,
            template="plotly_dark",
        )
        radar_fig.update_traces(
            fill="toself",
            line={"width": 3},
            fillcolor="rgba(88, 166, 255, 0.35)",
        )

        # Keep the radial axis fixed at 0-10 to prevent visual distortion.
        text_color = _contrast_text_color(chart_background)

        radar_fig.update_layout(
            showlegend=False,
            margin={"l": 20, "r": 20, "t": 30, "b": 20},
            font={"size": chart_text_size, "color": text_color},
            paper_bgcolor=chart_background,
            plot_bgcolor=chart_background,
            polar={
                "bgcolor": chart_background,
                "radialaxis": {
                    "visible": True,
                    "range": [0, 20],
                    "tickmode": "linear",
                    "dtick": 2,
                    "tickfont": {"size": chart_text_size, "color": text_color},
                },
                "angularaxis": {"tickfont": {"size": chart_text_size, "color": text_color}},
            },
        )

        st.plotly_chart(
            radar_fig,
            use_container_width=True,
            config=PLOTLY_CHART_CONFIG,
        )

        # Render the chart download button (handles missing kaleido/Chrome).
        _render_png_download(
            chart_figure=radar_fig,
            output_file_name="rpg_skill_tree.png",
        )

        with st.expander("Settings", expanded=False):
            st.markdown("#### Chart appearance")
            st.slider(
                "Skill label font size",
                min_value=8,
                max_value=32,
                value=st.session_state.rpg_chart_text_size,
                key="rpg_chart_text_size",
                help="Set the size of the skill labels in the radar chart.",
            )
            st.color_picker(
                "Chart background color",
                value=st.session_state.rpg_chart_background,
                key="rpg_chart_background",
                help="Pick a background color for the chart export.",
            )


def render_sankey_builder() -> None:
    """Render the complete Time River Sankey workflow."""
    st.subheader("🌊 Time River (Sankey)")
    st.caption("Map how your 168 weekly hours flow across priorities.")

    if "time_river_rows" not in st.session_state:
        st.session_state.time_river_rows = pd.DataFrame(DEFAULT_TIME_RIVER_ROWS)

    # Keep the same split pattern as the radar section.
    input_col, chart_col = st.columns([1, 1.2], gap="large")

    with input_col:
        st.markdown("#### User Inputs")
        st.write(
            "Add or remove rows to describe your time flow. "
            "Each row is Source -> Target with Hours."
        )

        edited_rows = st.data_editor(
            st.session_state.time_river_rows,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Source": st.column_config.TextColumn(
                    "Source",
                    help="Where the hours come from",
                    required=True,
                ),
                "Target": st.column_config.TextColumn(
                    "Target",
                    help="Where the hours go",
                    required=True,
                ),
                "Hours": st.column_config.NumberColumn(
                    "Hours",
                    help="Hours allocated for this flow",
                    min_value=0,
                    step=1,
                    required=True,
                ),
            },
            use_container_width=True,
            key="time_river_editor",
        )

        # Persist edits across reruns.
        st.session_state.time_river_rows = edited_rows

        cleaned_rows = edited_rows.copy()
        cleaned_rows["Source"] = (
            cleaned_rows["Source"].fillna("").astype(str).str.strip()
        )
        cleaned_rows["Target"] = (
            cleaned_rows["Target"].fillna("").astype(str).str.strip()
        )
        cleaned_rows["Hours"] = pd.to_numeric(
            cleaned_rows["Hours"],
            errors="coerce",
        ).fillna(0)

        valid_rows = cleaned_rows[
            (cleaned_rows["Source"] != "")
            & (cleaned_rows["Target"] != "")
            & (cleaned_rows["Hours"] > 0)
        ]

        weekly_total = valid_rows.loc[
            valid_rows["Source"] == TIME_RIVER_ROOT,
            "Hours",
        ].sum()
        remaining_hours = 168 - weekly_total

        if weekly_total > 168:
            st.warning(
                "Allocated hours from Total Week exceed 168. "
                f"Current total: {weekly_total:.0f}h."
            )
        else:
            st.info(
                f"Total allocated from Total Week: {weekly_total:.0f}h | "
                f"Remaining: {remaining_hours:.0f}h"
            )

    with chart_col:
        st.markdown("#### Chart")

        if valid_rows.empty:
            st.info("Add at least one valid flow row to generate the Sankey chart.")
            return

        all_nodes = pd.unique(
            pd.concat(
                [valid_rows["Source"], valid_rows["Target"]],
                ignore_index=True,
            )
        )
        node_to_index = {node_name: idx for idx, node_name in enumerate(all_nodes)}

        source_indices = valid_rows["Source"].map(node_to_index).tolist()
        target_indices = valid_rows["Target"].map(node_to_index).tolist()
        flow_values = valid_rows["Hours"].tolist()

        node_colors = []
        for idx, node_name in enumerate(all_nodes):
            node_colors.append(
                TIME_RIVER_NODE_COLOR_MAP.get(
                    node_name,
                    TIME_RIVER_FALLBACK_COLORS[
                        idx % len(TIME_RIVER_FALLBACK_COLORS)
                    ],
                )
            )

        link_colors = [
            _hex_to_rgba(node_colors[source_idx], alpha=0.35)
            for source_idx in source_indices
        ]

        sankey_fig = go.Figure(
            data=[
                go.Sankey(
                    arrangement="snap",
                    node={
                        "pad": 18,
                        "thickness": 18,
                        "line": {"color": "#0F172A", "width": 0.5},
                        "label": list(all_nodes),
                        "color": node_colors,
                    },
                    link={
                        "source": source_indices,
                        "target": target_indices,
                        "value": flow_values,
                        "color": link_colors,
                    },
                )
            ]
        )
        sankey_fig.update_layout(
            template="plotly_dark",
            margin={"l": 10, "r": 10, "t": 25, "b": 10},
            font={"size": 13},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            sankey_fig,
            use_container_width=True,
            config=PLOTLY_CHART_CONFIG,
        )

        _render_png_download(
            chart_figure=sankey_fig,
            output_file_name="time_river_sankey.png",
        )


def render_heatmap_builder() -> None:
    """Render a GitHub-style habit consistency heatmap for the last 30 days."""
    st.subheader("🟩 Consistency Heatmap")
    st.caption("Track one habit daily and visualize your consistency pattern.")

    last_30_days = _last_n_days(HEATMAP_WINDOW_DAYS)

    # Use a two-column layout: controls on the left and chart on the right.
    input_col, chart_col = st.columns([1, 1.2], gap="large")

    with input_col:
        st.markdown("#### User Inputs")
        habit_name = st.text_input(
            "Habit name",
            placeholder="Example: Worked out",
            key="heatmap_habit_name",
        )

        # Quick actions for bulk updates to the 30-day grid.
        quick_action_col_1, quick_action_col_2 = st.columns(2)
        with quick_action_col_1:
            if st.button("Mark all done", use_container_width=True):
                for current_day in last_30_days:
                    st.session_state[
                        f"habit_done_{current_day.isoformat()}"
                    ] = True

        with quick_action_col_2:
            if st.button("Clear all", use_container_width=True):
                for current_day in last_30_days:
                    st.session_state[
                        f"habit_done_{current_day.isoformat()}"
                    ] = False

        st.markdown("#### Last 30 Days")
        st.caption("Check a box when the habit was completed on that date.")

        # Render a simple date checkbox grid to match GitHub-like tracking.
        date_grid_columns = st.columns(5, gap="small")
        for index, current_day in enumerate(last_30_days):
            day_key = f"habit_done_{current_day.isoformat()}"

            if day_key not in st.session_state:
                st.session_state[day_key] = False

            with date_grid_columns[index % 5]:
                st.checkbox(
                    label=current_day.strftime("%b %d"),
                    key=day_key,
                )

        completion_values = [
            int(st.session_state[f"habit_done_{current_day.isoformat()}"])
            for current_day in last_30_days
        ]
        done_days = sum(completion_values)
        completion_rate = (done_days / HEATMAP_WINDOW_DAYS) * 100

        st.metric("Completed Days", f"{done_days}/{HEATMAP_WINDOW_DAYS}")
        st.metric("Completion Rate", f"{completion_rate:.0f}%")

    with chart_col:
        st.markdown("#### Chart")

        heatmap_df = pd.DataFrame(
            {
                "Date": last_30_days,
                "Done": completion_values,
            }
        )

        grid_start = last_30_days[0]
        heatmap_df["WeekIndex"] = heatmap_df["Date"].apply(
            lambda current_day: (current_day - grid_start).days // 7
        )
        heatmap_df["DayIndex"] = heatmap_df["Date"].apply(
            lambda current_day: current_day.weekday()
        )

        total_weeks = int(heatmap_df["WeekIndex"].max()) + 1
        z_values = [[None for _ in range(total_weeks)] for _ in range(7)]
        hover_text = [["" for _ in range(total_weeks)] for _ in range(7)]

        # Build the 7 x N matrix used by Plotly's Heatmap trace.
        for _, row in heatmap_df.iterrows():
            week_index = int(row["WeekIndex"])
            day_index = int(row["DayIndex"])
            day_status = int(row["Done"])
            row_date = row["Date"]
            iso_year, iso_week, _ = row_date.isocalendar()

            z_values[day_index][week_index] = day_status
            hover_text[day_index][week_index] = (
                f"{row_date:%Y-%m-%d}<br>"
                f"Week: {iso_year}-W{iso_week:02d}<br>"
                f"{habit_name or 'Habit'}: "
                f"{'Done' if day_status == 1 else 'Missed'}"
            )

        week_labels = []
        for week_index in range(total_weeks):
            week_start = grid_start + timedelta(days=7 * week_index)
            week_iso_year, week_iso_number, _ = week_start.isocalendar()
            week_labels.append(f"{week_iso_year}-W{week_iso_number:02d}")

        day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        heatmap_fig = go.Figure(
            data=[
                go.Heatmap(
                    z=z_values,
                    x=week_labels,
                    y=day_labels,
                    text=hover_text,
                    hovertemplate="%{text}<extra></extra>",
                    colorscale=[
                        [0.0, HEATMAP_MISSED_COLOR],
                        [1.0, HEATMAP_DONE_COLOR],
                    ],
                    zmin=0,
                    zmax=1,
                    xgap=4,
                    ygap=4,
                    showscale=False,
                )
            ]
        )
        heatmap_fig.update_layout(
            template="plotly_dark",
            title=(habit_name or "Habit") + " - Last 30 Days",
            margin={"l": 20, "r": 20, "t": 55, "b": 20},
            xaxis={"title": "ISO Week", "showgrid": False},
            yaxis={
                "title": "",
                "showgrid": False,
                "autorange": "reversed",
            },
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            heatmap_fig,
            use_container_width=True,
            config=PLOTLY_CHART_CONFIG,
        )

        _render_png_download(
            chart_figure=heatmap_fig,
            output_file_name="consistency_heatmap.png",
        )


def main() -> None:
    """Run the Streamlit app."""
    st.set_page_config(
        page_title="Self-Reflection Diagram Generator 📊",
        page_icon="📊",
        layout="wide",
    )

    st.title("Self-Reflection Diagram Generator 📊")

    # Sidebar navigation controls the main content routing.
    st.sidebar.header("Navigation")
    selected_view = st.sidebar.radio(
        "Choose a chart generator",
        options=NAV_OPTIONS,
        index=0,
    )

    # Treat the initial option as the default landing route and show welcome text.
    if selected_view == NAV_OPTIONS[0]:
        render_welcome()
        render_radar_builder()
    elif selected_view == NAV_OPTIONS[1]:
        render_sankey_builder()
    elif selected_view == NAV_OPTIONS[2]:
        render_heatmap_builder()


if __name__ == "__main__":
    main()