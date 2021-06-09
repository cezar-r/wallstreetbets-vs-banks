import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from process import KEY

# open json file for each stock
# for each date in josn file, go through each comment 
# for each comment, use sid.polarity_scores(comment)
# 		calculate average sentiment (compund) for each date
# 		graph sentiment vs max of stock price
# also
#		calculate dif between postive vs negative sentiment for each date
#		graph differnce using fillbetween


sid = SentimentIntensityAnalyzer()


def open_json(ticker):
	f = open(f'../data/comment_data/{ticker}_comments.txt',)
	data = json.load(f)
	df = pd.DataFrame(data[ticker.lower()]).T
	return df


def text_to_score(x):
	if x == []:
		return 0
	total = 0
	for sentence in x:
		sentiment = sid.polarity_scores(sentence)
		total += sentiment['compound']
	return total / len(x)


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


def stock_plot_data(ticker):
	stock_data = get_stock_data(ticker)
	stock_x = list(stock_data.keys())[::-1]
	#stock_x = [i + ':00 am' if int(i[:2]) < 12 else i + ':00 pm' for i in stock_x]
	stock_y = list(stock_data.values())[::-1]
	return stock_x[1:], stock_y


def display_rel_max(data, ticker):
	stock_x, stock_y = stock_plot_data(ticker)
	stock_y = [i/max(stock_y) for i in stock_y][1:]

	data['scores'] = data.iloc[:, 0].apply(text_to_score)
	data.drop(data.columns[0], axis=1, inplace=True)
	data_t = data.T 

	x = data.index.values.tolist()[::-1]
	new_x = []
	for date in x:
		if date in stock_x:
			new_x.append(date)

	new_y = []
	for date in new_x:
		new_y.append(data_t.loc['scores', date])

	plt.style.use("dark_background")
	fig, ax = plt.subplots(figsize=(18, 9))
	plt.plot(stock_x, stock_y, color='fuchsia', linewidth = 3, label = f'${ticker} Share Price')
	plt.plot(new_x, new_y, label = f'Sentiment')
	plt.xlabel("Date")
	plt.xticks(new_x[::8], rotation = 45)
	plt.ylabel("Relative to maximum")
	plt.title(f'${ticker} Share Price vs Sentiment')
	plt.legend()
	#plt.show()
	#plt.savefig(f'../images/price_vs_sentiment/{ticker}_price_vs_sent.png')

def coefficient(x, y):
	smol = min(len(x), len(y))
	y = [y[i] for i in range(smol)]
	return np.corrcoef(x, y)[0, 1]


def copy(arr):
	return [i for i in arr]


def rotate(arr, n):
	return arr[n:] + arr[:n]


def trim(arr, y_arr, correct_arr, prev = True):
	idx = arr.index(correct_arr[0])
	if prev:
		arr = arr[idx:]
		y_arr = y_arr[idx:]
	else:
		arr = arr[:idx]
		y_arr = y_arr[:idx]
	return arr, y_arr


def corr_diff_day(eng, stock):
	x, y = eng
	prev_x = copy(x)
	future_x = copy(x)
	prev_y = copy(y)
	future_y = copy(y)
	stock_x, stock_y = stock
	
	prev_x = rotate(prev_x, -1)
	future_x = rotate(future_x, 1)
	prev_y = rotate(prev_y, -1)
	future_y = rotate(future_y, 1)
	
	prev_x, prev_y = trim(prev_x, prev_y, x)
	future_x, future_y = trim(future_x, future_y, x, prev = False)

	corr_prev =  coefficient(np.array(prev_y), np.array(stock_y[1:]))
	corr_future = coefficient(np.array(future_y), np.array(stock_y[len(stock_y) - len(future_y):]))
	return corr_prev, corr_future


