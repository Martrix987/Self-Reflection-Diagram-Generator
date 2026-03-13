"""Self-Reflection Diagram Generator.

Step 1 scaffold:
- Base Streamlit layout and page configuration.
- Sidebar navigation for chart generator sections.
- Placeholder routing blocks for each visualization mode.
"""

import hashlib

import pandas as pd
import plotly.express as px
import streamlit as st


# Navigation options shown in the sidebar.
NAV_OPTIONS = [
    "🕸️ RPG Skill Tree (Radar)",
    "🌊 Time River (Sankey)",
    "🟩 Consistency Heatmap",
]

# Default skills shown when the app is opened for the first time.
DEFAULT_RPG_SKILLS = [
    "Resilience",
    "Problem Solving",
    "Technical Mastery",
    "Communication",
    "Time Management",
]


def _normalize_skill_name(skill_name: str) -> str:
    """Clean user text input by trimming spaces and collapsing repeats."""
    return " ".join(skill_name.strip().split())


def _slider_key_for_skill(skill_name: str) -> str:
    """Return a stable slider key for each skill name."""
    skill_digest = hashlib.md5(skill_name.casefold().encode("utf-8")).hexdigest()
    return f"rpg_score_{skill_digest[:12]}"


def render_welcome() -> None:
    """Render a clean welcome panel for first-time visitors."""
    st.markdown("### Welcome to your personal reflection studio")

    # Use columns to create a modern, readable hero section.
    left_col, right_col = st.columns([2, 1], gap="large")

    with left_col:
        st.write(
            "Track your habits, skills, and time allocation in one place. "
            "This tool helps you turn self-reflection data into visual patterns "
            "you can explore and improve over time."
        )

    with right_col:
        st.info(
            "Use the sidebar to switch between diagram generators and start "
            "building your reflection dashboard."
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

    # Split the section into input controls and live chart preview.
    input_col, chart_col = st.columns([1, 1.2], gap="large")

    with input_col:
        st.markdown("#### User Inputs")

        # Let users add custom skills dynamically.
        new_skill = st.text_input(
            "Add a custom skill",
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
                max_value=10,
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
        radar_fig.update_layout(
            showlegend=False,
            margin={"l": 20, "r": 20, "t": 30, "b": 20},
            polar={
                "radialaxis": {
                    "visible": True,
                    "range": [0, 10],
                    "tickmode": "linear",
                    "dtick": 1,
                }
            },
        )

        st.plotly_chart(
            radar_fig,
            use_container_width=True,
            config={"displaylogo": False},
        )

        # Export the chart as PNG bytes for direct download in the browser.
        try:
            png_bytes = radar_fig.to_image(
                format="png",
                width=1200,
                height=900,
                scale=2,
            )
        except ValueError:
            st.warning(
                "PNG export requires the kaleido package in your environment."
            )
        else:
            st.download_button(
                label="Download chart as PNG",
                data=png_bytes,
                file_name="rpg_skill_tree.png",
                mime="image/png",
                use_container_width=True,
            )


def render_sankey_placeholder() -> None:
    """Placeholder content for the time river sankey view."""
    st.subheader("🌊 Time River (Sankey)")
    st.caption("Sankey diagram generator will be implemented in a later step.")


def render_heatmap_placeholder() -> None:
    """Placeholder content for the consistency heatmap view."""
    st.subheader("🟩 Consistency Heatmap")
    st.caption("Heatmap generator will be implemented in a later step.")


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
        render_sankey_placeholder()
    elif selected_view == NAV_OPTIONS[2]:
        render_heatmap_placeholder()


if __name__ == "__main__":
    main()