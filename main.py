from flask import Flask, request, render_template
import pdb, traceback, sys
from pprint import pprint
import json
import pandas as pd
import sys
from datetime import datetime, timedelta
import pytz
import time

import src.tinder_api as tinder_api
from src.features import *

from src import aws_utils

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('landing_page.html')


@app.route('/submit', methods=['POST'])
def submit():
    t0 = time.time()

    # start pdb on exception
    try:
        # authorize for normal workflow
        try:
            auth_status, auth_color = tinder_api.authorize(request.form['text'])
        # when someone submits feedback, save it and return to home page
        except:
            with open("feedback/success_feedback_form.txt", "a") as myfile:
                myfile.write(request.form['success_feedback_form'])
            return render_template('landing_page.html')

        # save user data to file to reduce frequency of API calls and store time series data where necessary
        user_profile = tinder_api.get_self()
        # TODO: verify that profile and updates is all we need to save. matches is a subset of updates i think, no need to save
        # all_matches = tinder_api.all_matches()
        user_updates = tinder_api.get_updates()
        

        # read DB
        file = open('user_data.json')
        DB_user_data = json.load(file)
        user_data = DB_user_data.copy()

        # add new user entry if they aren't in the DB
        user_id = user_profile["_id"]
        if user_id not in user_data:
            user_data[user_id] = {}

        # initialize time series lists if they don't already exist
        # my bio, photo scores, and my matches' bios change over time so we want to save time series data
        for name, DB in {"profile": user_profile, "updates": user_updates}.items():
            if name not in user_data[user_id]:
                user_data[user_id][name] = []

            # only save data if we have no data, or it's been more than a day since it was last saved
            now = datetime.now(pytz.utc)
            if not user_data[user_id][name] or (user_data[user_id][name] and now - datetime.strptime(user_data[user_id][name][-1]["romeo_ai_saved_at"],
                                    '%Y-%m-%d %H:%M:%S.%f%z') > timedelta(
                                        days=1)):
                user_data[user_id][name].append(DB)
                # temporarily cast as str bc datetime can't be encoded to json - we should have a datetime in the real database though
                user_data[user_id][name][-1]["romeo_ai_saved_at"] = str(now)
        # import pdb; pdb.set_trace()
        if user_data != DB_user_data:
            with open('user_data.json', 'w') as fp:
                json.dump(user_data, fp, default=str)

        # TODO: remove duplicate entries. convert to csv?
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
            opener_plot, ghosted_word_cloud, long_convo_word_cloud = None, None, None
        else:
            old_messages_df["romeo_ai_user_id"] = user_id

            from fuzzywuzzy import fuzz
            pd.set_option('display.max_colwidth', None)
            pd.set_option('display.max_rows', None)

            # TODO: not all matches have conversations??
            messages_df = old_messages_df
            messages_df["is_bucketed"], messages_df["is_hey"] = 0, 0
            messages_df["school_ref"], messages_df[
                "school_ref_str"], messages_df["bio_ref"], messages_df[
                    "bio_ref_str"], messages_df["job_ref"], messages_df[
                        "job_ref_str"] = "", "", "", "", "", ""

            grouped = messages_df.groupby(['romeo_ai_user_id',
                                           'match_id'])  #.apply()

            bio_ngrams_n = 2
            job_ngrams_n, school_ngrams_n = 1, 1

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
                        bio_ngrams = make_ngrams(row["match_bio"],
                                                 bio_ngrams_n)

                        if get_extra_match_info:
                            job_ngrams = make_ngrams(row["match_job"],
                                                     job_ngrams_n)
                            school_ngrams = make_ngrams(
                                row["match_school"], school_ngrams_n)

                        messages_df.loc[row_idx, "is_opener"] = 1 if user_id == row["from"] else 0

                    convo_depth += 1
                    # if row["match_bio"] and "5 kids" in row["match_bio"]:
                    # 	nn = 1
                    # 	messages_df.loc[row_idx, "is_opener"]
                    # 	print(group_idx[0] == row["from"])

                    # bucket openers
                    # TODO: this could probably be refactored as a bunch of .applys
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
                        #         fuzz.WRatio("hey " + row["match_name"], row["message"])
                        #         fuzz.WRatio(row["match_bio"], row["message"])
                        #         fuzz.ratio("hey " + row["match_name"], row["message"])
                        #         fuzz.partial_ratio("hey " + row["match_name"], row["message"])
                        # fuzz.token_set_ratio("hey " + row["match_name"], row["message"])

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
                            "long_convo"] = 1 if len(group) > 12 else 0

            # messages_df[["message", "match_bio", "bio_ref", "bio_ref_str"]][((messages_df["is_opener"] == 1))]
            means_dict = get_opener_plot_data(messages_df,
                                              get_extra_match_info)
            # opener_response_rates_df["samples"] = messages_df[messages_df["is_opener"] == 1].groupby('message').size()

            # matches over time
            matches_plot = get_matches_plot(user_updates["matches"])
            # plot opener performance
            opener_plot = get_opener_plot(means_dict)

            ##### wordclouds
            long_convo_word_cloud = make_cloud(
                messages_df["message_lower_case"][messages_df["long_convo"] ==
                                                  1]) if len(messages_df["message_lower_case"][messages_df["long_convo"] ==
                                                  1]) > 1 else None
            ghosted_word_cloud = make_cloud(messages_df["message_lower_case"][
                (messages_df["got_response"] == 0)
                & (messages_df["from"] == user_id)]) if len(messages_df["message_lower_case"][
                (messages_df["got_response"] == 0)
                & (messages_df["from"] == user_id)]) > 1 else None

        print("{} seconds wall time".format(time.time() - t0))
        # print(photo_scores[0]['filename'])
        return render_template(
            'results.html',
            auth_status=auth_status,
            auth_color=auth_color,
            score_1=photo_scores[0]['score'],
            score_2=photo_scores[1]['score'],
            score_3=photo_scores[2]['score'],
            score_4=photo_scores[3]['score'],
            score_5=photo_scores[4]['score'],
            score_6=photo_scores[5]['score'],
            score_7=photo_scores[6]['score'],
            score_8=photo_scores[7]['score'],
            score_9=photo_scores[8]['score'],
            score_10=photo_scores[9]['score'],
            url_1=photo_scores[0]['filename'],
            url_2=photo_scores[1]['filename'],
            url_3=photo_scores[2]['filename'],
            url_4=photo_scores[3]['filename'],
            url_5=photo_scores[4]['filename'],
            url_6=photo_scores[5]['filename'],
            url_7=photo_scores[6]['filename'],
            url_8=photo_scores[7]['filename'],
            url_9=photo_scores[8]['filename'],
            url_10=photo_scores[9]['filename'],
            # label_1=photo_scores[0]['label'],
            # label_2=photo_scores[1]['label'],
            # label_3=photo_scores[2]['label'],
            # label_4=photo_scores[3]['label'],
            # label_5=photo_scores[4]['label'],
            # label_6=photo_scores[5]['label'],
            matches_plot=matches_plot,
            opener_plot=opener_plot,
            long_convo_word_cloud=long_convo_word_cloud,
            ghosted_word_cloud=ghosted_word_cloud,
        )

    except:
        return render_template('error_form.html')
        # extype, value, tb = sys.exc_info()
        # traceback.print_exc()
        # pdb.post_mortem(tb)

@app.route('/error_form', methods=['POST'])
def submit_error_form():
    with open("feedback/error_form.txt", "a") as myfile:
        myfile.write(request.form['error_form'])
    return render_template('landing_page.html')

@app.route('/', methods=['POST'])
def submit_feedback():
    with open("feedback/landing_page_feedback.txt", "a") as myfile:
        myfile.write(request.form['feedback_text'])
    return render_template('landing_page.html')

@app.route('/submit', methods=['POST'])
def submit_success_feedback_form():
    pdb.set_trace()
    with open("feedback/success_feedback_form.txt", "a") as myfile:
        myfile.write(request.form['success_feedback_form'])
    return render_template('landing_page.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
