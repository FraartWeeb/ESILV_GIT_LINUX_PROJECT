#dashboard.py

import dash

import numpy as np
import pandas as pd
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from datetime import date
from dash import dash_table
from datetime import datetime

#heure_actuelle = datetime.now().time()


today = date.today()
app = dash.Dash(__name__)

app.layout = html.Div([
        dcc.Interval(id='interval-component', interval=5 * 60 * 1000, n_intervals=0),

            # graph
            dcc.Graph(id='gold-price-graph'),

            # bouton Moving average
            dcc.Checklist(
                id="ma-toggle",
                options=[{"label": "Moving Average", "value": "show"}],
                value=[]),

            # tableau daily report
            html.Div([
                html.H2(children=f'Daily Report of {today}', style={'marginTop': 20, 'marginBottom': 10}),
                dash_table.DataTable(
                    id='daily-report-table',
                    columns=[
                        {'name': 'Type', 'id': 'type'},
                        {'name': 'Hour', 'id': 'hour'}, # Hour on Ubuntu = -2h
                        {'name': 'Value', 'id': 'value'}],
                    data=[])])
])

def movingAverage(values, n, weights=None):
        # get window size
        window_size = n
        if weights is None:
            # if values don't have a weight then create a window size list of 1
            weights = [1.0 / window_size] * window_size
            # generate the average for each window size list of value
            rolling_average = np.convolve(values, weights, mode='valid')
        return np.array(rolling_average)

def calculate_volatility(data):
        returns = np.log(data / data.shift(1))
        volatility = np.sqrt(252) * np.std(returns)
        return volatility

def getDailyReport(dataframe):
        #today = date.today()
        dailyData = dataframe[dataframe['Date'].dt.date == today]

        # get first and last gold value for each ours
        cloOp = dailyData.groupby(pd.Grouper(key='Date', freq='H')).agg({'GoldValue': ['first', 'last']})

        # select the closure and opening gold values
        date_op = f'{today} 07:00:00'
        date_clo = f'{today} 16:00:00'
        closure = pd.DataFrame(cloOp["GoldValue"]["last"].loc[cloOp.index == pd.to_datetime(date_clo)])
        opening = pd.DataFrame(cloOp["GoldValue"]["first"].loc[cloOp.index == pd.to_datetime(date_op)])

        # min gold value in row 0 and max gold value in row 2
        minMax = dailyData.sort_values('GoldValue').iloc[[0, -1]].set_index(['Date'])

        # get the daily volatility
        if(len(dailyData["GoldValue"])==0):
            volatility = 0
        else:
            volatility = calculate_volatility(pd.Series(dailyData["GoldValue"]))

        return minMax, closure, opening, volatility

def toFloat(s):
        # take away 'espace insecable'
        s = s.replace('\u202f', '')
        # take away \0€
        s = s[:-3]
        # convert gold value to float
        return float(s.replace(',', '.'))


def dataLoading(dataPath):
        data = pd.read_csv(dataPath, header=None, sep=" ")

        # merge date and hour
        data.iloc[:, 0] = data.apply(lambda x: str(x[0]) + " " + str(x[1]), axis=1)

        # keep only date/hour column and gold value
        data = data.iloc[:, [0, 2]]
        data.columns = ["Date", "GoldValue"]

        # get data proper type
        data["Date"] = pd.to_datetime(data["Date"])
        data['GoldValue'] = data['GoldValue'].apply(toFloat)

        return data

@app.callback(
        [Output('gold-price-graph', 'figure'), Output('daily-report-table', 'data')],
        [Input('interval-component', 'n_intervals'), Input('ma-toggle', 'value')]
        )

def update_graph(n,ma_toggle):
        #load the gold value data
        data = dataLoading("/home/ec2-user/Scrapping/gold_data.csv")

        #create the graph for the time serie
        graph_data =[dict(x=data["Date"], y=data['GoldValue'], type='line',name="Gold Value")]

        #get de moving average
        n=24
        ma = movingAverage(data["GoldValue"].values,n)
        if "show" in ma_toggle :
            graph_data.append(dict(x=data["Date"][n-1:], y=ma, type='line', name=f'{n} points :\n{n*5//60} hours Moving Average'))

        #Indication de vente
        last_ma = ma[-1]
        Actual_price = data["GoldValue"].iloc[-1]


        indication = "Hold"
        if(Actual_price-last_ma > 0.01):
            indication = "Short"
        if(Actual_price - last_ma < -0.01):
            indication = "Long"

        #create de final figure
        figure= {
            'data': graph_data,
            'layout': {
                    'title': {
                            'text': 'Gold Value Time Series',
                            'style': {'marginTop': 20, 'marginBottom': 10}
                            },
                    'showlegend': True,
                    }}

        #get the daily report
        minMax,closure,opening,vol = getDailyReport(data)
        report = []

        #create the report

        if(len(minMax["GoldValue"])<=1):
            report.append({'type': "Min & Max", 'hour': "","value":"Not available"})
        else:
            report = [
                {'type': "Min", 'hour': f'{minMax.index[0].hour}h{minMax.index[0].minute}',"value":minMax["GoldValue"][0]},
                {'type': "Max", 'hour': f'{minMax.index[1].hour}h{minMax.index[1].minute}',"value":minMax["GoldValue"][1]}]

        if(len(opening["first"])==0):
            report.append({'type': "France Opening", 'hour': "","value":"Not available"})
        else:
            report.append({'type': "France Opening", 'hour': f'{opening.index[0].hour}h{opening.index[0].minute}',"value":opening["first"][0]})

        if(len(closure["last"])==0):
            report.append({'type': "France Closure", 'hour': "","value":"Not available"})
        else:
            report.append({'type': "France Closure", 'hour':f'{closure.index[0].hour}h{closure.index[0].minute}',"value":closure["last"][0]})

        report.append({'type': "Daily Vol", 'hour': f"{today}","value": f'{vol}%'})
        report.append({'type': "Sale Indication", 'hour': f'{data["Date"].iloc[-1].hour}h{data["Date"].iloc[-1].minute}',"value": f'{indication}'})

        return figure,report

if __name__ == '__main__':
        app.run_server(debug=True,host="0.0.0.0",port =8050)


