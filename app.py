import dash
from dash import html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd

# 샘플 데이터 생성
df = pd.DataFrame({
    "과일": ["사과", "오렌지", "바나나", "포도", "딸기"],
    "수량": [10, 15, 7, 12, 9],
    "가격": [1000, 800, 500, 1500, 2000]
})

# Dash 앱 초기화
app = dash.Dash(__name__)

# 레이아웃 정의
app.layout = html.Div([
    html.H1("Dash 테스트 애플리케이션", id="title"),

    html.Div([
        html.Label("과일 선택:"),
        dcc.Dropdown(
            id="fruit-dropdown",
            options=[{"label": fruit, "value": fruit} for fruit in df["과일"]],
            value=df["과일"].iloc[0]
        )
    ], style={"width": "50%", "margin": "20px"}),

    html.Div(id="fruit-info", style={"margin": "20px"}),

    dcc.Graph(id="fruit-chart"),

    html.Div([
        html.Button("데이터 새로고침", id="refresh-button", n_clicks=0),
        html.Div(id="button-click-count", style={"margin": "10px"})
    ])
])

# 콜백: 선택된 과일 정보 표시
@callback(
    Output("fruit-info", "children"),
    Input("fruit-dropdown", "value")
)
def display_fruit_info(selected_fruit):
    if selected_fruit:
        fruit_data = df[df["과일"] == selected_fruit].iloc[0]
        return html.Div([
            html.H3(f"선택된 과일: {selected_fruit}"),
            html.P(f"수량: {fruit_data['수량']}개"),
            html.P(f"가격: {fruit_data['가격']}원")
        ])
    return "과일을 선택해주세요."

# 콜백: 차트 업데이트
@callback(
    Output("fruit-chart", "figure"),
    Input("fruit-dropdown", "value")
)
def update_chart(selected_fruit):
    fig = px.bar(df, x="과일", y="수량", title="과일별 수량")
    return fig

# 콜백: 버튼 클릭 카운트
@callback(
    Output("button-click-count", "children"),
    Input("refresh-button", "n_clicks")
)
def count_clicks(n_clicks):
    return f"버튼 클릭 횟수: {n_clicks}"

if __name__ == "__main__":
    app.run(debug=True)
