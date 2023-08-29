import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
from urllib.request import urlopen

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

st.set_page_config(layout="wide")


covid_cnfrmd = pd.read_csv('covid_confirmed_usafacts_updated_data.csv')
county_pop = pd.read_csv('covid_county_population_usafacts.csv')
covid_deaths = pd.read_csv('covid_deaths_usafacts_updated_data.csv')

st.title("WHO's COVID-19 Weekly Epidemiological Update")


def group_and_drop(df,col_name):
    new_df = df.groupby(col_name).sum().diff(axis=1)
    new_df.drop(columns=['StateFIPS'],inplace=True)
    return new_df

def find_start_date(date_list):
    start_date = date_list[0]
    for i in date_list:
        if i.day_name() == 'Sunday':
            start_date = i.date()
            break
    return start_date

#function for finding the first 'Saturday'
def find_end_date(date_list):
    end_date = date_list[-1]
    for j in date_list[::-1]:
        if j.day_name() == 'Saturday':
            end_date = j.date()
            break
    return end_date

#function for filtering the required data based on the
#Start and end date from the original grouped dataframe
def new_start_end(df):
    df.columns = pd.to_datetime(df.columns)
    date_list = df.columns
    start_d = find_start_date(date_list)
    end_d = find_end_date(date_list)
    new_df = df.loc[:,str(start_d):str(end_d)]
    return new_df,start_d,end_d



