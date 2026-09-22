import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime
import requests
from openai import OpenAI
from dotenv import load_dotenv



st.title("Welcome to Habit Tracking")
st.header("What are you looking for?")


# Load habits
if "hdf" not in st.session_state:
    if os.path.exists("habit.csv"):
        st.session_state.hdf = pd.read_csv("habit.csv")

        st.session_state.hdf["Habit_Date"] = pd.to_datetime(
            st.session_state.hdf["Habit_Date"],
            format="mixed"
        )
    else:
        st.session_state.hdf = pd.DataFrame(
            columns=[
                "Habit_Name",
                "Habit_Frequency",
                "Habit_Goal",
                "Habit_Category",
                "Habit_Date"
            ]
        )
#load API LLm
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)




# Load completions
if "cdf" not in st.session_state:
    if os.path.exists("completion.csv"):
        st.session_state.hdf = pd.read_csv("habit.csv")

        st.session_state.hdf["Habit_Date"] = pd.to_datetime(
            st.session_state.hdf["Habit_Date"],
            format="mixed"
        )
    else:
        st.session_state.cdf = pd.DataFrame(
            columns=[
                "Habit_Complet_Name",
                "Habit_Complet_Date"
            ]
        )


options = st.selectbox(
    "",
    (
        "Add a new habit to track",
        "Log completion of a habit",
        "View habit streaks and statistics",
        "Edit or remove habits",
        "View all habits",
        "Personal Habit Coach"
    ),
    index=None,
    placeholder="Choose from the list"
)


# Mock notification
messages = [
    "Don't forget to complete your habits today!",
    "Keep going! Consistency builds habits.",
    "One more completion can keep your streak going!",
    "Small steps make big progress!",
    "Check your habits and keep your streak alive!"
]

if st.button("🔔 Show Reminder"):
    st.toast(random.choice(messages))


# OPTION 1
if options == "Add a new habit to track":

    habit_name = st.text_input(
        "Habit Name:",
        placeholder="eg: read, study ..."
    )

    habit_fre = st.selectbox(
        "Frequency",
        ["Daily", "Weekly", "Monthly"],
        index=None
    )

    habit_goal = st.number_input(
        "Number of Repetitions:",
        min_value=1,
        max_value=10,
        value=None,
        placeholder="range between 1 - 10"
    )

    habit_cat = st.selectbox(
        "Category",
        ["Health", "Productivity", "Learning"],
        index=None
    )

    habit_date = st.date_input("Select Start Date:")

    habit_button = st.button("Submit", type="primary")

    if habit_button:

        if all([
            habit_name,
            habit_fre,
            habit_goal,
            habit_cat,
            habit_date
        ]):

            new_habit = pd.DataFrame({
                "Habit_Name": [habit_name],
                "Habit_Frequency": [habit_fre],
                "Habit_Goal": [habit_goal],
                "Habit_Category": [habit_cat],
                "Habit_Date": [pd.to_datetime(habit_date)]
            })

            st.session_state.hdf = pd.concat(
                [st.session_state.hdf, new_habit],
                
                ignore_index=True
            )

            st.session_state.hdf.to_csv(
                "habit.csv",
                
                index=False
            )

            st.success("New Habit Added!")

        else:
            st.warning("Fill the Blank")

    st.dataframe(
        st.session_state.hdf,
        hide_index=True
    )


