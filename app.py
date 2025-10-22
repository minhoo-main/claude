import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd

# 과일 데이터 생성
df_fruits = pd.DataFrame({
    "과일": ["사과", "오렌지", "바나나", "포도", "딸기"],
    "수량": [10, 15, 7, 12, 9],
    "가격": [1000, 800, 500, 1500, 2000]
})

# 육류 데이터 생성
df_meats = pd.DataFrame({
    "육류": ["소고기", "돼지고기", "닭고기", "양고기", "오리고기"],
    "수량": [8, 12, 20, 5, 7],
    "가격": [15000, 8000, 5000, 18000, 12000]
})

# Dash 앱 초기화
app = dash.Dash(__name__)

# 레이아웃 정의
app.layout = html.Div([
    html.H1("Dash 테스트 애플리케이션", id="title"),

    # 탭 추가
    dcc.Tabs(id="tabs", value='tab-fruits', children=[
        dcc.Tab(label='과일', value='tab-fruits'),
        dcc.Tab(label='육류', value='tab-meats'),
    ]),

    html.Div(id='tabs-content')
])

# 콜백: 탭 전환
@callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'tab-fruits':
        return html.Div([
            html.Div([
                html.Label("과일 선택:"),
                dcc.Dropdown(
                    id="fruit-dropdown",
                    options=[{"label": fruit, "value": fruit} for fruit in df_fruits["과일"]],
                    value=df_fruits["과일"].iloc[0]
                )
            ], style={"width": "50%", "margin": "20px"}),

            html.Div(id="fruit-info", style={"margin": "20px"}),

            dcc.Graph(id="fruit-chart"),

            html.Div([
                html.Button("데이터 새로고침", id="refresh-button", n_clicks=0),
                html.Div(id="button-click-count", style={"margin": "10px"})
            ])
        ])
    elif tab == 'tab-meats':
        return html.Div([
            html.Div([
                html.Label("육류 선택:"),
                dcc.Dropdown(
                    id="meat-dropdown",
                    options=[{"label": meat, "value": meat} for meat in df_meats["육류"]],
                    value=df_meats["육류"].iloc[0]
                )
            ], style={"width": "50%", "margin": "20px"}),

            html.Div(id="meat-info", style={"margin": "20px"}),

            dcc.Graph(id="meat-chart"),

            html.Div([
                html.Button("데이터 새로고침", id="meat-refresh-button", n_clicks=0),
                html.Div(id="meat-button-click-count", style={"margin": "10px"})
            ])
        ])

# 콜백: 선택된 과일 정보 표시
@callback(
    Output("fruit-info", "children"),
    Input("fruit-dropdown", "value")
)
def display_fruit_info(selected_fruit):
    if selected_fruit:
        fruit_data = df_fruits[df_fruits["과일"] == selected_fruit].iloc[0]
        return html.Div([
            html.H3(f"선택된 과일: {selected_fruit}"),
            html.P(f"수량: {fruit_data['수량']}개"),
            html.P(f"가격: {fruit_data['가격']}원")
        ])
    return "과일을 선택해주세요."

# 콜백: 과일 차트 업데이트
@callback(
    Output("fruit-chart", "figure"),
    Input("fruit-dropdown", "value")
)
def update_fruit_chart(selected_fruit):
    fig = px.bar(df_fruits, x="과일", y="수량", title="과일별 수량")
    return fig

# 콜백: 과일 버튼 클릭 카운트
@callback(
    Output("button-click-count", "children"),
    Input("refresh-button", "n_clicks")
)
def count_fruit_clicks(n_clicks):
    return f"버튼 클릭 횟수: {n_clicks}"

# 콜백: 선택된 육류 정보 표시
@callback(
    Output("meat-info", "children"),
    Input("meat-dropdown", "value")
)
def display_meat_info(selected_meat):
    if selected_meat:
        meat_data = df_meats[df_meats["육류"] == selected_meat].iloc[0]
        return html.Div([
            html.H3(f"선택된 육류: {selected_meat}"),
            html.P(f"수량: {meat_data['수량']}kg"),
            html.P(f"가격: {meat_data['가격']}원")
        ])
    return "육류를 선택해주세요."

# 콜백: 육류 차트 업데이트
@callback(
    Output("meat-chart", "figure"),
    Input("meat-dropdown", "value")
)
def update_meat_chart(selected_meat):
    fig = px.bar(df_meats, x="육류", y="수량", title="육류별 수량")
    return fig

# 콜백: 육류 버튼 클릭 카운트
@callback(
    Output("meat-button-click-count", "children"),
    Input("meat-refresh-button", "n_clicks")
)
def count_meat_clicks(n_clicks):
    return f"버튼 클릭 횟수: {n_clicks}"

if __name__ == "__main__":
    app.run(debug=True)
