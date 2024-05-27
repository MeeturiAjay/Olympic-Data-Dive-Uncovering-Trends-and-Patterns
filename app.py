import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st
import seaborn as sns
import scipy
import plotly.figure_factory as ff

import preprocessor, helper

# Load data
df = pd.read_csv('athlete_events.csv')
regions = pd.read_csv('noc_regions.csv')

# Preprocess data
df = preprocessor.preprocess(df, regions)

# Streamlit layout
st.sidebar.title("Olympics Analysis")
st.sidebar.image('https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png')
user_choice = st.sidebar.radio(
    'Choose an option',
    ('Medal Tally', 'Overall Analysis', 'Country wise Analysis', 'Athlete wise Analysis')
)

if user_choice == 'Medal Tally':
    col1, col2, col3 = st.columns([2, 4, 1])
    with col2:
        st.title("Medals Tally")

    st.sidebar.header(user_choice)
    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox('Choose year', years)
    selected_country = st.sidebar.selectbox('Choose country', country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
    if selected_year == selected_country == 'Overall':
        st.title("Overall Statistics")
    if selected_year != 'Overall' and selected_country == 'Overall':
        st.title("Medal Tally in " + str(selected_year))
    if selected_year == 'Overall' and selected_country != 'Overall':
        st.title("Medal Tally of " + selected_country)
    if selected_year != 'Overall' and selected_country != 'Overall':
        st.title(f"Medal Tally of {selected_country} in {str(selected_year)}")

    st.table(medal_tally)

if user_choice == 'Overall Analysis':
    col1, col2, col3 = st.columns([2, 4, 1])
    with col2:
        st.title("Overall Analysis")

    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    st.title("Top Statistics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Cities")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Athletes")
        st.title(athletes)
    with col3:
        st.header("Nations")
        st.title(nations)

    st.title("")

    st.header("No. of nations participated (year-wise)")
    nations_overtime = helper.data_overtime(df, 'region')
    fig = px.line(nations_overtime, x='Year', y='count')
    st.plotly_chart(fig)

    st.header("No. of Events (year-wise)")
    events_overtime = helper.data_overtime(df, 'Event')
    fig = px.line(events_overtime, x='Year', y='count')
    st.plotly_chart(fig)

    st.header("No. of Athletes participated (year-wise)")
    athletes_overtime = helper.data_overtime(df, 'Name')
    fig = px.line(athletes_overtime, x='Year', y='count')
    st.plotly_chart(fig)

    st.header("Stats of Events (year-wise)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(
        x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(int),
        annot=True
    )
    st.pyplot(fig)

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()

    st.header("Most Successful Athletes")
    selected_sport = st.selectbox('Select the sport', sport_list)
    result = helper.most_successful(df, selected_sport)
    st.table(result)

if user_choice == 'Country wise Analysis':
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.title("Country wise Analysis")
    st.sidebar.header("Country wise Analysis")

    st.header("Medal Tally (year-wise)")
    countries = df['region'].dropna().unique().tolist()
    countries.sort()
    country_selected = st.sidebar.selectbox("Choose a country", countries)
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'Season', 'City', 'Sport', 'Event', 'Medal'],
                            inplace=True)
    new_df = temp_df[temp_df['region'] == country_selected]
    final_df = new_df.groupby('Year')['Medal'].count().reset_index()
    st.plotly_chart(px.line(final_df, x='Year', y='Medal'))

    st.header("Medal Tally (sport-wise)")
    new_df = temp_df[temp_df['region'] == country_selected]
    fig, ax = plt.subplots(figsize=(20, 20))
    ax = sns.heatmap(
        new_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0).astype(int),
        annot=True
    )
    st.pyplot(fig)

    st.header("Top Athletes")
    result1 = helper.most_successful_country_wise(df, country_selected)
    st.table(result1)

if user_choice == 'Athlete wise Analysis':
    st.sidebar.title("Athlete wise Analysis")

    atheletes_df = df.drop_duplicates(subset=['Name', 'region'])
    x1 = atheletes_df['Age'].dropna()
    x2 = atheletes_df[atheletes_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = atheletes_df[atheletes_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = atheletes_df[atheletes_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
                             show_hist=False, show_rug=False)

    fig.update_layout(
        xaxis_title='Age',
        yaxis_title='Probability'
    )
    st.header("Distribution of Ages")
    st.plotly_chart(fig)

    sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
              'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
              'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
              'Water Polo', 'Hockey', 'Rowing', 'Fencing',
              'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
              'Tennis', 'Golf', 'Softball', 'Archery',
              'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
              'Rhythmic Gymnastics', 'Rugby Sevens',
              'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']

    x = []
    name = []

    # Iterate through the unique sports and collect age data
    for sport in sports:
        temp_df = atheletes_df[atheletes_df['Sport'] == sport]
        ages = temp_df['Age'].dropna()
        if len(ages) > 1:
            x.append(ages)
            name.append(sport)

    # Create the distribution plot
    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)

    # Update the layout
    fig.update_layout(
        xaxis_title='Age',
        yaxis_title='Probability'
    )
    st.header('Ages wrt. Sports (Gold Medalists)')
    st.plotly_chart(fig)

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    st.header("Height Vs Weight")
    selected_sport = st.selectbox('Select the sport', sport_list)
    temp_df = helper.weightvheight(df, selected_sport)
    fig, ax = plt.subplots()
    ax = sns.scatterplot(x=temp_df['Weight'], y=temp_df['Height'], hue=temp_df['Medal'], style=temp_df['Sex'])
    st.pyplot(fig)

    st.header("Men Vs Women")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)
