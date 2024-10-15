import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime


def load_data():
    """
    Loads data from the CSV file.
    """
    try:
        return pd.read_csv("odds_data.csv")
    except FileNotFoundError:
        return pd.DataFrame()  # Return an empty DataFrame if the file is not found


def main():
    st.title("Odds Data Viewer")

    # Load the data
    data = load_data()

    # Add a new column to represent the match as "home_team vs away_team"
    if not data.empty:
        data["match"] = data["home_team"] + " vs " + data["away_team"]

    # Display the current time and data
    st.write("Data last fetched at:",
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # st.dataframe(data)  # Display the DataFrame in the app

    # Sidebar filters
    if not data.empty:
        # Get unique match identifiers in the form of "home_team vs away_team"
        match_ids = data['match'].unique()
        st.sidebar.header("Filter Options")

        # Dropdown menu for selecting a match
        selected_match = st.sidebar.selectbox("Select a Match", match_ids)

        # Filter data based on the selected match
        filtered_data = data[data['match'] == selected_match]

        if not filtered_data.empty:
            # Get the unique teams for the selected match
            teams = filtered_data['team'].unique()
            selected_team = st.sidebar.selectbox("Select a Team", teams)
            bookmakers = filtered_data['bookmaker'].unique()
            selected_bookmakers = st.sidebar.multiselect(
                "Select Bookmakers", bookmakers)

            if selected_bookmakers:
                # Filter the data based on the selected bookmakers
                filtered_odds_data = filtered_data[filtered_data['bookmaker'].isin(
                    selected_bookmakers)]
                if not filtered_odds_data.empty:
                    # Aggregate data to avoid duplicates by taking the mean odds for each team per bookmaker
                    odds_data = filtered_odds_data.groupby(
                        ['bookmaker', 'team'], as_index=False)['odds'].mean()
                    odds_data = odds_data.pivot(
                        index='bookmaker', columns='team', values='odds').reset_index()

                    if not odds_data.empty:
                        # Plot the bar chart for odds comparison
                        fig_bar = px.bar(odds_data, x='bookmaker', y=odds_data.columns[1:],
                                         title=f'Odds Comparison for {selected_match}',
                                         labels={'value': 'Odds',
                                                 'bookmaker': 'Bookmaker'},
                                         barmode='group')
                        st.plotly_chart(fig_bar)
                    else:
                        st.write("No odds data available for plotting.")
                else:
                    st.write(
                        "No odds data available for the selected bookmakers.")
            else:
                st.write("Please select at least one bookmaker to compare odds.")

            # Line chart for odds over time
            st.subheader("Odds Changes Over Time")
            time_series_data = filtered_data[[
                'time', 'bookmaker', 'team', 'odds']]

            if not time_series_data.empty:
                # Convert time column to datetime
                time_series_data['time'] = pd.to_datetime(
                    time_series_data['time'])
                # Filter by selected team
                time_series_data = time_series_data[time_series_data['team']
                                                    == selected_team]

                if not time_series_data.empty:
                    # Create line chart
                    fig_line = px.line(time_series_data, x='time', y='odds', color='bookmaker',
                                       title=f'Odds Changes Over Time for {selected_team} in {selected_match}',
                                       labels={'odds': 'Odds', 'time': 'Time'})
                    st.plotly_chart(fig_line)
                else:
                    st.write(
                        "No time series data available for the selected team.")
            else:
                st.write("No time series data available.")

        else:
            st.write("No data available for the selected match.")
    else:
        st.write("No data available.")

    # Refresh button to manually update the data
    if st.button("Reload Data"):
        # Reload the data
        data = load_data()  # This will load the data again and refresh the content


if __name__ == "__main__":
    main()
