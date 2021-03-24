from flask import Flask, request, render_template
import requests
import re
from pprint import pprint
import json
import pandas as pd
import sys
import matplotlib.pyplot as plt

import tinder_api

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html')

def get_fb_id(access_token):
    if "error" in access_token:
        return {"error": "access token could not be retrieved"}
    """Gets facebook ID from access token"""
    req = requests.get(
        'https://graph.facebook.com/me?access_token=' + access_token)
    return req.json()["id"]

from datetime import datetime
import pytz

@app.route('/submit', methods=['POST'])
def submit():
	# get fb token and ID from user input
	fb_access_token = re.search(r"access_token=([\w\d]+)", request.form['text']).groups()[0]
	# fb_user_id = '1004334432928490'
	fb_user_id = get_fb_id(fb_access_token)
	# get tinder token and update api headers 
	# tinder_api.get_auth_token(fb_access_token, fb_user_id)
	# To check you are authorized 
	# print("auth verified: {}".format(tinder_api.authverif(fb_access_token, fb_user_id)))

	# save to file to reduce frequency of API calls 
	my_profile = tinder_api.get_self()
	# all_matches = tinder_api.all_matches()
	updates = tinder_api.get_updates()

    ###### saving user data
	# now = str(datetime.now(pytz.utc))

    # file = open('user_data.json')
    # user_data = json.load(file)
    # user = user_data["Billy"]

    # # user = user_data["Billy"]["profile"]
    # for name in ["profile", "updates"]: # "matches"
    #     # TODO: matches is a subset of updates i think, eliminate
    #     if name not in user:
    #         user[name] = []

    # # my bio, photo scores, and my matches' bios change over time so we want to save time series data
    # user["profile"].append(my_profile)
    # user["profile"][-1]["romeo_ai_saved_at"] = now
    # user["updates"] = [user["updates"]]
    # user["updates"].append(updates)
    # user["updates"][-1]["romeo_ai_saved_at"] = now
    # # user["matches"] = all_matches
    # # user["matches"][len(user["matches"]) - 1]["romeo_ai_saved_at"] = now

	####### requires time series saved data

    # def plot_gb_time_series(df, ts_name, gb_name, value_name, figsize=(20,7), title=None):
	# 	'''
	# 	Runs groupby on Pandas dataframe and produces a time series chart.

	# 	Parameters:
	# 	----------
	# 	df : Pandas dataframe
	# 	ts_name : string
	# 			The name of the df column that has the datetime timestamp x-axis values.
	# 	gb_name : string
	# 			The name of the df column to perform group-by.
	# 	value_name : string
	# 			The name of the df column for the y-axis.
	# 	figsize : tuple of two integers
	# 			Figure size of the resulting plot, e.g. (20, 7)
	# 	title : string
	# 			Optional title
	# 	'''
	# 	xtick_locator = matplotlib.dates.DayLocator(interval=1)
	# 	xtick_dateformatter = matplotlib.dates.DateFormatter('%m/%d/%Y')
	# 	fig, ax = plt.subplots(figsize=figsize)
	# 	for key, grp in df.groupby([gb_name]):
	# 			ax = grp.plot(ax=ax, kind='line', x=ts_name, y=value_name, label=key, marker='o')
	# 	ax.xaxis.set_major_locator(xtick_locator)
	# 	ax.xaxis.set_major_formatter(xtick_dateformatter)
	# 	ax.autoscale_view()
	# 	ax.legend(loc='upper left')
	# 	_ = plt.xticks(rotation=90, )
	# 	_ = plt.grid()
	# 	_ = plt.xlabel('')
	# 	_ = plt.ylim(0, df[value_name].max() * 1.25)
	# 	_ = plt.ylabel(value_name)
	# 	if title is not None:
	# 			_ = plt.title(title)
	# 	_ = plt.show()

	# 	photo_df = pd.DataFrame()
	# 	for date in my_profile:
	# 		timestamp_str = date["romeo_ai_saved_at"]
	# 		for picture in date["photos"]:
	# 				if picture['type'] != 'image' or "score" not in picture.keys():
	# 						continue
	# 				photo_id = picture["id"]
	# 		#         rank = int(idx) # rank as given by the API can change
	# 				score = picture["score"]
	# 				photo_df = photo_df.append({"timestamp": datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f%z'), "id": photo_id, "score": score}, ignore_index=True)
				
	# 	# pprint(photo_df)
	# 	plot_gb_time_series(photo_df, 'timestamp', 'id', 'score', figsize=(10, 5), title="Profile Photo Performance Over Time")

	# 	total_photo_perf_df = photo_df[["score", "timestamp"]].groupby("timestamp").sum()
	# import pdb; pdb.set_trace()
	from PIL import Image

	my_id = my_profile["_id"]
	ranking = 0
	num_non_photos = 0
	return_var = "<h1>Your Profile Photos' Performance</h1><br/><h2>The relative performance scores of your Tinder photos follows. The higher the score, the more often the photo is swiped right on. You may want to replace your worst scoring photos!<br/><br/><pre>Photo Rank     Success Score</pre></h2>"

	while ranking < len(my_profile['photos']) - num_non_photos:
		for n, p in enumerate(my_profile['photos']):
			if p['type'] != 'image':
				num_non_photos += 1
				continue
			score = p['score'] if "score" in p.keys() else "unknown"
			Image.open(requests.get(p['url'], stream=True).raw)
			return_var += '<h2><pre>     <a href="{}">{}</a>         {}</pre></h2><br/>'.format(p['url'], n, score)
			ranking += 1
	# password!23


	return return_var

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)