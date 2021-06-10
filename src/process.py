import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats


KEY = '65779b0496d310893e07ff78a196f383'


def open_json(ticker):
	f = open(f'../data/engagement_data/{ticker}_data.txt',)
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


def stock_plot_data(ticker):
	if __name__ != '__main__':
		print('Oher file called me')
	stock_data = get_stock_data(ticker)
	stock_x = list(stock_data.keys())[::-1]
	stock_x = [i + ':00 am' if int(i[:2]) < 12 else i + ':00 pm' for i in stock_x]
	stock_y = list(stock_data.values())[::-1]
	return stock_x[1:], stock_y


def display(data, ticker):
	stock_x, stock_y = stock_plot_data(ticker)
	stock_y = [i/max(stock_y) for i in stock_y][1:]

	plt.style.use("dark_background")
	fig, ax = plt.subplots(figsize=(18, 9))

	y = data.iloc[0]
	x = [i + ':00 am' if int(i[:2]) < 12 else i + ':00 pm' for i in data][::-1][140:]
	y = [j[0] + j[1]  for j in y.values][::-1]
	y = [i/max(y) for i in y][140:]

	plt.plot(x, y, label = 'Engagement')
	plt.plot(stock_x, stock_y, linewidth = 4, color = 'purple', label = f'${ticker} price')
	plt.xticks(x[::20], rotation=45)
	plt.title(f'${ticker} price vs Wallstreetbets engagement')
	plt.xlabel("Date", fontsize=18)
	plt.ylabel("Relative to maximum", fontsize=16)
	plt.tight_layout()
	plt.legend()
	# plt.savefig(f'../images/price_vs_eng/{ticker}_eng_vs_price.png')
	# plt.show()
	y = [i for i in y[-len(stock_y):]]
	cur_corr = coefficient(np.array(y), np.array(stock_y))
	prev_corr, future_corr = corr_diff_day((x, y), (stock_x, stock_y))
	return {'Stock': ticker, 'Same Day Correlation' : cur_corr, "Prev Day Correlation" : prev_corr, "Next Day Correlation" : future_corr}


def percent_change(x1, x2):
	return (x2-x1)/x1


def coefficient(x, y):
	return np.corrcoef(x, y)[0, 1]


def display_change(data, ticker):
	stock_x, stock_y = stock_plot_data(ticker)
	stock_y = [(stock_y[i] - stock_y[i-1])/stock_y[i-1] for i in range(1, len(stock_y))]

	plt.style.use("dark_background")
	fig, ax = plt.subplots(figsize=(18, 9))

	y = data.iloc[0]
	x = [i + ':00 am' if int(i[:2]) < 12 else i + ':00 pm' for i in data][::-1][140:]
	y = [(y.values[i][0] - y.values[i-1][0])/y.values[i-1][0] for i in range(1, len(y.values))][139:]
	#y = [lambda x : (y.values[x][0] - y.values[x-1][0])/y.values[x][0] for x in range(1, len(y.values))]


	plt.plot(x, y, label = f'% change of ${ticker} engagement reddit')
	plt.plot(stock_x, stock_y, linewidth=4, color='purple', label=f'% change of ${ticker} stock')
	plt.xticks(x[::20], rotation = 45)
	plt.title(f'${ticker} stock price % change vs Wallstreetbets engagement % change')
	plt.ylabel(f'% change')
	plt.tight_layout()
	plt.legend()
	#plt.savefig(f'../images/prices_vs_eng_per/{ticker}_eng_vs_price_per.png')
	
	y = [i for i in y[-len(stock_y):]]
	cur_corr = coefficient(np.array(y), np.array(stock_y))
	prev_corr, future_corr = corr_diff_day((x, y), (stock_x, stock_y))
	return {'Stock': ticker, 'Same Day Correlation' : cur_corr, "Prev Day Correlation" : prev_corr, "Next Day Correlation" : future_corr}


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
	
	prev_x = rotate(prev_x, -10)
	future_x = rotate(future_x, 10)
	prev_y = rotate(prev_y, -10)
	future_y = rotate(future_y, 10)
	
	prev_x, prev_y = trim(prev_x, prev_y, x)
	future_x, future_y = trim(future_x, future_y, x, prev = False)

	corr_prev =  coefficient(np.array(prev_y), np.array(stock_y[5:]))
	corr_future = coefficient(np.array(future_y), np.array(stock_y[5:]))
	return corr_prev, corr_future


