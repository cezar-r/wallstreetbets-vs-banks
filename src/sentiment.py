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



def display(data, ticker):
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
	plt.savefig(f'../images/price_vs_sentiment/{ticker}_price_vs_sent.png')


tickers = ['AMC', 'GME', 'BB', 'SNDL', 'TLRY', 'NOK']
for ticker in tickers:

	d = open_json(ticker)
	display(d, ticker)