def week_manipulation(df,start_date,end_date):
    new_df = df.groupby([i//7 for i in range(len(df.columns))],axis = 1).sum().T
    date_range = pd.period_range(start = start_date, end = end_date,freq='W')
    date_range = date_range.map(str)
    #splitting since period range will return weeks start and end date.
    date_range = date_range.str.split('/').str[1]
    date_range=pd.Series(date_range)
    #assigning date range to a new column weeks in a new df
    new_weekly_cases = new_df.assign(weeks = date_range)
    new_weekly_cases.set_index(['weeks'],inplace=True)
    return new_weekly_cases


def countyFIPS_manipulation(df):
    df['countyFIPS'] = df['countyFIPS'].astype(str)
    for i in range(1,len(df['countyFIPS'])+1):
        if len(df['countyFIPS'][i])<5:
            df['countyFIPS'][i] = df['countyFIPS'][i].zfill(5)
    return df


def merge_operation(df,county_population):
    new_df = pd.merge(df,county_population,how='outer',on=['countyFIPS'])
    new_df.dropna(how='any', inplace=True)
    new_df.reset_index(level=0,inplace=True)
    new_df['countyFIPS'] = new_df['countyFIPS'].astype(int)
    return new_df

def per_100k(df):
    df.iloc[:,1:-1] = df.iloc[:,1:-1].apply(lambda x: x/(df['population']))
    df.iloc[:,1:-1] = df.iloc[:,1:-1].apply(lambda y: y*100000).round(2)
    return df


def slider_code(df):
    new_data = df.T.iloc[1:-1,:].reset_index(level=0).rename(columns={'index':'date'})
    date_options = new_data.iloc[:,0:1].values.tolist()
    #st.write(date_options)#dates_option
    d_2=list()
    for i in date_options:
        for j in i:
            d_2.append(j)
    return d_2

# def choropleth_plot(df,date_r,l,color,counties):
#     fig = px.choropleth(df,  # Input Pandas DataFrame
#             st.write(df[countyFIPS]),
#
#             locations=df[countyFIPS],  # DataFrame column with locations
#             geojson= counties,
#             color= df[date_r],# DataFrame column with color values
#             color_continuous_scale=color,
#             range_color=(l[0],l[1]))
#     return fig


#Filtering the required columns
new_df_state = covid_cnfrmd.loc[:,'State':]
s_sum = group_and_drop(new_df_state,'State') #calling the function for grouping and droping unnecessary columns
s_sum_df,start_date_s,end_date_s = new_start_end(s_sum)
new_weekly_cases = week_manipulation(s_sum_df,start_date_s,end_date_s) #calling the function for creating weeks
new_weekly_cases['Total_weekly_cases'] = new_weekly_cases.sum(axis=1) #finding the total death cases
fig_new_cases = px.line(new_weekly_cases,
                #x = new_weekly_cases['weeks'],
                y = new_weekly_cases['Total_weekly_cases'],
                title = 'Weekly new Covid-19 cases')
fig_new_cases.update_traces(line_color = "blue")



#Covid-19 weekly death cases

new_death_df = covid_deaths.loc[:,'State':]
new_death_df = group_and_drop(new_death_df,'State')  #calling the function for grouping and droping unnecessary columns
new_deaths, start_date_deaths,end_date_deaths = new_start_end(new_death_df)
weekly_death_cases = week_manipulation(new_deaths,start_date_deaths,end_date_deaths) #calling the function for creating weeks
weekly_death_cases['Total deaths'] = weekly_death_cases.sum(axis = 1) #finding the total death cases

#Plotting the data
fig_death = px.line(weekly_death_cases,
            y = weekly_death_cases['Total deaths'],
            title = 'Weekly Covid-19 Deaths')

fig_death.update_traces(line_color = "maroon")
#b = st.plotly_chart(fig_death)


option_1 = st.selectbox('Select the type of Visualization',('line chart','Market Basket Analysis','RFM_Segmentation')



    #Question 3
    covid_county = group_and_drop(covid_cnfrmd,'countyFIPS')
    new_cases_county,start_date_county,end_date_county = new_start_end(covid_county)
    covid_county = week_manipulation(new_cases_county,start_date_county,end_date_county)
    covid_county = covid_county.T

    ### Manipulating population dataframe and merging it with the county weekly cases
    county_population = county_pop.groupby(['countyFIPS']).sum()
    new_merged_df = merge_operation(covid_county,county_population)
    new_cases_df = per_100k(new_merged_df)
    new_cases_df.dropna(inplace=True)
    new_cases_df = countyFIPS_manipulation(new_cases_df)


    # Slider Code
    d_2 = slider_code(new_cases_df)


    #Question 4
    new_death_df_map = group_and_drop(covid_deaths,'countyFIPS')
    new_deaths_county,start_date_county_deaths,end_date_county_deaths = new_start_end(new_death_df_map)
    new_death_df_map = week_manipulation(new_deaths_county,start_date_county_deaths,end_date_county_deaths)
    new_deaths_county = new_death_df_map.T

    county_population = county_pop.groupby(['countyFIPS']).sum()
    new_deaths_county = merge_operation(new_deaths_county,county_population)
    new_deaths_county['countyFIPS'] = new_deaths_county['countyFIPS'].astype(int)

    new_deaths_county = per_100k(new_deaths_county)
    new_deaths_county.dropna(inplace=True)
    new_deaths_county = countyFIPS_manipulation(new_deaths_county)


### Question 5 and Question 6
    if option_2 == 'Weekly new Covid-19 cases':
        ss = st.empty()
        play = st.empty()
        new_cases_positions = st.empty()
    #new_death_positions = st.empty()
        with ss:
             chosen = st.select_slider('', options=d_2, value=d_2[0],key='1')
             with new_cases_positions:
                 #fig = choropleth_plot(new_cases_df,chosen,[0,1000])
                 fig = px.choropleth(new_cases_df,  # Input Pandas DataFrame
                              locations="countyFIPS",  # DataFrame column with locations
                              geojson= counties,
                              color = chosen,# DataFrame column with color values
                               color_continuous_scale='burg',
                               range_color=(0,10000)
                               ) # Set to plot as US States

                 #fig = choropleth_plot(new_cases_df,chosen,[0,100000],'burg',counties)
                 fig.update_layout(
                     title_text = 'Covid-19 Weekly new cases in each county', # Create a Title
                     geo_scope='usa',)
                 st.plotly_chart(fig,use_container_width=True)

                 def graph_plot():
                    for week in d_2:
                        with ss:
                            chosen = st.select_slider('', options=d_2, value=week, key="2")
                        with new_cases_positions:
                            #fig = choropleth_plot(new_cases_df,week,[0,1000])
                            fig = px.choropleth(new_cases_df,  # Input Pandas DataFrame
                                 locations="countyFIPS",  # DataFrame column with locations
                                geojson= counties,
                                 color= week,# DataFrame column with color values
                                 color_continuous_scale='burg',
                                 range_color=(0,10000)) # Set to plot as US States
                            #fig = choropleth_plot(new_cases_df,chosen,[0,100000],'burg',counties)
                            fig.update_layout(
                                title_text = 'Covid-19 Weekly new cases in each US county', # Create a Title
                                geo_scope='usa',)
                            st.plotly_chart(fig,use_container_width=True)

                 with play:
                    st.button(label='Play',on_click= graph_plot)



    if option_2 == 'Weekly new Covid-19 deaths':
        ss = st.empty()
        play = st.empty()
        new_death_positions = st.empty()
        with ss:
             chosen = st.select_slider('', options=d_2, value=d_2[0],key='1')
             with new_death_positions:
                 fig_1 = px.choropleth(new_deaths_county,  # Input Pandas DataFrame
                                   locations="countyFIPS",  # DataFrame column with locations
                                   geojson= counties,
                                   color= chosen,# DataFrame column with color values
                                   color_continuous_scale='oranges',
                                 range_color=(0,500),) # Set to plot as US States
                 fig_1.update_layout(
                        title_text = 'Covid 19 Weekly new deaths in each county', # Create a Title
                         geo_scope='usa',)
                 st.plotly_chart(fig_1,use_container_width=True)

                 def graph_plot():
                    for week in d_2:
                        with ss:
                            chosen = st.select_slider('', options=d_2, value=week, key="2")
                        with new_death_positions:
                             fig_1 = px.choropleth(new_deaths_county,  # Input Pandas DataFrame
                                               locations="countyFIPS",  # DataFrame column with locations
                                                geojson= counties,
                                                 color= week,# DataFrame column with color values
                                                 color_continuous_scale='oranges',
                                                 range_color=(0,500),) # Set to plot as US States
                             #fig_1 = choropleth_plot(new_deaths_county,chosen,[0,10000],'oranges',counties)
                             fig_1.update_layout(
                                     title_text = 'Covid 19 Weekly new deaths in each county', # Create a Title
                                      geo_scope='usa',)
                             st.plotly_chart(fig_1,use_container_width=True)
                 with play:
                    st.button(label='Play',on_click= graph_plot)