def display_daily_avg(data, ticker):
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

	y = data.iloc[0]
	x = [i + ':00 am' if int(i[:2]) < 12 else i + ':00 pm' for i in data][::-1][140:]
	daily_x = [i[:10] for i in data][::-1][140:]
	y = [j[0] + j[1]  for j in y.values][::-1]
	y = [i/max(y) for i in y][140:]

	eng_daily_totals = {}
	for i, time in enumerate(daily_x):
		if time in eng_daily_totals:
			eng_daily_totals[time].append(y[i])
		else:
			eng_daily_totals[time] = [y[i]]

	eng_daily_avgs = {}
	for k in eng_daily_totals:
		eng_daily_avgs[k] = sum(eng_daily_totals[k])/len(eng_daily_totals[k])


	#plt.style.use("dark_background")
	#fig, ax = plt.subplots(figsize=(18,9))

	# plt.plot(list(eng_daily_avgs.keys()), list(eng_daily_avgs.values()), linewidth = 4, label = 'Engagement', solid_capstyle='round')
	# plt.fill_between(list(eng_daily_avgs.keys()), 0, list(eng_daily_avgs.values()), alpha = 0.15)

	# plt.plot(list(stock_daily_avgs.keys()), list(stock_daily_avgs.values()), linewidth = 4, color = 'mediumslateblue', label = f'${ticker} price', solid_capstyle='round')
	# plt.fill_between(list(stock_daily_avgs.keys()), 0, list(stock_daily_avgs.values()), color = 'mediumslateblue', alpha= 0.1)

	# plt.xticks(list(eng_daily_avgs.keys()), rotation=45)
	# plt.title(f'${ticker} price vs Wallstreetbets engagement')
	# plt.xlabel("Date", fontsize=18)
	# plt.ylabel("Relative to maximum", fontsize=16)
	# plt.tight_layout()
	# plt.legend()

	return percent_correct((list(eng_daily_avgs.keys()), list(eng_daily_avgs.values())), (list(stock_daily_avgs.keys()), list(stock_daily_avgs.values())), ticker)
	#plt.show()
	#plt.savefig(f'../images/daily_price_vs_eng/{ticker}_daily_eng_vs_price_per.png')

	# y = [i for i in list(eng_daily_avgs.values())[-len(list(stock_daily_avgs.values())):]]
	# cur_corr = coefficient(np.array(y), np.array(list(stock_daily_avgs.values())))
	# prev_corr, future_corr = corr_diff_day((list(eng_daily_avgs.keys()), list(eng_daily_avgs.values())), (list(stock_daily_avgs.keys()), list(stock_daily_avgs.values())))
	# return {'Stock': ticker, 'Same Day Correlation' : cur_corr, "Prev Day Correlation" : prev_corr, "Next Day Correlation" : future_corr}
	# t_cur = calculate_t_test(np.array(y), np.array(list(stock_daily_avgs.values())), .05)
	# return t_cur


	'''
	High Prev Day Correlation = Following the trend
	High Next Day Correlation = Ahead of the trend
	{'Stock': 'AMC', 'Same Day Correlation': 0.7836734791979197, 'Prev Day Correlation': -0.095002426197534, 'Next Day Correlation': 0.7522435819173727}
	{'Stock': 'GME', 'Same Day Correlation': 0.7015547092161876, 'Prev Day Correlation': -0.15977934508996347, 'Next Day Correlation': 0.6473196702717451}
	{'Stock': 'BB', 'Same Day Correlation': 0.7510425096787338, 'Prev Day Correlation': -0.0005532303271056227, 'Next Day Correlation': 0.7172539412716349}
	{'Stock': 'SNDL', 'Same Day Correlation': 0.7200428404381856, 'Prev Day Correlation': -0.07856040160933374, 'Next Day Correlation': 0.6745332953594741}
	{'Stock': 'TLRY', 'Same Day Correlation': 0.7148534722081824, 'Prev Day Correlation': -0.041808424581382016, 'Next Day Correlation': 0.6758162262791414}
	{'Stock': 'NOK', 'Same Day Correlation': 0.5355591273765817, 'Prev Day Correlation': 0.2730968257985349, 'Next Day Correlation': 0.4012833566220041}


	T-Test 
	AMC (5.141029882342577e-05, True)
	GME (2.1902759648971002e-18, True)
	BB (4.196445396871837e-14, True)
	SNDL (1.7236621209051704e-16, True)
	TLRY (3.989543501641067e-23, True)
	NOK (6.1759986290167304e-30, True)
	'''


