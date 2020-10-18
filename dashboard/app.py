import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import boto3
import random

dynamo = boto3.resource('dynamodb',
                        region_name='us-east-2')

table = dynamo.Table('test_table')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def get_table(table):
    response = table.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    df = pd.DataFrame(data)
    print(df.shape)
    return df

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
graph_df = pd.DataFrame({
    "Terms": ["Biden", "Trump"],
    "Amount": [2, 3],
})

fig = px.bar(graph_df, x="Terms", y="Amount", color="Terms")

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    dcc.Graph(id='example-graph'),
    dcc.Interval(id='interval-component',
                 interval=10*1000,
                 n_intervals=0)
])

@app.callback(Output('example-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_example_graph(n):
    df = get_table(table)
    print("hi")

    count_biden = df[df['text'].str.contains('Biden')].shape[0]
    count_trump = df[df['text'].str.contains('trump')].shape[0]

    if count_biden == 0:
        count_biden=random.choice([1,2,3,4,5])
    if count_trump == 0:
        count_trump=random.choice([1,2,3,4,5,6,7])
    graph_df = pd.DataFrame({
        "Terms": ["Biden", "Trump"],
        "Amount": [count_biden, count_trump],
    })
    fig = px.bar(graph_df, x="Terms", y="Amount", color="Terms")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
