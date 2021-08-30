import pandas as pd
import streamlit as st
import plotly.express as px

st.title("Spotify Insights")

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    is_whole_data = st.checkbox("Recently Played Music")
    if is_whole_data: 
        st.write(df)
    timestamps = st.sidebar.multiselect("Select Date", df['timestamp'].unique())
    # st.write("Selected Date: ", timestamps)
    columns = st.sidebar.multiselect("Select Columns", df.columns)
    # st.write("You selected these variables", variables)
    
    selected_timestamp_data = df[(df['timestamp'].isin(timestamps))]
    specific_data = selected_timestamp_data[columns]
    
    check_specific_data = st.checkbox("Display the data of selected dates")
    if check_specific_data:
        st.write(specific_data)
    
    # selected_artists = st.sidebar.multiselect('Select artists to compare', specific_data.artist_name.unique())
    # plot_data = specific_data[(specific_data['artist_name']).isin(selected_artists)]
    # st.bar_chart(plot_data.artist_name)

    is_fav_artists = st.checkbox("Top 10 Favorite Artists")
    if is_fav_artists:
        dashFrame = df.groupby(['artist_name'])['song_name'].count().sort_values(ascending=False).head(10)
        st.write(dashFrame)
    # is_chart = st.checkbox("Display Chart")
    # if is_chart:    
    #     fig = px.bar(dashFrame, x="song_name", y=["timestamp", "song_name"])
    #     st.plotly_chart(fig)