def percent_growth(arr):
	arr = [(arr[i] - arr[i-1])/arr[i-1] for i in range(1, len(arr))]
	return arr
	

def calc_predictions(dict1, dict2, key):
	dict1_items = dict1.items()
	dict2_items = dict2.items()

	for i, d in enumerate(dict1_items):
		if i == len(dict2_items):
			return 0
		if d[0] == key:
			idx_of_key = [i for i, e in enumerate(list(dict2_items)) if e[0] == key][0]
			if list(dict1_items)[i][1] > 0 and list(dict2_items)[idx_of_key+1][1] > 0:
				return 1
			else:
				return 0
	return 0


def number_of_up_days(arr):
	up = 0
	for i in arr:
		if i > 0:
			up += 1
	return up


def percent_correct(eng_data, stock_data, ticker):
	eng_x, eng_y = eng_data
	stock_x, stock_y = stock_data

	new_eng_y = copy(eng_y)
	new_stock_y = copy(stock_y)

	percent_change_eng_y = percent_growth(new_eng_y)
	percent_change_stock_y = percent_growth(stock_y)
	
	eng_dict = {}
	for i in range(len(eng_x) - 1):
		eng_dict[eng_x[i]] = percent_change_eng_y[i]

	stock_dict = {}
	for i in range(len(stock_x) - 1):
		stock_dict[stock_x[i]] = percent_change_stock_y[i]

	predictions = 0

	for k in eng_dict:
		if k in stock_dict:
			predictions += calc_predictions(eng_dict, stock_dict, k) 

	positive_days = number_of_up_days(percent_change_stock_y)

	return ticker, (predictions/positive_days)

	'''
	stock on target with engagement / total up days for that stock
	AMC % chance of getting in early: 0.45454545454545453
	GME % chance of getting in early: 0.38461538461538464
	BB % chance of getting in early: 0.3076923076923077
	SNDL % chance of getting in early: 0.2857142857142857
	TLRY % chance of getting in early: 0.3333333333333333
	NOK % chance of getting in early: 0.18181818181818182

	stock follows engagement / total up days for that stock
	AMC % chance of getting in early: 0.45454545454545453
	GME % chance of getting in early: 0.38461538461538464
	BB % chance of getting in early: 0.38461538461538464
	SNDL % chance of getting in early: 0.35714285714285715
	TLRY % chance of getting in early: 0.4166666666666667
	NOK % chance of getting in early: 0.2727272727272727

	stock on target with engagement / total up days for engagement
	AMC % chance of getting in early: 0.45454545454545453
	GME % chance of getting in early: 0.45454545454545453
	BB % chance of getting in early: 0.36363636363636365
	SNDL % chance of getting in early: 0.36363636363636365
	TLRY % chance of getting in early: 0.36363636363636365
	NOK % chance of getting in early: 0.2

	stock follows engagement / total up days for engagement
	AMC % chance of getting in early: 0.45454545454545453
	GME % chance of getting in early: 0.45454545454545453
	BB % chance of getting in early: 0.45454545454545453
	SNDL % chance of getting in early: 0.45454545454545453
	TLRY % chance of getting in early: 0.45454545454545453
	NOK % chance of getting in early: 0.3
	'''


def calculate_t_test(x, y, a):
	_, p_value = stats.ttest_ind(x, y)
	return p_value, p_value < a


def display_eng():
	predictions = {}
	colors = ["mediumslateblue", 'fuchsia', 'springgreen', 'tomato', 'cyan', 'darkorange']
	tickers = ['AMC', 'GME', 'BB', 'SNDL', 'TLRY', 'NOK']
	for ticker in tickers:

		d = open_json(ticker)
		#print(display(d, ticker))
		ticker, probability = 	display_daily_avg(d, ticker)
		predictions[ticker] = probability
	print(predictions)

	plt.style.use("dark_background")
	fig, ax = plt.subplots(figsize=(9, 9))

	plt.bar(list(predictions.keys()), list(predictions.values()), color = 'black', edgecolor = colors, zorder = 1, linewidth = 3)
	plt.bar(list(predictions.keys()), list(predictions.values()), color = colors, alpha = 0.2, zorder = 2)
	plt.title(f"% Chance of Share Price Increase vs Engagement Increase (Next Day)")
	plt.xlabel("Stocks")
	plt.ylabel("Probability of share price increase day after engagement increase")
	#plt.show()
	plt.savefig(f'../images/bar_price_vs_eng_probability/percent_chance_next_day_stock.png')


if __name__ == '__main__':
	display_eng()

