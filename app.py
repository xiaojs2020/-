import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from dash.exceptions import PreventUpdate
import json

# 初始化Dash应用
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "作息分析工具"

# 读取初始数据
df = pd.read_csv('作息.csv')

# 计算初始方差和上下界
df['作息方差'] = (df['平均作息'] ** 3) * 1.0
df['作息上界'] = np.minimum(df['平均作息'] + df['作息方差'], 1)
df['作息下界'] = np.maximum(df['平均作息'] - df['作息方差'], 0)

# 添加作息时间字段
df['作息启动期A'] = ''
df['作息启动期B'] = ''
df['作息启动期C'] = ''
df['作息结束期A'] = ''
df['作息结束期B'] = ''
df['作息结束期C'] = ''

# 应用布局
app.layout = html.Div([
    # 标题
    #html.H1("📊 作息分析工具", style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    # 控制面板
    html.Div([
        #html.H3("控制面板", style={'marginBottom': '20px'}),
        
        # 数据输入区域
        html.H4("数据输入"),
        html.Label("批量输入平均作息值（支持多种格式）："),
        html.P("💡 支持：逗号分隔、空格分隔、换行分隔、表格复制粘贴", style={'fontSize': '12px', 'color': 'gray'}),
        dcc.Textarea(
            id='batch-textarea',
            value='0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.18, 0.24, 0.34, 0.44, 0.54, 0.64, 0.58, 0.52, 0.46, 0.40, 0.40, 0.40, 0.40, 0.40, 0.46, 0.52, 0.58, 0.64, 0.68, 0.72, 0.76, 0.80, 0.80, 0.80, 0.80, 0.80, 0.72, 0.64, 0.56, 0.48, 0.48, 0.48, 0.48, 0.48, 0.56, 0.64, 0.72, 0.80, 0.80, 0.80, 0.80, 0.80, 0.74, 0.68, 0.62, 0.56, 0.44, 0.32, 0.20, 0.08, 0.06, 0.04, 0.02, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00',
            style={'width': '100%', 'height': '100px'},
            placeholder="请输入96个数值，支持多种格式..."
        ),
        html.Button("应用批量输入", id='apply-batch', n_clicks=0, style={'marginTop': '10px'}),
        html.Div(id='batch-input-status', style={'marginTop': '5px', 'fontSize': '12px'}),
        
        html.Hr(),
        
        # 调整方式选择
        html.H4("调整方式选择"),
        dcc.RadioItems(
            id='adjustment-mode',
            options=[
                {'label': '全局调整', 'value': 'global'},
                {'label': '逐个调整', 'value': 'individual'}
            ],
            value='individual',
            style={'marginBottom': '20px'}
        ),
        
        # 全局调整滑块
        html.Div(id='global-adjustment', children=[
            html.Label("作息方差调整系数："),
            dcc.Slider(
                id='variance-multiplier',
                min=0.1,
                max=3.0,
                step=0.1,
                value=1.0,
                marks={0.1: '0.1', 0.5: '0.5', 1.0: '1.0', 1.5: '1.5', 2.0: '2.0', 2.5: '2.5', 3.0: '3.0'},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ]),
        
        # 逐个调整面板
        html.Div(id='individual-adjustment', style={'display': 'none'}, children=[
            html.H4("逐个调整模式"),
            html.Div(id='selected-point-info'),
            html.Div(id='individual-variance-slider', children=[
                html.Label("选中时间点的方差值："),
                dcc.Slider(
                    id='individual-variance',
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    value=0.0,
                    marks={i/10: str(i/10) for i in range(0, 11)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ])
        ]),
        
        # 作息时间设置区域
        html.Hr(),
        html.H4("作息时间设置"),
        html.P("💡 点击图表中的点，然后点击下方按钮设置作息时间", style={'fontSize': '12px', 'color': 'gray'}),
        
        # 作息启动期按钮
        html.Div([
            html.Button("作息启动期A", id='start-period-a', n_clicks=0, 
                       style={'width': '30%', 'margin': '2px', 'backgroundColor': '#28a745', 'color': 'white', 'border': 'none', 'padding': '8px 4px', 'fontSize': '11px'}),
            html.Button("作息启动期B", id='start-period-b', n_clicks=0, 
                       style={'width': '30%', 'margin': '2px', 'backgroundColor': '#28a745', 'color': 'white', 'border': 'none', 'padding': '8px 4px', 'fontSize': '11px'}),
            html.Button("作息启动期C", id='start-period-c', n_clicks=0, 
                       style={'width': '30%', 'margin': '2px', 'backgroundColor': '#28a745', 'color': 'white', 'border': 'none', 'padding': '8px 4px', 'fontSize': '11px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
        
        # 作息结束期按钮
        html.Div([
            html.Button("作息结束期A", id='end-period-a', n_clicks=0, 
                       style={'width': '30%', 'margin': '2px', 'backgroundColor': '#dc3545', 'color': 'white', 'border': 'none', 'padding': '8px 4px', 'fontSize': '11px'}),
            html.Button("作息结束期B", id='end-period-b', n_clicks=0, 
                       style={'width': '30%', 'margin': '2px', 'backgroundColor': '#dc3545', 'color': 'white', 'border': 'none', 'padding': '8px 4px', 'fontSize': '11px'}),
            html.Button("作息结束期C", id='end-period-c', n_clicks=0, 
                       style={'width': '30%', 'margin': '2px', 'backgroundColor': '#dc3545', 'color': 'white', 'border': 'none', 'padding': '8px 4px', 'fontSize': '11px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
        
        # 作息时间显示
        html.Div(id='period-times-display', style={'marginTop': '10px', 'fontSize': '12px'}),
        
        # 应用按钮
        html.Button("🔄 应用更改", id='apply-changes', n_clicks=0, 
                   style={'marginTop': '20px', 'backgroundColor': '#007bff', 'color': 'white', 'border': 'none', 'padding': '10px 20px'})
    ], style={'width': '20%', 'float': 'left', 'padding': '20px', 'backgroundColor': '#f8f9fa'}),
    
    # 主要内容区域
    html.Div([
        # 图表区域
        html.Div([
            dcc.Tabs([
                dcc.Tab(label="图1: 平均作息与作息方差", children=[
                    dcc.Graph(
                        id='graph1',
                        config={
                            'displayModeBar': True, 
                            'modeBarButtonsToAdd': ['pan2d', 'select2d', 'lasso2d'],
                            'editable': True,
                            'edits': {'shapePosition': True}
                        },
                        style={'height': '500px'}
                    ),
                    html.Div(id='click-output1', style={'marginTop': '10px'})
                ]),
                dcc.Tab(label="图2: 平均作息与上下界", children=[
                    dcc.Graph(
                        id='graph2',
                        config={
                            'displayModeBar': True, 
                            'modeBarButtonsToAdd': ['pan2d', 'select2d', 'lasso2d'],
                            'editable': True,
                            'edits': {'shapePosition': True}
                        },
                        style={'height': '500px'}
                    ),
                    html.Div(id='click-output2', style={'marginTop': '10px'})
                ])
            ])
        ], style={'width': '90%', 'float': 'left'}),
        
        # 数据表格
        html.Div([
            #html.H3("数据表格"),
            #html.Div(id='data-table'),
            html.Button("📥 下载CSV", id='download-csv', n_clicks=0, style={
                'marginTop': '10px',
                'padding': '15px 30px',
                'fontSize': '16px',
                'fontWeight': 'bold',
                'backgroundColor': '#28a745',
                'color': 'white',
                'border': 'none',
                'borderRadius': '8px',
                'cursor': 'pointer',
                'boxShadow': '0 4px 8px rgba(0,0,0,0.2)',
                'transition': 'all 0.3s ease'
            })
        ], style={'width': '30%', 'float': 'left', 'padding': '20px'})
    ], style={'marginLeft': '20%'}),
    
    # 存储组件
    dcc.Store(id='data-store', data=df.to_dict('records')),
    dcc.Store(id='selected-point', data=None),
    dcc.Store(id='period-times', data={
        '作息启动期A': '',
        '作息启动期B': '',
        '作息启动期C': '',
        '作息结束期A': '',
        '作息结束期B': '',
        '作息结束期C': ''
    }),
    
    # 键盘事件监听
    dcc.Store(id='keyboard-events', data={'last_key': None}),
    
    # 下载组件
    dcc.Download(id='download-dataframe-csv'),
    
    # 加载组件
    dcc.Loading(id="loading-1", type="default"),
    
    # 键盘事件监听脚本
    html.Script('''
        document.addEventListener('keydown', function(event) {
            if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
                // 发送键盘事件到Dash
                window.dispatchEvent(new CustomEvent('dash-keyboard', {
                    detail: { key: event.key }
                }));
            }
        });
    '''),
    
    # 清除浮动
    html.Div(style={'clear': 'both'})
], style={'fontFamily': 'Arial, sans-serif'})

# 回调函数：更新调整模式显示
@app.callback(
    [Output('global-adjustment', 'style'),
     Output('individual-adjustment', 'style')],
    [Input('adjustment-mode', 'value')]
)
def update_adjustment_mode(mode):
    if mode == 'global':
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}

# 合并的回调函数：处理所有数据更新和图表渲染
@app.callback(
    [Output('data-store', 'data'),
     Output('graph1', 'figure'),
     Output('graph2', 'figure'),
     Output('batch-input-status', 'children')],
    [Input('variance-multiplier', 'value'),
     Input('adjustment-mode', 'value'),
     Input('selected-point', 'data'),
     Input('individual-variance', 'value'),
     Input('apply-batch', 'n_clicks'),
     Input('apply-changes', 'n_clicks'),
     Input('graph1', 'relayoutData'),
     Input('graph2', 'relayoutData')],
    [State('batch-textarea', 'value'),
     State('data-store', 'data')]
)
def update_data_and_handle_interactions(variance_multiplier, adjustment_mode, selected_point, individual_variance, 
                                      batch_clicks, apply_clicks, relayout1, relayout2, batch_text, data):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # 从存储中获取数据
    df = pd.DataFrame(data)
    status_message = ""
    
    # 处理键盘事件和拖拽
    if trigger_id in ['graph1', 'graph2']:
        relayout_data = relayout1 if trigger_id == 'graph1' else relayout2
        if relayout_data and selected_point:
            point_index = selected_point['index']
            
            # 检查是否是键盘事件（通过relayoutData中的特殊标记）
            if 'keyboard_event' in relayout_data:
                key = relayout_data['keyboard_event']
                current_variance = df.loc[point_index, '作息方差']
                
                if key == 'ArrowUp':
                    # 增加方差值
                    new_variance = min(current_variance + 0.01, 1.0)
                    df.loc[point_index, '作息方差'] = new_variance
                elif key == 'ArrowDown':
                    # 减少方差值
                    new_variance = max(current_variance - 0.01, 0.0)
                    df.loc[point_index, '作息方差'] = new_variance
                
                # 更新上下界
                current_average = df.loc[point_index, '平均作息']
                df.loc[point_index, '作息上界'] = np.minimum(current_average + new_variance, 1)
                df.loc[point_index, '作息下界'] = np.maximum(current_average - new_variance, 0)
    
    # 处理批量输入
    if trigger_id == 'apply-batch' and batch_text:
        try:
            # 支持多种分隔符：逗号、空格、换行、制表符
            import re
            # 先按换行分割，再按逗号、空格、制表符分割
            lines = batch_text.strip().split('\n')
            values_str = []
            
            for line in lines:
                if line.strip():
                    # 分割每行中的数值
                    line_values = re.split(r'[,\s\t]+', line.strip())
                    values_str.extend([v.strip() for v in line_values if v.strip()])
            
            # 过滤掉非数字的字符串
            numeric_values = []
            for v in values_str:
                try:
                    val = float(v)
                    if 0 <= val <= 1:
                        numeric_values.append(val)
                except ValueError:
                    continue
            
            if len(numeric_values) == 96:
                df['平均作息'] = numeric_values
                status_message = f"✅ 成功解析 {len(numeric_values)} 个数值"
            elif len(numeric_values) > 96:
                df['平均作息'] = numeric_values[:96]
                status_message = f"⚠️ 数值过多，只使用前96个"
            elif len(numeric_values) < 96:
                # 如果数值不足96个，用0填充
                while len(numeric_values) < 96:
                    numeric_values.append(0.0)
                df['平均作息'] = numeric_values
                status_message = f"⚠️ 数值不足96个，已用0填充到96个"
            else:
                status_message = "❌ 未找到有效数值"
        except Exception as e:
            status_message = f"❌ 解析错误: {str(e)}"
            pass
    
    # 更新方差
    if adjustment_mode == 'global':
        df['作息方差'] = (df['平均作息'] ** 3) * variance_multiplier
        # 更新上下界
        df['作息上界'] = np.minimum(df['平均作息'] + df['作息方差'], 1)
        df['作息下界'] = np.maximum(df['平均作息'] - df['作息方差'], 0)
    elif selected_point and adjustment_mode == 'individual' and trigger_id == 'individual-variance':
        # 处理个别点调整
        point_index = selected_point.get('index')
        if point_index is not None:
            # 更新选中点的方差
            df.loc[point_index, '作息方差'] = individual_variance
            # 更新该点的上下界
            current_average = df.loc[point_index, '平均作息']
            df.loc[point_index, '作息上界'] = np.minimum(current_average + individual_variance, 1)
            df.loc[point_index, '作息下界'] = np.maximum(current_average - individual_variance, 0)
    
    # 创建图1
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df['时间'],
        y=df['平均作息'],
        mode='lines+markers',
        name='平均作息',
        line=dict(color='orange', width=3),
        marker=dict(size=4),
        customdata=np.arange(len(df))
    ))
    fig1.add_trace(go.Scatter(
        x=df['时间'],
        y=df['作息方差'],
        mode='lines+markers',
        name='作息方差',
        line=dict(color='green', width=3, dash='dash'),
        marker=dict(size=4),
        customdata=np.arange(len(df))
    ))
    fig1.update_layout(
        title="341-工作日客流",
        xaxis_title="时间",
        yaxis_title="数值",
        xaxis=dict(
            tickmode='array',
            tickvals=df['时间'][::4],
            ticktext=[f"{i//4:02d}:00" for i in range(0, 96, 4)]
        ),
        yaxis=dict(range=[0, 1]),
        hovermode='x unified'
    )
    
    # 创建图2
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df['时间'],
        y=df['平均作息'],
        mode='lines+markers',
        name='平均作息',
        line=dict(color='blue', width=3),
        marker=dict(size=4),
        customdata=np.arange(len(df))
    ))
    fig2.add_trace(go.Scatter(
        x=df['时间'],
        y=df['作息上界'],
        mode='lines+markers',
        name='作息上界',
        line=dict(color='red', width=2),
        marker=dict(size=3),
        customdata=np.arange(len(df))
    ))
    fig2.add_trace(go.Scatter(
        x=df['时间'],
        y=df['作息下界'],
        mode='lines+markers',
        name='作息下界',
        line=dict(color='purple', width=2),
        marker=dict(size=3),
        customdata=np.arange(len(df))
    ))
    fig2.update_layout(
        title="作息上下界分析",
        xaxis_title="时间",
        yaxis_title="数值",
        xaxis=dict(
            tickmode='array',
            tickvals=df['时间'][::4],
            ticktext=[f"{i//4:02d}:00" for i in range(0, 96, 4)]
        ),
        yaxis=dict(range=[0, 1]),
        hovermode='x unified'
    )
    
    return df.to_dict('records'), fig1, fig2, status_message

# 回调函数：处理图表点击事件
@app.callback(
    [Output('selected-point', 'data'),
     Output('click-output1', 'children'),
     Output('click-output2', 'children')],
    [Input('graph1', 'clickData'),
     Input('graph2', 'clickData')]
)
def handle_click(click_data1, click_data2):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    click_data = click_data1 if trigger_id == 'graph1' else click_data2
    
    if click_data:
        point = click_data['points'][0]
        point_info = {
            'index': point['customdata'],
            'x': point['x'],
            'y': point['y'],
            'curveNumber': point['curveNumber']
        }
        
        output_text = f"点击了时间: {point['x']}, 数值: {point['y']:.3f}"
        return point_info, output_text, output_text
    
    return None, "", ""



# 回调函数：更新选中点信息
@app.callback(
    [Output('selected-point-info', 'children'),
     Output('individual-variance', 'value')],
    [Input('selected-point', 'data')],
    [State('data-store', 'data')]
)
def update_selected_point_info(selected_point, data):
    if not selected_point or not data:
        return "", 0.0
    
    df = pd.DataFrame(data)
    point_index = selected_point['index']
    
    if point_index < len(df):
        current_time = df.iloc[point_index]['时间']
        current_average = df.iloc[point_index]['平均作息']
        current_variance = df.iloc[point_index]['作息方差']
        
        info_text = f"""
        **选中时间：{current_time}**
        - 当前平均作息：{current_average:.3f}
        - 当前方差值：{current_variance:.3f}
        """
        
        return info_text, current_variance
    
    return "请点击图表中的点来选择要调整的时间点", 0.0

# 回调函数：处理作息时间按钮点击
@app.callback(
    [Output('period-times', 'data'),
     Output('period-times-display', 'children')],
    [Input('start-period-a', 'n_clicks'),
     Input('start-period-b', 'n_clicks'),
     Input('start-period-c', 'n_clicks'),
     Input('end-period-a', 'n_clicks'),
     Input('end-period-b', 'n_clicks'),
     Input('end-period-c', 'n_clicks')],
    [State('selected-point', 'data'),
     State('period-times', 'data')]
)
def handle_period_button_click(start_a, start_b, start_c, end_a, end_b, end_c, selected_point, period_times):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    if not selected_point:
        return period_times, ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    selected_time = selected_point['x']
    
    # 更新对应的作息时间
    if trigger_id == 'start-period-a':
        period_times['作息启动期A'] = selected_time
    elif trigger_id == 'start-period-b':
        period_times['作息启动期B'] = selected_time
    elif trigger_id == 'start-period-c':
        period_times['作息启动期C'] = selected_time
    elif trigger_id == 'end-period-a':
        period_times['作息结束期A'] = selected_time
    elif trigger_id == 'end-period-b':
        period_times['作息结束期B'] = selected_time
    elif trigger_id == 'end-period-c':
        period_times['作息结束期C'] = selected_time
    
    # 生成显示文本
    display_text = html.Div([
        html.H5("已设置的作息时间：", style={'marginBottom': '10px', 'fontSize': '14px'}),
        html.Div(f"作息启动期A: {period_times['作息启动期A'] or '未设置'}", style={'marginBottom': '5px', 'fontSize': '12px'}),
        html.Div(f"作息启动期B: {period_times['作息启动期B'] or '未设置'}", style={'marginBottom': '5px', 'fontSize': '12px'}),
        html.Div(f"作息启动期C: {period_times['作息启动期C'] or '未设置'}", style={'marginBottom': '5px', 'fontSize': '12px'}),
        html.Div(f"作息结束期A: {period_times['作息结束期A'] or '未设置'}", style={'marginBottom': '5px', 'fontSize': '12px'}),
        html.Div(f"作息结束期B: {period_times['作息结束期B'] or '未设置'}", style={'marginBottom': '5px', 'fontSize': '12px'}),
        html.Div(f"作息结束期C: {period_times['作息结束期C'] or '未设置'}", style={'marginBottom': '5px', 'fontSize': '12px'})
    ])
    
    return period_times, display_text

# 回调函数：更新数据表格
@app.callback(
    Output('data-table', 'children'),
    [Input('data-store', 'data')]
)
def update_table(data):
    if not data:
        return ""
    
    df = pd.DataFrame(data)
    
    # 创建表格
    table_header = [html.Th(col) for col in df.columns]
    table_rows = []
    
    for i in range(min(10, len(df))):  # 只显示前10行
        row = [html.Td(f"{df.iloc[i][col]:.3f}" if isinstance(df.iloc[i][col], float) else str(df.iloc[i][col])) 
               for col in df.columns]
        table_rows.append(html.Tr(row))
    
    return html.Table([html.Thead(html.Tr(table_header)), html.Tbody(table_rows)])

# 回调函数：下载CSV
@app.callback(
    Output('download-dataframe-csv', 'data'),
    [Input('download-csv', 'n_clicks')],
    [State('data-store', 'data'),
     State('period-times', 'data')],
    prevent_initial_call=True
)
def download_csv(n_clicks, data, period_times):
    if not data:
        raise PreventUpdate
    
    df = pd.DataFrame(data)
    
    # 创建一个新的DataFrame，只包含原始数据（A-F列）
    export_df = df[['时间', '平均作息', '作息方差', '作息上界', '作息下界']].copy()
    
    # 添加G-J列，初始化为空
    export_df['作息启动期'] = ''
    export_df['作息启动期A'] = ''
    export_df['作息启动期B'] = ''
    export_df['作息启动期C'] = ''
    
    # 在第1行设置作息启动期信息
    export_df.loc[0, '作息启动期'] = '作息启动期'
    export_df.loc[0, '作息启动期A'] = period_times['作息启动期A'] or ''
    export_df.loc[0, '作息启动期B'] = period_times['作息启动期B'] or ''
    export_df.loc[0, '作息启动期C'] = period_times['作息启动期C'] or ''
    
    # 在第2行设置作息结束期信息
    export_df.loc[1, '作息启动期'] = '作息结束期'
    export_df.loc[1, '作息启动期A'] = period_times['作息结束期A'] or ''
    export_df.loc[1, '作息启动期B'] = period_times['作息结束期B'] or ''
    export_df.loc[1, '作息启动期C'] = period_times['作息结束期C'] or ''
    
    # 限制数值列的小数点后最多6位
    numeric_columns = ['平均作息', '作息方差', '作息上界', '作息下界']
    for col in numeric_columns:
        export_df[col] = export_df[col].apply(lambda x: round(x, 6) if isinstance(x, (int, float)) else x)
    
    return dcc.send_data_frame(export_df.to_csv, '作息分析结果.csv')

# 运行应用
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=10000)
