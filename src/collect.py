import requests
import json
import time
from datetime import datetime, timedelta

#url = 'https://api.pushshift.io/reddit/search/comment/?q=doge&subreddit=wallstreetbets&sort=asc&size=1000&after=30d'
'''
UTC_datetime = datetime.datetime.utcnow()
UTC_datetime_timestamp = float(UTC_datetime.strftime("%s"))
local_datetime_converted = datetime.datetime.fromtimestamp(UTC_datetime_timestamp)

'''

def query_eng(ticker):
	s = 2880
	e = 2890
	mentions = 0
	upvotes = 0
	data = ''
	data_dict = {}
	while s < 45000:
		now = datetime.now()
		url = f'https://api.pushshift.io/reddit/search/comment/?q=amc&subreddit=wallstreetbets&sort=asc&size=100&fields=body,author,score,created_utc&before={str(s)}m&after={str(e)}m'
		response = requests.get(url)
		try:
			json_data = json.loads(response.text)
		except:
			time.sleep(2)
			url = f'https://api.pushshift.io/reddit/search/comment/?q=amc&subreddit=wallstreetbets&sort=asc&size=100&fields=body,author,score,created_utc&before={str(s)}m&after={str(e)}m'
			response = requests.get(url)
			json_data = json.loads(response.text)
		data = json_data['data']
		if data != []:
			
			cur_day = str(datetime.fromtimestamp(data[0]['created_utc']))[:13]
		
		for comment in data:
			upvotes += comment['score']

		if cur_day in data_dict:
			data_dict[cur_day][0] += len(data)
			data_dict[cur_day][1] += upvotes
		else:
			data_dict[cur_day] = [len(data), upvotes]

		# end of loop
		s += 20
		e += 20
		upvotes = 0
		print(f'Completed loop, s = {s}')
		print(f'{(45000-s)/20} loops to go')
		elapsed = datetime.now() - now
		print(f'Estimated wait time: {elapsed * ((45000-s)/20)}')

	json_contents = {}
	json_contents[ticker] = []
	json_contents[ticker].append(data_dict)
	with open(f'{ticker}_data.txt', 'w') as f:
		json.dump(json_contents, f)

	return mentions, upvotes


def query_text(ticker):
	s = 2880
	e = 2890
	mentions = 0
	upvotes = 0
	data = ''
	data_dict = {}
	while s < 45000:
		comments = []
		now = datetime.now()
		url = f'https://api.pushshift.io/reddit/search/comment/?q={ticker}&subreddit=wallstreetbets&sort=asc&size=100&before={str(s)}m&after={str(e)}m'
		response = requests.get(url)
		try:
			json_data = json.loads(response.text)
		except:
			time.sleep(2)
			url = f'https://api.pushshift.io/reddit/search/comment/?q={ticker}&subreddit=wallstreetbets&sort=asc&size=100&before={str(s)}m&after={str(e)}m'
			response = requests.get(url)
			json_data = json.loads(response.text)
		data = json_data['data']
		if data != []:
			cur_day = str(datetime.fromtimestamp(data[0]['created_utc']))[:13]
		else:
			s += 20
			e += 20
			comments = []
			continue
		
		for comment in data:
			comments.append(comment['body'])

		if cur_day in data_dict:
			data_dict[cur_day].extend(comments)
		else:
			data_dict[cur_day] = []
		s += 20
		e += 20
		comments = []
		print(f'Completed loop, s = {s}')
		print(f'{(45000-s)/20} loops to go')
		elapsed = datetime.now() - now
		print(f'Estimated wait time: {elapsed * ((45000-s)/20)}')

	json_contents = {}
	json_contents[ticker] = []
	json_contents[ticker].append(data_dict)
	with open(f'../data/comment_data/{ticker}_comments.txt', 'w') as f:
		json.dump(json_contents, f)



tickers = ['AMC', 'GME']

def query_all_eng():
	for ticker in tickers:
		query_eng(ticker)


def query_all_text():
	for ticker in tickers:
		query_text(ticker.lower())

query_all_text()