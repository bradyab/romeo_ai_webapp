from flask import Flask, request, render_template
import pdb, traceback, sys
import requests
import re
from pprint import pprint
import json
import pandas as pd
import sys
from datetime import datetime
import pytz

import tinder_api
from features import *

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('form.html')


@app.route('/submit', methods=['POST'])
def submit():
	# start pdb on exception
	try:
		# get fb token and ID from user input
		form_input = '<script type="text/javascript" nonce="9pF6859V">window.location.href="fb464891386855067:\/\/authorize\/#granted_scopes=user_birthday\u00252Cuser_likes\u00252Cuser_photos\u00252Cemail\u00252Cpublic_profile&denied_scopes=&signed_request=yYeXS0tLtJ1fh7X4a0UCLbftKJM5ks20gIRsiSUtjF0.eyJ1c2VyX2lkIjoiMTAwNDMzNDQzMjkyODQ5MCIsImNvZGUiOiJBUUE5S0lJaVlVdDFoXzRodkg3emxldTNsZzBzTWNlcUVTT2JVeDQwd040MUE1dXNJYjZrc19abmhMTGZjUld2ZHFOaXNSMDIyZWRXSi01TG5zMnNQS1VZRzJVaUF5bEVtbHhNWUVZOXkzbWNLdjNxd1NTbFFQc040TnRxY3VPbkVlTzVQUmptOU1SbEtQLVlsemFQQ0ZHM0FiaUhmeTFYVnFweUd1Rl85dUhoT0haaEwwdnJ4TVRsRVZFUC1RaVh5ZlVPeHFzeFBRZDJ4a3UtbmxVTlVmZ3RQc0NkTkQxOHFqRVJPenJJUkw5ZG9nUkFoZHlyQTNKMkdrRHB0cmlUTU9uSnhzZTJBVDZPWFpvMXAzd2dTTVBiQXVpZ1RZQWg3cW45cHpWWWw5bVk5NzZzejdscHVVX3NxbEdaU01tQW1QQ1l0aXJtV0JjMHRteWw4TElmXzdKaGRqYXZMYzFWd0phV3JCVHhEd3RLNFptTVgzTXg2WWRUcmpRelhMT1BEWUVBcXpOUklHVDFfbUw4SndIZGtLanUiLCJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImlzc3VlZF9hdCI6MTYxNjYwNzI4NX0&access_token=EAAGm0PX4ZCpsBAD4j1WHa7hJwvLEXHWEMVZB9sjPBAB1AqHv58CD53Nq7bFxemmlS89eedKkDSWoAJclQA0afqlnf67M2ZAZBnnFloPbvi37hSV5zk2Wgod1PonRDmfSJFWeqjIOLuwvYVlPJae2gTbFQvBZBQAodY0GkUd0MGKctrH9gOCYj8v8B6sLZB2WmGBczX9z33bwVyy6Gm5dlmPeUvD2BEyPx1kvZBDO0989QZDZD&data_access_expiration_time=1624383285&expires_in=5116586&state=\u00257B\u002522challenge\u002522\u00253A\u002522IUUkEUqIGud332lfu\u0025252BMJhxL4Wlc\u0025253D\u002522\u00252C\u0025220_auth_logger_id\u002522\u00253A\u00252230F06532-A1B9-4B10-BB28-B29956C71AB1\u002522\u00252C\u002522com.facebook.sdk_client_state\u002522\u00253Atrue\u00252C\u0025223_method\u002522\u00253A\u002522sfvc_auth\u002522\u00257D";</script>' if request.form['text'] == "" else request.form['text']
		fb_access_token = re.search(r"access_token=([\w\d]+)", form_input).groups()[0]
		fb_user_id = get_fb_id(fb_access_token)
		print(fb_user_id)
		print(fb_access_token)
		# get tinder token and update api headers
		# tinder_api.get_auth_token(fb_access_token, fb_user_id)
		# To check you are authorized
		auth_status, auth_color = ("was successfully authorized!", "green") if tinder_api.authverif(
			fb_access_token, fb_user_id) == True else ("failed to authorize :( If the error persists, report any issues to info@getromeo.ai", "tomato")

		# save to file to reduce frequency of API calls
		user_profile = tinder_api.get_self()
		# all_matches = tinder_api.all_matches()
		user_updates = tinder_api.get_updates()
		user_id = user_profile["_id"]
		###### saving user data
		# file = open('user_data.json')
		# user_data = json.load(file)
		

		# user = user_data["Billy"]
		# for name in ["profile", "updates"]: # "matches"
		#     # TODO: matches is a subset of updates i think, eliminate
		#     if name not in user:
		#         user[name] = []

		# # my bio, photo scores, and my matches' bios change over time so we want to save time series data
		# now = str(datetime.now(pytz.utc))
		# user["profile"].append(user_profile)
		# user["profile"][-1]["romeo_ai_saved_at"] = now
		# user["updates"] = [user["updates"]]
		# user["updates"].append(user_updates)
		# user["updates"][-1]["romeo_ai_saved_at"] = now
		# user_data[user_id] = user


		###############
		# from replit import db

		# with open('user_data.json', 'w') as fp:
		#     json.dump(user_data, fp, default=str)
		# # TODO: remove duplicate entries. convert to csv?

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
		# 	for date in user_profile:
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

		photo_scores = get_photo_scores(user_profile['photos'])

		############# opening lines analysis

		# this takes a while and calls the tinder API many times if true
		get_extra_match_info = False

		old_messages_df = pd.DataFrame()
		n = 0
		for match in user_updates["matches"]:
			match_name = match.get("person").get("name")
			match_bio = match.get("person").get("bio")
			if get_extra_match_info:
				# don't call this too much, lest we get banned
				# TODO: save this info to DB. If data exists in DB, check DB for their info closest to the time of opener being sent. Don't add to DB unless values change
				extra_match_info = tinder_api.get_person(
					match.get("person").get("_id")).get("results")
				n += 1
				if extra_match_info:
					# TODO: concat all jobs in list
					# TODO: check spotify refs
					match_school = ""
					try:
						for idx, school in enumerate(
								extra_match_info.get("schools")):
							match_school += extra_match_info.get(
								"schools")[idx].get('name').lower()
					except:
						continue
					try:
						match_job_name = extra_match_info.get("jobs")[0].get(
							'title').get('name').lower()
					except:
						match_job_name = ""
					try:
						match_job_company = extra_match_info.get("person").get(
							"jobs")[0].get('company').get('name').lower()
					except:
						match_job_company = ""

					match_job = match_job_name + match_job_company

			for message in match['messages']:
				if get_extra_match_info:
					message.update({
						"match_name": match_name,
						"message_lower_case": message["message"],
						"match_bio": match_bio,
						"match_job": match_job,
						"match_school": match_school
					})
				else:
					message.update({
						"match_name": match_name,
						"message_lower_case": message["message"],
						"match_bio": match_bio
					})
				old_messages_df = old_messages_df.append(message,
														ignore_index=True)

		# this can be empty if they haven't sent messages
		if old_messages_df.empty:
			pass
		else:
			old_messages_df["romeo_ai_user_id"] = user_id

			import numpy as np
			import math
			import scipy.stats
			from fuzzywuzzy import process, fuzz
			import pprint
			pd.set_option('display.max_colwidth', None)
			pd.set_option('display.max_rows', None)

			# TODO: not all matches have conversations??
			messages_df = old_messages_df
			messages_df["is_bucketed"], messages_df["is_hey"] = 0, 0
			messages_df["school_ref"], messages_df[
				"school_ref_str"], messages_df["bio_ref"], messages_df[
					"bio_ref_str"], messages_df["job_ref"], messages_df[
						"job_ref_str"] = "", "", "", "", "", ""

			grouped = messages_df.groupby(['romeo_ai_user_id', 'match_id'])  #.apply()

			bio_ngrams_n = 2
			job_ngrams_n, school_ngrams_n = 1, 1

			from nltk.util import ngrams
			from collections import Counter
			from itertools import chain
			import string
			import spacy

			sp = spacy.load('en_core_web_sm')  #en-core-web-sm-abd') #
			stop_words = sp.Defaults.stop_words | set(["", " "])

			# match substrings in messages with those in bio, job, school, etc
			def fuzzy_string_match(df, row_idx, read_col_name, write_col_name,
								ngrams_1, n):
				# get ngrams from message
				#                                                     stringIn.translate(stringIn.maketrans("",""), string.punctuation)
				ngrams_2 = ngrams(
					df.loc[row_idx, "message_lower_case"].translate(
						str.maketrans('', '', string.punctuation)).split(" "),
					n)
				# count occurrences of each n-gram in both strings
				counter = Counter(chain(ngrams_1, ngrams_2))

				# if any ngrams were found 2+ times,
				if any(v > 1 for v in counter.values()):
					joined = ""
					# TODO: this needs optimization
					for k, v in counter.items():
						if v > 1:
							for word in k:
								# TODO: swap words with synonyms
								# if the ngram occurs in both strings, record it
								if word not in stop_words and word.lower(
								) in df.loc[row_idx, read_col_name].lower(
								) and word.lower() in df.loc[
										row_idx, "message_lower_case"]:
									joined += " " + word
							# to separate ngrams for debug
							if len(joined) > 1:
								joined += ", "
					if len(joined) > 1:
						df.loc[row_idx, write_col_name] = 1
						df.loc[row_idx, write_col_name + "_str"] = joined

			# todo: capture openers with multiple messages within 5 minues of each other
			# TODO: n of various lengths

			for group_idx, group in grouped:
				convo_depth = 0
				for row_idx, row in group.iterrows():
					# remove spam from Billy's tinder 
					if row["from"] == '58324a72815c629704a4cfba' and (any([substring in row["message"] for substring in ["It would help*", "I'm building an app"]]) or\
					(datetime.strptime(row["sent_date"].replace("Z",""), '%Y-%m-%dT%H:%M:%S.%f') >= datetime.strptime("2021-02-23T02:11:26.531", '%Y-%m-%dT%H:%M:%S.%f') and datetime.strptime(row["sent_date"].replace("Z",""), '%Y-%m-%dT%H:%M:%S.%f')<= datetime.strptime("2021-02-23T03:17:12.469", '%Y-%m-%dT%H:%M:%S.%f'))):
						messages_df = messages_df.drop(index=row_idx)
						continue

					# collate bio, job, and school info 1x per match
					if not convo_depth:
						bio_ngrams = ngrams(
							str(row["match_bio"]).lower().translate(
								str.maketrans('', '',
											string.punctuation)).split(" "),
							bio_ngrams_n) if row["match_bio"] else ""

						if get_extra_match_info:
							job_ngrams = ngrams(
								str(row["match_job"]).translate(
									str.maketrans(
										'', '',
										string.punctuation)).split(" "),
								job_ngrams_n) if row["match_job"] else ""
							school_ngrams = ngrams(
								str(row["match_school"]).translate(
									str.maketrans(
										'', '',
										string.punctuation)).split(" "),
								school_ngrams_n) if row["match_school"] else ""

						messages_df.loc[row_idx, "is_opener"] = 1 if group_idx[
							0] == row["from"] else 0

					convo_depth += 1
					#             if row["match_bio"] and "5 kids" in row["match_bio"]:
					#                 nn = 1
					#                 messages_df.loc[row_idx, "is_opener"]
					#                 print(group_idx[0] == row["from"])

					# calculate opener stats. this could probably be refactored as a bunch of .applys
					if messages_df.loc[row_idx, "is_opener"] == 1:
						# fuzzy pattern matching
						messages_df.loc[
							row_idx,
							"match_name_in_message_token_set_ratio"] = fuzz.token_set_ratio(
								row["match_name"], row["message"])
						messages_df.loc[
							row_idx,
							"whats_up_partialratio"] = fuzz.partial_ratio(
								"what's up", row["message_lower_case"])
						messages_df.loc[row_idx,
										"hey_sort"] = fuzz.token_sort_ratio(
											"hey", row["message_lower_case"])
						messages_df.loc[
							row_idx, "hey_name_sort"] = fuzz.token_sort_ratio(
								"hey " + row["match_name"], row["message"])

						#         fuzz.token_set_ratio("hey " + row["match_name"], row["message"])
						#         messages_df.loc[row_idx, "hey_match_name_wratio"] = fuzz.WRatio("hey " + row["match_name"], row["message"])
						#         messages_df.loc[row_idx, "bio_wratio"] = fuzz.WRatio(row["match_bio"], row["message"])
						#         messages_df.loc[row_idx, "fuzzratio"] = fuzz.ratio("hey " + row["match_name"], row["message"])
						#         messages_df.loc[row_idx, "partialratio"] = fuzz.partial_ratio("hey " + row["match_name"], row["message"])
						#         messages_df.loc[row_idx, "set"] = fuzz.token_set_ratio("hey " + row["match_name"], row["message"])

						# fuzzy string match to bucket openers
						# TODO: decide which should be mutually exclusive
						if messages_df.loc[row_idx,
										"whats_up_partialratio"] >= 90:
							messages_df.loc[row_idx,
											"is_whats_up"], messages_df.loc[
												row_idx,
												"is_bucketed"] = (1, 1)
						elif messages_df.loc[
								row_idx,
								"hey_name_sort"] >= 70 and messages_df.loc[
									row_idx, "is_bucketed"] == 0:
							messages_df.loc[
								row_idx, "is_hey_match_name"], messages_df.loc[
									row_idx, "is_bucketed"] = (1, 1)
						elif messages_df.loc[
								row_idx, "hey_sort"] >= 55 and messages_df.loc[
									row_idx, "is_bucketed"] == 0:
							# for one-word responses we can be more precise
							messages_df.loc[row_idx,
											"is_hey"], messages_df.loc[
												row_idx,
												"is_bucketed"] = (1, 1)
						if row["match_bio"]:
							# TODO: FP with billy match bio "Looking for the Sokka to my Suki | Can probably beat you in Mario Kart 8 | Incredibly mediocre | 🇰🇷🇯🇵	"
							fuzzy_string_match(messages_df,
											row_idx,
											read_col_name="match_bio",
											write_col_name="bio_ref",
											ngrams_1=bio_ngrams,
											n=bio_ngrams_n)
						if get_extra_match_info:
							if row["match_school"]:
								fuzzy_string_match(
									messages_df,
									row_idx,
									read_col_name="match_school",
									write_col_name="school_ref",
									ngrams_1=school_ngrams,
									n=school_ngrams_n)
							if row["match_job"]:
								fuzzy_string_match(messages_df,
												row_idx,
												read_col_name="match_job",
												write_col_name="job_ref",
												ngrams_1=job_ngrams,
												n=job_ngrams_n)

						# did they respond to the message?
						this_msg_and_all_after = group[
							group['sent_date'] >= row['sent_date']]
						messages_df.loc[row_idx, "got_response"] = 1 if len(
							this_msg_and_all_after["from"].unique()) > 1 else 0
						messages_df.loc[
							row_idx,
							"long_convo"] = 1 if len(group) > 10 else 0

			# messages_df[["message", "match_bio", "bio_ref", "bio_ref_str"]][((messages_df["is_opener"] == 1))]

			# map col names to axis labels
			display_name_mapping = {
				"bio reference": "bio_ref",
				"hey": "is_hey",
				"hey <name>": "is_hey_match_name",
				"what's up": "is_whats_up"
			}
			if get_extra_match_info:
				display_name_mapping += {
					"school reference": "school_ref",
					"job reference": "job_ref"
				}

			# baseline opener response rate for this person
			all_opener_mean = messages_df["got_response"][(
				messages_df["is_opener"] == 1)].mean()

			# calc mean and sample size for each bucket
			means_dict = {}
			for display_name, column_name in display_name_mapping.items():
				mean_pct_diff = (messages_df["got_response"][
					(messages_df["is_opener"] == 1) &
					(messages_df[column_name] == 1)].mean() -
								all_opener_mean) / all_opener_mean
				samples = len(messages_df["got_response"]
							[(messages_df["is_opener"] == 1)
							& (messages_df[column_name] == 1)])
				means_dict.update({display_name: [mean_pct_diff, samples]})

			# TODO: this is inelegant, should be combined in previous data structure. currently putting means in a list to make iterating through them to find p_value easier
			means_list = [data[0] for name, data in means_dict.items()]
			means_std_dev = np.std(np.array(means_list))

			# calc p_values for each bucket
			# TODO: fix
			# TODO: calc for all users, then display color coded leaderboard + user lines
			for display_name, data in means_dict.items():
				mean = data[0]
				samples = data[1]
				z_score = (mean - all_opener_mean) / (means_std_dev /
													math.sqrt(samples))
				p_value = scipy.stats.norm.pdf(
					abs(z_score)
				) * 2  # two - sided test since we can't be sure which direction the mean will move
				means_dict[display_name].append(p_value)

			# opener_response_rates_df["samples"] = messages_df[messages_df["is_opener"] == 1].groupby('message').size()

			# plot opener performance
			plot_url = get_opener_plot(means_dict)

			##### wordclouds
			long_convo_cloud_url = make_cloud(messages_df["message_lower_case"][messages_df["long_convo"] == 1])
			ghosted_cloud_url = make_cloud(messages_df["message_lower_case"][(messages_df["got_response"] == 0) & (messages_df["from"] == user_id)])

		return render_template('results.html', 
			auth_color = auth_color,
			auth_status = auth_status, 
			score_1 = photo_scores[0]['score'], 
			score_2 = photo_scores[1]['score'], 
			score_3 = photo_scores[2]['score'], 
			score_4 = photo_scores[3]['score'], 
			score_5 = photo_scores[4]['score'], 
			score_6 = photo_scores[5]['score'], 
			url_1 = photo_scores[0]['url'], 
			url_2 = photo_scores[1]['url'], 
			url_3 = photo_scores[2]['url'], 
			url_4 = photo_scores[3]['url'], 
			url_5 = photo_scores[4]['url'], 
			url_6 = photo_scores[5]['url'],
			plot_url = plot_url,
			long_convo_cloud_url = long_convo_cloud_url,
			ghosted_cloud_url = ghosted_cloud_url,
	)

	except:
		extype, value, tb = sys.exc_info()
		traceback.print_exc()
		pdb.post_mortem(tb)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
