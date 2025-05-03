import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Leer y preprocesar datos
df = pd.read_csv("train.csv")
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)


# Inicializar app
app = dash.Dash(__name__)
app.title = "Dashboard Ventas - Grid 2x2"

# Layout en 2 filas x 2 columnas
app.layout = html.Div([
    html.H1("Dashboard de Ventas - Superstore", style={'textAlign': 'center', 'marginBottom': '30px'}),

    # Fila 1: dropdowns de categoría y región
    html.Div([
        html.Div([
            html.Label("Categoría:"),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': c, 'value': c} for c in df['Category'].unique()],
                value=df['Category'].unique()[0]
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Región:"),
            dcc.Dropdown(
                id='region-dropdown',
                options=[{'label': r, 'value': r} for r in df['Region'].unique()],
                value=df['Region'].unique()[0]
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ]),

    # Fila 2: línea y barras/torta
    html.Div([
        html.Div(dcc.Graph(id='line-chart'), style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        html.Div(dcc.Graph(id='category-chart'), style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ]),

    # Fila 3: dispersión y región
    html.Div([
        html.Div(dcc.Graph(id='scatter-plot'), style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        html.Div(dcc.Graph(id='region-chart'), style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ]),

    # Fila 4: selector de tipo de gráfico y rango de fechas
    html.Div([
        html.Div([
            html.Label("Tipo de gráfico:"),
            dcc.RadioItems(
                id='chart-type',
                options=[
                    {'label': 'Barras', 'value': 'bar'},
                    {'label': 'Torta', 'value': 'pie'}
                ],
                value='bar', labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Rango de fechas:"),
            dcc.DatePickerRange(
                id='date-range',
                start_date=df['Order Date'].min(),
                end_date=df['Order Date'].max(),
                display_format='DD/MM/YYYY'
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ])
])

# Callbacks:
@app.callback(
    Output('line-chart', 'figure'),
    Input('category-dropdown', 'value'),
    Input('region-dropdown', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_line(selected_cat, selected_reg, start, end):
    dff = df[(df['Category']==selected_cat)&(df['Region']==selected_reg)&
             (df['Order Date']>=start)&(df['Order Date']<=end)]
    monthly = dff.groupby('YearMonth')['Sales'].sum().reset_index()
    fig = px.line(monthly, x='YearMonth', y='Sales', title=f"Ventas Mensuales - {selected_cat}")
    fig.update_xaxes(rangeslider_visible=True)
    return fig

@app.callback(
    Output('category-chart', 'figure'),
    Input('chart-type', 'value'),
    Input('category-dropdown', 'value'),
    Input('region-dropdown', 'value')
)
def update_cat_chart(chart_type, cat, reg):
    dff = df[(df['Category']==cat)&(df['Region']==reg)]
    sub = dff.groupby('Sub-Category')['Sales'].sum().reset_index()
    if chart_type=='bar':
        return px.bar(sub, x='Sub-Category', y='Sales', title=f"Ventas Sub-categoría - {cat}")
    return px.pie(sub, names='Sub-Category', values='Sales', title=f"Distribución Sub-categoría - {cat}")

@app.callback(
    Output('scatter-plot', 'figure'),
    Input('category-dropdown', 'value'),
    Input('region-dropdown', 'value')
)
def update_scatter(cat, reg):
    dff = df[(df['Category']==cat)&(df['Region']==reg)]
    return px.scatter(dff, x='Sub-Category', y='Sales', color='Segment', title='Dispersión Ventas')

@app.callback(
    Output('region-chart', 'figure'),
    Input('region-dropdown', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_region(reg, start, end):
    dff = df[(df['Region']==reg)&(df['Order Date']>=start)&(df['Order Date']<=end)]
    state_sales = dff.groupby('State')['Sales'].sum().reset_index()
    return px.bar(state_sales, x='State', y='Sales', title=f"Ventas por Estado - {reg}")

if __name__=='__main__':
    app.run(debug=True)
