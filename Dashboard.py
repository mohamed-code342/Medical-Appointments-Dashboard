import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__)

df = pd.read_csv('KaggleV2-May-2016.csv')
df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'])
df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'])
df['WaitingDays'] = (df['AppointmentDay'] - df['ScheduledDay']).dt.days
df['WaitingDays'] = df['WaitingDays'].clip(lower=0)
df['WaitingDaysGroup'] = pd.cut(df['WaitingDays'], bins=[0, 2, 5, 10, 178], labels=['0-2', '3-5', '6-10', '11-178'], right=False)
df['DayOfWeek'] = df['AppointmentDay'].dt.day_name()
df['ChronicConditions'] = df[['Hipertension', 'Diabetes', 'Alcoholism', 'Handcap']].sum(axis=1)
df['AgeGroup'] = pd.cut(df['Age'], bins=[-1, 12, 18, 60, 120], labels=['Kid', 'Teen', 'Adult', 'Senior'])

colors = {
    'background': '#111827',
    'text': '#F9FAFB',
    'primary': '#3B82F6',
    'secondary': '#10B981',
    'no_show_yes': '#EF4444',
    'no_show_no': '#10B981'
}

px.defaults.template = "plotly_dark"


app.layout = html.Div([
    html.Div([
        html.H1("Medical Appointments Analysis", 
                style={'textAlign': 'center', 'color': colors['text'], 'padding': '20px'}),
        html.H3("Understanding Patient Attendance Patterns",
                style={'textAlign': 'center', 'color': colors['text'], 'marginBottom': '30px'})
    ]),
    
    html.Div([
        html.H2("1. Overall Attendance Overview", 
                style={'color': colors['text'], 'marginBottom': '20px'}),
        html.P("Let's first look at the overall distribution of show-ups versus no-shows.",
               style={'color': colors['text'], 'marginBottom': '15px'}),
        dcc.Graph(id='noshow-pie')
    ], style={'marginBottom': '40px'}),
    
    html.Div([
        html.H2("2. Patient Demographics", 
                style={'color': colors['text'], 'marginBottom': '20px'}),
        html.P("Analyze how age and gender affect appointment attendance.",
               style={'color': colors['text'], 'marginBottom': '15px'}),
        html.Div([
            html.Label('Select Age Groups to Analyze:', 
                      style={'color': colors['text'], 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='age-filter',
                options=[{'label': x, 'value': x} for x in df['AgeGroup'].unique()],
                value=df['AgeGroup'].unique().tolist(),
                multi=True,
                style={'backgroundColor': colors['background'], 'color': 'black', 'marginBottom': '15px'}
            ),
            dcc.Graph(id='age-gender-box')
        ])
    ], style={'marginBottom': '40px'}),
    
    html.Div([
        html.H2("3. Weekly Patterns", 
                style={'color': colors['text'], 'marginBottom': '20px'}),
        html.P("Discover which days of the week have higher attendance rates.",
               style={'color': colors['text'], 'marginBottom': '15px'}),
        dcc.Graph(id='weekly-distribution')
    ], style={'marginBottom': '40px'}),
    
    html.Div([
        html.H2("4. Impact of Health Conditions", 
                style={'color': colors['text'], 'marginBottom': '20px'}),
        html.P("Examining how chronic conditions affect attendance.",
               style={'color': colors['text'], 'marginBottom': '15px'}),
        dcc.Graph(id='chronic-conditions')
    ], style={'marginBottom': '40px'}),
    
    html.Div([
        html.H2("5. Scheduling Patterns", 
                style={'color': colors['text'], 'marginBottom': '20px'}),
        html.P("Analysis of waiting times between scheduling and appointment dates.",
               style={'color': colors['text'], 'marginBottom': '15px'}),
        dcc.Graph(id='waiting-days')
    ], style={'marginBottom': '40px'}),
    
    html.Div([
        html.H2("6. Neighborhood Analysis", 
                style={'color': colors['text'], 'marginBottom': '20px'}),
        html.P("Explore attendance patterns across different neighborhoods.",
               style={'color': colors['text'], 'marginBottom': '15px'}),
        html.Div([
            html.Label('Select Neighborhoods:', 
                      style={'color': colors['text'], 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='neighborhood-filter',
                options=[{'label': x, 'value': x} for x in df['Neighbourhood'].unique()],
                value=df['Neighbourhood'].unique().tolist()[:10],
                multi=True,
                style={'backgroundColor': colors['background'], 'color': 'black', 'width': '50%', 'marginBottom': '15px'}
            ),
            dcc.Graph(id='neighborhood-heatmap')
        ])
    ], style={'marginBottom': '40px'}),
    
    html.Div([
        html.H2("Key Insights", 
                style={'color': colors['text'], 'marginBottom': '20px'}),
        html.Ul([
            html.Li("Distribution of show vs no-show appointments", 
                   style={'color': colors['text']}),
            html.Li("Age and gender impact on attendance", 
                   style={'color': colors['text']}),
            html.Li("Weekly attendance patterns", 
                   style={'color': colors['text']}),
            html.Li("Impact of chronic conditions", 
                   style={'color': colors['text']}),
            html.Li("Effect of waiting time", 
                   style={'color': colors['text']}),
            html.Li("Neighborhood-specific patterns", 
                   style={'color': colors['text']})
        ], style={'marginBottom': '20px'})
    ])
], style={'backgroundColor': colors['background'], 'padding': '40px', 'maxWidth': '1200px', 'margin': '0 auto'})

@app.callback(
    Output('age-gender-box', 'figure'),
    [Input('age-filter', 'value')]
)
def update_age_gender(selected_ages):
    filtered_df = df[df['AgeGroup'].isin(selected_ages)]
    
    fig = px.box(filtered_df, 
                 x='Gender', 
                 y='Age',
                 color='No-show',
                 title='Age Distribution by Gender and Attendance',
                 color_discrete_map={'Yes': colors['no_show_yes'], 'No': colors['no_show_no']})
    
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    return fig

@app.callback(
    Output('neighborhood-heatmap', 'figure'),
    [Input('neighborhood-filter', 'value')]
)
def update_neighborhood(selected_neighborhoods):
    filtered_df = df[df['Neighbourhood'].isin(selected_neighborhoods)]
    
    fig = px.bar(
        filtered_df.groupby(['Neighbourhood', 'No-show']).size().reset_index(name='count'),
        x='Neighbourhood',
        y='count',
        color='No-show',
        title='Neighborhood Attendance Patterns',
        barmode='stack',  
        color_discrete_map={'Yes': colors['no_show_yes'], 'No': colors['no_show_no']},
        labels={'count': 'Number of Appointments', 'Neighbourhood': 'Neighborhood'}
    )
    
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        showlegend=True,
        xaxis_tickangle=-45,  
        height=600  )
    
    return fig

@app.callback(
    [Output('noshow-pie', 'figure'),
     Output('weekly-distribution', 'figure'),
     Output('chronic-conditions', 'figure'),
     Output('waiting-days', 'figure')],
    [Input('dummy', 'children')] 
)
def update_static_graphs(_):
    noshow_pie = px.pie(
        df,
        names='No-show',
        title='No-show vs Show-up Distribution',
        hole=0.4,
        color='No-show',
        color_discrete_map={'Yes': colors['no_show_yes'], 'No': colors['no_show_no']}
    )
    
    weekly_dist = px.bar(
        df.groupby('DayOfWeek').size().reset_index(name='count'),
        x='DayOfWeek',
        y='count',
        title='Appointments by Day of Week',
        color_discrete_sequence=[colors['primary']]
    )
    
    chronic_fig = px.bar(
        df.groupby(['ChronicConditions', 'No-show']).size().reset_index(name='count'),
        x='ChronicConditions',
        y='count',
        color='No-show',
        title='Impact of Chronic Conditions',
        barmode='stack',
        color_discrete_map={'Yes': colors['no_show_yes'], 'No': colors['no_show_no']}
    )
    
    waiting_days = px.bar(
        df.groupby(['WaitingDaysGroup', 'No-show']).size().reset_index(name='count'),
        x='WaitingDaysGroup',
        y='count',
        color='No-show',
        title='Delay Between Scheduling and Appointment',
        barmode='group',
        color_discrete_map={'Yes': colors['no_show_yes'], 'No': colors['no_show_no']}
    )
    
    for fig in [noshow_pie, weekly_dist, chronic_fig, waiting_days]:
        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
    
    return noshow_pie, weekly_dist, chronic_fig, waiting_days

app.layout.children.append(html.Div(id='dummy', style={'display': 'none'}))

if __name__ == '__main__':
    app.run()