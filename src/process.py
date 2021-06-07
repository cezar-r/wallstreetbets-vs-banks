import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

KEY = '919abee0cf38b0288f06795a2303033c'

def open_json(ticker):
	f = open(f'../data/{ticker}_data.txt',)
	data = json.load(f)
	df = pd.DataFrame(data[ticker])
	return df


def change(date):
	date = date.split('-')	# ['2021', '06', '04']
	if int(date[2]) - 7 < 0:
		from_30 = 7 - int(date[2])
		date[1] = '0' + str(int(date[1]) - 1)
		date[2] = str(30 - from_30)
	else:
		date[2] = str(int(date[2]) - 7)
		if len(date[2]) == 1:
			date[2] = '0' + date[2]
	date = '-'.join(date)
	return date

def change_dates(start, end):
	return change(start), change(end)
	


def get_stock_data(ticker):
	data_dict = {}
	s = '2021-06-04'
	e = '2021-05-27'
	while e != '2021-05-06':
		url = f'http://api.marketstack.com/v1/intraday?access_key={KEY}&symbols={ticker}&date_from={e}&date_to={s}'
		response = requests.get(url)
		try:
			json_data = json.loads(response.text)
		except:
			time.sleep(2)
			url = f'http://api.marketstack.com/v1/intraday?access_key={KEY}&symbols={ticker}&date_from={e}&date_to={s}'
			response = requests.get(url)
			json_data = json.loads(response.text)
		data = json_data['data']
		for i in data:

			data_dict[i['date'][:10] + ' ' + i['date'][11:13]] = i['low'] + ((i['high'] - i['low'])/2)

		s, e = change_dates(s, e)

	return data_dict

	# return dict {timestamp : price}



def display(data, ticker):

	stock_data = get_stock_data(ticker)
	stock_x = list(stock_data.keys())[::-1]
	stock_x = [i + ':00 am' if int(i[:2]) < 12 else i + ':00 pm' for i in stock_x]
	stock_y = list(stock_data.values())[::-1]
	stock_y = [i / max(stock_y) for i in stock_y]

	plt.style.use("dark_background")
	fig, ax = plt.subplots(figsize=(18, 9))

	y = data.iloc[0]
	x = [i + ':00 am' if int(i[:2]) < 12 else i + ':00 pm' for i in data][::-1][140:]
	y = [j[0] for j in y.values][::-1]
	y = [i/max(y) for i in y][140:]

	plt.plot(x, y, label = 'engagement')
	plt.plot(stock_x, stock_y, linewidth = 4, color = 'purple', label = ticker)
	plt.xticks(x[::20], rotation=45)
	plt.tight_layout()
	plt.legend()
	plt.savefig(f'../images/{ticker}_eng_vs_price.png')
	#plt.show()

def display_eng():
	tickers = ['GME', 'AMC', 'BBBY', 'BB', 'SNDL', 'TLRY', 'NOK']
	for ticker in tickers:

		d = open_json(ticker)
		display(d, ticker)

'''
d = open_json("AMC")
display(d, "AMC")
'''

display_eng()

