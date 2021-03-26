import requests
from PIL import Image
from nltk.util import ngrams
from collections import Counter
from itertools import chain
import matplotlib
matplotlib.use('Agg')  # prevent inline printing, which crashes the repl
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from wordcloud import WordCloud, STOPWORDS
import gensim
import spacy
import string
import numpy as np
import math
import scipy.stats

sp = spacy.load('en_core_web_sm')
stop_words = sp.Defaults.stop_words | set(["", " "])


def get_photo_scores(user_photos):
    ranking = 0
    num_non_photos = 0
    photo_scores = [
        {
            "url": None,
            "score": None
        },
        {
            "url": None,
            "score": None
        },
        {
            "url": None,
            "score": None
        },
        {
            "url": None,
            "score": None
        },
        {
            "url": None,
            "score": None
        },
        {
            "url": None,
            "score": None
        },
    ]

    while ranking < len(user_photos) - num_non_photos:
        for n, p in enumerate(user_photos):
            if p['type'] != 'image':
                num_non_photos += 1
                continue
            score = p['score'] if "score" in p.keys() else "unknown"
            Image.open(requests.get(p['url'], stream=True).raw)
            photo_scores[n]['url'] = p["url"]
            photo_scores[n]['score'] = round(score * 100, 3)
            ranking += 1

    # photo_scores_ordered = []
    # for photo in photo_scores:
    # 	if photo["url"]:
    # 		temp = photo_scores_ordered
    # 		photo_scores_ordered = [photo].append(temp)

    return photo_scores  #_ordered


def make_ngrams(text, n):
    return ngrams(
        str(text).lower().translate(str.maketrans(
            '', '', string.punctuation)).split(" "), n) if string else ""


# match substrings in messages with those in bio, job, school, etc
def fuzzy_string_match(df, row_idx, read_col_name, write_col_name, ngrams_1,
                       n):
    # get ngrams from message
    ngrams_2 = ngrams(
        df.loc[row_idx, "message_lower_case"].translate(
            str.maketrans('', '', string.punctuation)).split(" "), n)
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
                    if word not in stop_words and word.lower() in df.loc[
                            row_idx, read_col_name].lower() and word.lower(
                            ) in df.loc[row_idx, "message_lower_case"]:
                        joined += " " + word
                # to separate ngrams for debug
                if len(joined) > 1:
                    joined += ", "
        if len(joined) > 1:
            df.loc[row_idx, write_col_name] = 1
            df.loc[row_idx, write_col_name + "_str"] = joined

def get_opener_plot_data(messages_df, get_extra_match_info):
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

	return means_dict


def get_opener_plot(means_dict):
    x = [
        key + "\n P-value: " + str(round(value[2], 3))
        for key, value in means_dict.items()
    ]
    y = [value[0] for value in means_dict.values()]

    img = BytesIO()

    _ = plt.bar(x, y)
    # _ = plt.xticks(rotation=45)
    _ = plt.xlabel('Opener Category')
    _ = plt.ylabel('Response Rate: % better than your average opener')
    _ = plt.savefig(img, format='png')
    _ = plt.close()

    img.seek(0)

    # add floating text annotations
    # ax = fig.add_subplot(111)
    # ax)
    # for value in means_dict.values():
    #     ax.text(x + 3, y + .25, "P-value: " + str(value[2]), color='blue', fontweight='bold')

    return base64.b64encode(img.getvalue()).decode('utf8')


def make_cloud(df):
    # stopwords = stopwords + set()
    gs_stopwords = gensim.parsing.preprocessing.STOPWORDS
    sp_stopwords = sp.Defaults.stop_words
    comment_words = ''

    custom_words = [
        "lol", "haha", "yeah", "oh", "u", "m", "s", "t", "guess", "weird",
        "start", "wbu", "week", "girl", "fun", "friend", "lot", "ohh", "lmao",
        "ok", "went", "fact", "help", "tho", "stuff", "think", "fact", "okay",
        "idk", "hey", "yes", "mean", "sorry", "going", "hmm", "right",
        "actually", "good", "cool", "know", "people", "work", "probably",
        "https"
    ]
    sets = [gs_stopwords, sp_stopwords, STOPWORDS, custom_words]

    stopwords_list = [list(x) for x in sets]
    stopwords = []
    for lists in stopwords_list:
        stopwords += lists

    for val in df:

        # typecaste each val to string
        val = str(val)

        # split the value
        tokens = val.split()

        # Converts each token into lowercase
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()

        comment_words += " ".join(tokens) + " "

    long_wordcloud = WordCloud(width=800,
                               height=800,
                               background_color='white',
                               stopwords=stopwords,
                               min_font_size=10).generate(comment_words)

    # generate the WordCloud image
    img = BytesIO()
    long_wordcloud.to_image().save(img, 'png')

    return base64.b64encode(img.getvalue()).decode('utf8')