# OPTION 2
elif options == "Log completion of a habit":

    habit_names = st.session_state.hdf["Habit_Name"].to_list()

    if len(habit_names) == 0:
        st.warning("No habits available. Add a habit first.")

    else:

        name_complet = st.selectbox(
            "Which Habit?",
            options=habit_names,
            index=None
        )

        if name_complet is not None:

            filt = st.session_state.hdf[
                st.session_state.hdf["Habit_Name"] == name_complet
            ]

            frequency = filt.iloc[0, 1]
            goal = filt.iloc[0, 2]

            col1, col2 = st.columns(2)

            col1.metric("Frequency", frequency)
            col2.metric("Target", goal)

        complet_button = st.button(
            "Submit",
            type="primary"
        )

        if complet_button:

            if name_complet:

                date_complet = datetime.now().replace(
                    microsecond=0
                )

                new_completion = pd.DataFrame({
                    "Habit_Complet_Name": [name_complet],
                    "Habit_Complet_Date": [date_complet]
                })

                st.session_state.cdf = pd.concat(
                    [st.session_state.cdf, new_completion],
                    ignore_index=True
                )

                st.session_state.cdf.to_csv(
                    "completion.csv",
                    index=False
                )

                st.success("Habit Completion Added!")

                # API advice

                with st.spinner("Getting your motivational quote...", show_time=True):

                    response = requests.get("https://zenquotes.io/api/random")

                    r = response.json()

                    advice = r[0]['q']

                    st.header(advice)

            else:
                st.warning("Select a habit first.")


# OPTION 3
elif options == "View habit streaks and statistics":

    habit_comp_name = st.session_state.cdf[
        "Habit_Complet_Name"
    ]

    if len(habit_comp_name) == 0:
        st.warning("No habits completed.")

    else:

        name_streak = st.selectbox(
            "Which Habit?",
            options=habit_comp_name.unique(),
            index=None
        )

        if name_streak is not None:

            filt_1 = st.session_state.cdf[
                st.session_state.cdf[
                    "Habit_Complet_Name"
                ] == name_streak
            ].copy()

            filt_2 = st.session_state.hdf[
                st.session_state.hdf[
                    "Habit_Name"
                ] == name_streak
            ]

            start_date = pd.to_datetime(
                filt_2.iloc[0, 4],
                 format="mixed")
            
            end_date = pd.Timestamp.today().normalize()

            frequency = filt_2.iloc[0, 1]
            goal = filt_2.iloc[0, 2]

            number_days = (
                end_date - start_date
            ).days + 1


            if frequency == "Daily":
                number_periods = number_days

            elif frequency == "Weekly":
                number_periods = (number_days + 6) // 7

            elif frequency == "Monthly":
                number_periods = (
                    (end_date.year - start_date.year) * 12
                    + (end_date.month - start_date.month)
                    + 1
                )


            expected = number_periods * goal
            actual = len(filt_1)

            completion_rate = (
                actual / expected
            ) * 100

            completion_rate = min(
                completion_rate,
                100
            )


            if frequency == "Daily":

                period_counts = (
                    filt_1
                    .groupby(
                        filt_1[
                            "Habit_Complet_Date"
                        ].dt.date
                    )
                    .size()
                )

            elif frequency == "Weekly":

                period_counts = (
                    filt_1
                    .groupby(
                        filt_1[
                            "Habit_Complet_Date"
                        ].dt.to_period("W")
                    )
                    .size()
                )

            elif frequency == "Monthly":

                period_counts = (
                    filt_1
                    .groupby(
                        filt_1[
                            "Habit_Complet_Date"
                        ].dt.to_period("M")
                    )
                    .size()
                )


            successful_periods = period_counts[
                period_counts >= goal
            ].index.tolist()


            streak = 0
            best_streak = 0
            previous_period = None

            for period in successful_periods:

                if previous_period is None:
                    streak = 1

                else:

                    if frequency == "Daily":

                        current = pd.Timestamp(period)
                        previous = pd.Timestamp(previous_period)

                        if (current - previous).days == 1:
                            streak += 1
                        else:
                            streak = 1

                    else:

                        if (
                            period.ordinal
                            - previous_period.ordinal
                            == 1
                        ):
                            streak += 1
                        else:
                            streak = 1


                if streak > best_streak:
                    best_streak = streak

                previous_period = period


            current_streak = 0

            if len(successful_periods) > 0:

                last_successful = successful_periods[-1]

                if frequency == "Daily":
                    current_period = end_date.date()

                elif frequency == "Weekly":
                    current_period = end_date.to_period("W")

                elif frequency == "Monthly":
                    current_period = end_date.to_period("M")


                if last_successful == current_period:
                    current_streak = streak


            st.subheader(f"📊 {name_streak} Statistics")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Completions",
                actual
            )

            col2.metric(
                "Expected",
                expected
            )

            col3.metric(
                "Completion Rate",
                f"{completion_rate:.1f}%"
            )


            col1, col2 = st.columns(2)

            col1.metric(
                "🔥 Current Streak",
                current_streak
            )

            col2.metric(
                "🏆 Best Streak",
                best_streak
            )


            st.subheader("Progress")

            st.progress(
                completion_rate / 100,
                text=f"Completion Progress: {completion_rate:.1f}%"
            )


            if current_streak == 0:

                st.info(
                    f"Complete your target of {goal} "
                    f"time(s) this {frequency.lower()} period "
                    "to start a streak!"
                )

            else:

                st.success(
                    f"🔥 You're currently on a "
                    f"{current_streak} {frequency.lower()} "
                    "streak!"
                )