def display_daily_rel_max(data, ticker):

	stock_x, stock_y = stock_plot_data(ticker)
	stock_y = [i/max(stock_y) for i in stock_y][1:]

	daily_stock_x = [i[:10] for i in stock_x]

	stock_daily_totals = {}
	for i, time in enumerate(daily_stock_x):
		if time in stock_daily_totals:
			stock_daily_totals[time].append(stock_y[i])
		else:
			stock_daily_totals[time] = [stock_y[i]]

	stock_daily_avgs = {}
	for k in stock_daily_totals:
		stock_daily_avgs[k] = sum(stock_daily_totals[k])/len(stock_daily_totals[k])


	data['scores'] = data.iloc[:, 0].apply(text_to_score)
	data.drop(data.columns[0], axis=1, inplace=True)
	data_t = data.T 

	x = data.index.values.tolist()[::-1]
	new_x = []
	for date in x:
		if date in stock_x:
			new_x.append(date)

	new_x_axis = [i[:10] for i in new_x]

	new_y = []
	for date in new_x:
		new_y.append(data_t.loc['scores', date])

	sent_daily_totals = {}
	for i, time in enumerate(new_x):
		if time in sent_daily_totals:
			sent_daily_totals[time[:10]].append(new_y[i])
		else:
			sent_daily_totals[time[:10]] = [new_y[i]]

	sent_daily_avgs = {}
	for k in sent_daily_totals:
		sent_daily_avgs[k] = sum(sent_daily_totals[k])/len(sent_daily_totals[k])


	plt.style.use("dark_background")
	fig, ax = plt.subplots(figsize=(18, 9))
	plt.plot(list(stock_daily_avgs.keys()), list(stock_daily_avgs.values()), color='mediumslateblue', linewidth = 3, label = f'${ticker} Share Price')
	plt.plot(list(sent_daily_avgs.keys()), list(sent_daily_avgs.values()), label = f'Sentiment % Change')
	plt.xlabel("Date")
	plt.xticks(list(stock_daily_avgs.keys()), rotation = 45)
	plt.ylabel(f"Relative to maximum")
	plt.title(f'${ticker} Share Price vs Sentiment')
	plt.legend()
	#plt.show()
	plt.savefig(f'../images/daily_price_vs_sent/{ticker}_daily_price_vs_sent.png')


	# cur_corr = coefficient(np.array(list(sent_daily_avgs.values())), np.array(list(stock_daily_avgs.values())))
	# prev_corr, future_corr = corr_diff_day((list(sent_daily_avgs.keys()), list(sent_daily_avgs.values())), (list(stock_daily_avgs.keys()), list(stock_daily_avgs.values())))
	# return {'Stock': ticker, 'Same Day Correlation' : cur_corr, "Prev Day Correlation" : prev_corr, "Next Day Correlation" : future_corr}

	'''
	{'Stock': 'AMC', 'Same Day Correlation': 0.1880430994649141, 'Prev Day Correlation': 0.1643244582163266, 'Next Day Correlation': 0.20964264934836863}
	{'Stock': 'GME', 'Same Day Correlation': -0.13353840119143612, 'Prev Day Correlation': -0.26680192916383383, 'Next Day Correlation': -0.07981608799037299}
	{'Stock': 'BB', 'Same Day Correlation': 0.14066300516384844, 'Prev Day Correlation': 0.0004447491674216089, 'Next Day Correlation': 0.12972014328056283}
	{'Stock': 'SNDL', 'Same Day Correlation': -0.3308839745169938, 'Prev Day Correlation': -0.41927300761475034, 'Next Day Correlation': -0.41814679003020616}
	{'Stock': 'TLRY', 'Same Day Correlation': 0.25013672132674425, 'Prev Day Correlation': -0.004957606017787319, 'Next Day Correlation': -0.19683313239289507}
	{'Stock': 'NOK', 'Same Day Correlation': 0.26446406497637365, 'Prev Day Correlation': 0.08285193416749015, 'Next Day Correlation': 0.30708360038714383}
	'''

	


def display_percent(data, ticker):
	stock_x, stock_y = stock_plot_data(ticker)
	stock_y = [(stock_y[i] - stock_y[i-1])/stock_y[i-1] for i in range(1, len(stock_y))]

	data['scores'] = data.iloc[:, 0].apply(text_to_score)
	data.drop(data.columns[0], axis=1, inplace=True)
	data_t = data.T 

	x = data.index.values.tolist()[::-1]
	new_x = []
	for date in x:
		if date in stock_x:
			new_x.append(date)

	new_y = []
	for date in new_x:
		new_y.append(data_t.loc['scores', date])
	new_y = [i/max(new_y) for i in new_y]

	plt.style.use("dark_background")
	fig, ax = plt.subplots(figsize=(18, 9))
	plt.plot(stock_x, stock_y, color='fuchsia', linewidth = 3, label = f'${ticker} Share Price % Change')
	plt.plot(new_x, new_y, label = f'Sentiment % Change')
	plt.xlabel("Date")
	plt.xticks(new_x[::8], rotation = 45)
	plt.ylabel(f"% change")
	plt.title(f'${ticker} Share Price vs Sentiment % Change')
	plt.legend()
	#plt.show()
	plt.savefig(f'../images/price_vs_sentiment_per/{ticker}_price_vs_sent.png')


if __name__ == '__main__':
	tickers = ['AMC', 'GME', 'BB', 'SNDL', 'TLRY', 'NOK']
	for ticker in tickers:

		d = open_json(ticker)
		print(display_daily_rel_max(d, ticker))
		#display_percent(d, ticker)