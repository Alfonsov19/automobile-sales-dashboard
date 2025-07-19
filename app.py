#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import os 

# Load data once and cache
def load_data():
    return pd.read_csv("historical_automobile_sales.csv")

data = load_data()

# Initialize Dash app with suppressed callback exceptions
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Automobile Sales Dashboard"

# Constants
YEAR_RANGE = list(range(1980, 2024))
STAT_OPTIONS = [
    {'label': 'Yearly Statistics', 'value': 'yearly'},
    {'label': 'Recession Period Statistics', 'value': 'recession'}
]
DROPDOWN_STYLE = {'width': '80%', 'padding': '3px', 'fontSize': 20, 'textAlignLast': 'center'}

# Layout
app.layout = html.Div([
    html.H1(
        "Automobile Sales Dashboard",
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 24}
    ),
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(id='dropdown-statistics', options=STAT_OPTIONS, placeholder='Select a report type', style=DROPDOWN_STYLE)
    ]),
    html.Div([
        dcc.Dropdown(id='select-year', options=[{'label': year, 'value': year} for year in YEAR_RANGE],
                    placeholder='Select a year', style=DROPDOWN_STYLE)
    ]),
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flexDirection': 'column'})
])

# Helper function for recession plots
def create_recession_plots():
    recession_data = data[data['Recession'] == 1]
    
    # Plot 1: Yearly sales during recession
    yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
    chart1 = dcc.Graph(figure=px.line(
        yearly_rec, x='Year', y='Automobile_Sales',
        title="Average Automobile Sales During Recession"
    ))

    # Plot 2: Average sales by vehicle type
    avg_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
    chart2 = dcc.Graph(figure=px.bar(
        avg_sales, x='Vehicle_Type', y='Automobile_Sales',
        title="Average Vehicles Sold by Type During Recession"
    ))

    # Plot 3: Expenditure share by vehicle type
    exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
    chart3 = dcc.Graph(figure=px.pie(
        exp_rec, names='Vehicle_Type', values='Advertising_Expenditure',
        title="Expenditure Share by Vehicle Type During Recession"
    ))

    # Plot 4: Unemployment effect
    unemp_data = recession_data.groupby(['Vehicle_Type', 'unemployment_rate'])['Automobile_Sales'].mean().reset_index()
    chart4 = dcc.Graph(figure=px.bar(
        unemp_data, x='Vehicle_Type', y='Automobile_Sales', color='unemployment_rate',
        labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Sales'},
        title="Unemployment Rate Effect on Vehicle Sales"
    ))

    return [
        html.Div([html.Div(chart1, style={'width': '50%'}), html.Div(chart2, style={'width': '50%'})], style={'display': 'flex'}),
        html.Div([html.Div(chart3, style={'width': '50%'}), html.Div(chart4, style={'width': '50%'})], style={'display': 'flex'})
    ]

# Helper function for yearly plots
def create_yearly_plots(selected_year):
    yearly_data = data[data['Year'] == selected_year]
    
    # Plot 1: Overall yearly sales
    yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
    chart1 = dcc.Graph(figure=px.line(
        yas, x='Year', y='Automobile_Sales',
        title="Automobile Sales Over Years"
    ))

    # Plot 2: Monthly sales
    mas = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
    chart2 = dcc.Graph(figure=px.line(
        mas, x='Month', y='Automobile_Sales',
        title=f"Monthly Automobile Sales in {selected_year}"
    ))

    # Plot 3: Average sales by vehicle type
    avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
    chart3 = dcc.Graph(figure=px.bar(
        avr_vdata, x='Vehicle_Type', y='Automobile_Sales',
        title=f"Average Vehicles Sold by Type in {selected_year}"
    ))

    # Plot 4: Advertisement expenditure
    exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
    chart4 = dcc.Graph(figure=px.pie(
        exp_data, names='Vehicle_Type', values='Advertising_Expenditure',
        title=f"Advertisement Expenditure by Vehicle Type in {selected_year}"
    ))

    return [
        html.Div([html.Div(chart1, style={'width': '50%'}), html.Div(chart2, style={'width': '50%'})], style={'display': 'flex'}),
        html.Div([html.Div(chart3, style={'width': '50%'}), html.Div(chart4, style={'width': '50%'})], style={'display': 'flex'})
    ]

# Callbacks
@app.callback(
    Output('select-year', 'disabled'),
    Input('dropdown-statistics', 'value')
)
def toggle_year_dropdown(selected_statistics):
    return selected_statistics != 'yearly'

@app.callback(
    Output('output-container', 'children'),
    [Input('dropdown-statistics', 'value'), Input('select-year', 'value')]
)
def update_dashboard(selected_statistics, selected_year):
    if not selected_statistics:
        return [html.Div("Please select a report type.")]
    
    if selected_statistics == 'recession':
        return create_recession_plots()
    if selected_statistics == 'yearly' and selected_year:
        return create_yearly_plots(selected_year)
    
    return [html.Div("Please select a valid report type and year.")]

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True, host='0.0.0.0', port=port)