# OPTION 4
elif options == "Edit or remove habits":

    if st.session_state.hdf.empty:

        st.warning(
            "No habits available. Add a habit first."
        )


    else:


        st.session_state.hdf["Habit_Date"] = pd.to_datetime(
            st.session_state.hdf["Habit_Date"], format="mixed"
        )



        
        edited_df = st.data_editor(
            st.session_state.hdf,
            num_rows="delete",
            hide_index=True,

            column_config={

                "Habit_Name":
                    st.column_config.TextColumn(
                        "Habit Name",
                        required=True
                    ),

                "Habit_Frequency":
                    st.column_config.SelectboxColumn(
                        "Frequency",
                        options=[
                            "Daily",
                            "Weekly",
                            "Monthly"
                        ],
                        required=True
                    ),

                "Habit_Goal":
                    st.column_config.NumberColumn(
                        "Target",
                        min_value=1,
                        max_value=10,
                        step=1,
                        required=True
                    ),

                "Habit_Category":
                    st.column_config.SelectboxColumn(
                        "Category",
                        options=[
                            "Health",
                            "Productivity",
                            "Learning"
                        ],
                        required=True
                    ),

                "Habit_Date":
                    st.column_config.DateColumn(
                        "Start Date",
                        required=True
                    )
            }
        )

        edit_me = st.button(
            "Save Changes",
            type="primary"
        )

        if edit_me:

            if edited_df.equals(
                st.session_state.hdf
            ):

                st.warning("No changes were made!")

            else:

                st.session_state.hdf = edited_df
                st.session_state.hdf.to_csv(
                    "habit.csv",
                    index=False
                )

                st.success("Changes saved!")


# OPTION 5
elif options == "View all habits":

    if st.session_state.hdf.empty:

        st.warning("No habits available.")

    else:

        st.dataframe(
            st.session_state.hdf,
            hide_index=True
        )

elif options == "Personal Habit Coach":

    st.subheader("🤖 Personal Habit Coach")

    if st.session_state.hdf.empty:
        st.warning("Add some habits first.")

    elif st.session_state.cdf.empty:
        st.warning("Log some habit completions first.")

    else:

        st.write(
            "Your coach will analyze your habits and completion history "
            "and give you personalized advice."
        )

        if st.button("Analyze My Habits", type="primary"):

            habits_data = st.session_state.hdf.to_string(index=False)
            completion_data = st.session_state.cdf.to_string(index=False)

            prompt = f"""
            You are a personal habit coach.

            Here are the user's habits:
            {habits_data}

            Here are the user's completion logs:
            {completion_data}

            Analyze the user's habit patterns.

            Give:
            1. A short summary of their consistency.
            2. Any possible burnout or inconsistency patterns.
            3. Practical personalized advice.
            4. One habit stacking suggestion.

            Keep the response simple and concise.
            """

            with st.spinner("Analyzing your habits...", show_time=True):

                response = client.chat.completions.create(
                    model="poolside/laguna-s-2.1:free",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                coach_response = response.choices[0].message.content

            st.subheader("Coach's Advice")
            st.markdown(coach_response)