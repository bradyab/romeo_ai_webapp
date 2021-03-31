from datetime import datetime
import requests
import os
import glob
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
import paralleldots


def reformat_timestamp(timestamp, format_contains_T, format_contains_Z=True):
    t = "T" if format_contains_T else " "
    # was getting error
    #	 File "main.py", line 63, in submit
    #		 if not user_data[user_id][name] or (user_data[user_id][name] and now - reformat_timestamp(user_data[user_id][name][-1]["romeo_ai_saved_at"].split("+")[0], False) > timedelta(days=1)):
    # TypeError: can't subtract offset-naive and offset-aware datetimes
    z = "%z" if format_contains_Z else ""
    return datetime.strptime(timestamp, '%Y-%m-%d' + t + '%H:%M:%S.%f')


def get_responses():
    # from transformers import AutoModelForCausalLM, AutoTokenizer
    # import torch

    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")
    model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")

    # Let's chat for 5 lines
    for step in range(5):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = tokenizer.encode(input(">> User:") +
                                              tokenizer.eos_token,
                                              return_tensors='pt')

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat(["what's up", new_user_input_ids],
                                  dim=-1) if step > 0 else new_user_input_ids

        # generated a response while limiting the total chat history to 1000 tokens,
        chat_history_ids = model.generate(bot_input_ids,
                                          max_length=1000,
                                          pad_token_id=tokenizer.eos_token_id)

        # pretty print last ouput tokens from bot
        print("DialoGPT: {}".format(
            tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0],
                             skip_special_tokens=True)))


def analyze_text(df):  #url, path):
    api_key = "ugNAuLVAjWwYQDryjgiphySToJI47LozLJOvSZ62syQ"
    paralleldots.set_api_key(api_key)
    print("API Key: {}".format(paralleldots.get_api_key()))

    text = df["message_lower_case"].head(20).tolist()
    response = paralleldots.batch_emotion(text)

    # Mapping the dictionary keys to the data frame.
    mapped_emotions = {}
    for emotion in response["emotion"][0].keys():
        for i in range(len(response["emotion"])):
            string = text[i]
            mapped_emotions.update(
                {string: response["emotion"][i].get(emotion)})

        df[emotion] = df["message_lower_case"].map(mapped_emotions)

    import pdb

    top_texts = {}
    for emotion in response["emotion"][0].keys():
        # pdb.set_trace()
        idxmax = df[emotion].idxmax()
        top_texts.update({
            emotion:
            df[["match_name", "message", emotion]][df.index == idxmax]
        })

    return top_texts

# text			= "Chipotle in the north of Chicago is a nice outlet. I went to this place for their famous burritos but fell in love with their healthy avocado salads. Our server Jessica was very helpful. Will pop in again soon!"


# >>> path			= "/path/to/image.jpg"
# >>> lang_code = "fr"
# >>> aspect		= "food"
# >>> lang_text = "C'est un environnement très hostile, si vous choisissez de débattre ici, vous serez vicieusement attaqué par l'opposition."
# >>> category	= [ "travel","food","shopping", "market" ]
# >>> url			 = "http://i.imgur.com/klb812s.jpg"
# >>> data			=	[ "I like walking in the park", "Don't repeat the same thing over and over!", "This new Liverpool team is not bad", "I have a throat infection" ]

# print( "\nAbuse" )
# print(paralleldots.abuse( text ))

# >>> print( "\nBatch Abuse" )
# >>> paralleldots.batch_abuse( data )

# >>> print( "\nCustom Classifier" )
# >>> paralleldots.custom_classifier( text, category )

# >>> print( "\nEmotion" )
# >>> paralleldots.emotion( text )

# >>> print( "\nBatch Emotion" )
# >>> paralleldots.batch_emotion( data )

# >>> print( "\nEmotion - Lang: Fr". )
# >>> paralleldots.emotion( lang_text, lang_code )

# >>> print( "\nSarcasm - Lang: Fr" )
# >>> paralleldots.sarcasm( lang_text,lang_code )

# >>> print( "\nSarcasm" )
# >>> paralleldots.sarcasm( text)

# >>> print( "\nBatch Sarcasm" )
# >>> paralleldots.batch_sarcasm( data )

# print( "\nFacial Emotion" )
# # import pdb
# # pdb.set_trace()
# paralleldots.facial_emotion("/home/runner/romeoai-brady/" + path)

# print( "\nFacial Emotion: URL Method" )
# import pdb
# pdb.set_trace()
# print(paralleldots.facial_emotion_url(url))

# >>> print( "\nIntent" )
# >>> paralleldots.intent( text )

# >>> print( "\nBatch Intent" )
# >>> paralleldots.batch_intent( data )

# >>> print( "\nKeywords" )
# >>> paralleldots.keywords( text )

# >>> print( "\nBatch Keywords" )
# >>> paralleldots.batch_keywords( data )

# >>> print( "\nLanguage Detection" )
# >>> paralleldots.language_detection( lang_text )

# >>> print( "\nBatch Language Detection" )
# >>> paralleldots.batch_language_detection( data )

# >>> print( "\nMultilang Keywords - Lang: fr". )
# >>> paralleldots.multilang_keywords( lang_text, lang_code )

# >>> print( "\nNER" )
# >>> paralleldots.ner( text )

# >>> print( "\nNER - Lang: es" )
# >>> paralleldots.ner( "Lionel Andrés Messi vuelve a ser el gran protagonista en las portadas de la prensa deportiva internacional al día siguiente de un partido de Champions.","es" )

# >>> print( "\nBatch NER" )
# # >>> paralleldots.batch_ner( data )
# 	print( "\nObject Recognizer" )
# 	paralleldots.object_recognizer( path )

# print( "\nObject Recognizer: URL Method" )
# print(paralleldots.object_recognizer_url( url ))

# >>> print( "\nPhrase Extractor" )
# >>> paralleldots.phrase_extractor( text )

# >>> print( "\nBatch Phrase Extractor" )
# >>> paralleldots.batch_phrase_extractor( data )

# >>> print( "\nSentiment" )
# >>> paralleldots.sentiment( text )

# >>> print( "\nTarget Sentiment" )
# >>> paralleldots.target_sentiment( text, aspect )

# >>> print( "\nBatch Sentiment" )
# >>> paralleldots.batch_sentiment( data )

# >>> print( "\nSentiment - Lang: Fr". )
# >>> paralleldots.sentiment( lang_text, lang_code )

# >>> print( "\nSimilarity" )
# >>> paralleldots.similarity( "I love fish and ice cream!", "fish and ice cream are the best!" )

# >>> print( "\nTaxonomy" )
# >>> paralleldots.taxonomy( text )

# >>> print( "\nBatch Taxonomy" )
# >>> paralleldots.batch_taxonomy( data )

# >>> paralleldots.usage()

sp = spacy.load('en_core_web_sm')
stop_words = sp.Defaults.stop_words | set(["", " "])


def get_matches_plot(matches):
    x, y, n = [], [], 1
    for match in matches:
        x.append(
            datetime.strptime(match.get("created_date"),
                              '%Y-%m-%dT%H:%M:%S.%f%z'))
        y.append(n)
        n += 1

    x.sort()
    img = BytesIO()

    _ = plt.scatter(x, y)
    _ = plt.xticks(rotation=45)
    _ = plt.xlabel('Your Matches Over Time')
    _ = plt.ylabel('Matches')
    _ = plt.savefig(img, format='png')
    _ = plt.close()

    img.seek(0)

    return base64.b64encode(img.getvalue()).decode('utf8')


# def detect_labels_uri(uri):
#		 """Detects labels in the file located in Google Cloud Storage or on the
#		 Web."""
#		 from google.cloud import vision
#		 client = vision.ImageAnnotatorClient()
#		 image = vision.Image()
#		 image.source.image_uri = uri

#		 response = client.label_detection(image=image)
#		 labels = response.label_annotations
#		 print('Labels:')

#		 for label in labels:
#				 print(label.description)

#		 labels_joined = ""
#		 labels_joined += " ".join(labels) + " "

#		 if response.error.message:
#				 raise Exception(
#						 '{}\nFor more info on error messages, check: '
#						 'https://cloud.google.com/apis/design/errors'.format(
#								 response.error.message))

#		 return labels_joined


def get_photo_scores(user_photos):
    photos_evaluated = 0
    num_non_photos = 0
    photo_scores = [
        {
            "url": None,
            "score": None,
            "filename": "",
            "labels": ""
        },
        {
            "url": None,
            "score": None,
            "filename": "",
            "labels": ""
        },
        {
            "url": None,
            "score": None,
            "filename": "",
            "labels": ""
        },
        {
            "url": None,
            "score": None,
            "filename": "",
            "labels": ""
        },
        {
            "url": None,
            "score": None,
            "filename": "",
            "labels": ""
        },
        {
            "url": None,
            "score": None,
            "filename": "",
            "labels": ""
        },
        {
            "url": None,
            "score": None,
            "filename": "",
            "labels": ""
        },
        {
            "url": None,
            "score": None,
            "filename": "",
            "labels": ""
        },
        {
            "url": None,
            "score": None,
            "filename": "",
            "labels": ""
        },
        {
            "url": None,
            "score": None,
            "filename": "",
            "labels": ""
        },
        {
            "url": None,
            "score": None,
            "filename": "",
            "labels": ""
        },
    ]

    files_deleted = False

    # is this while loop necessary?
    while photos_evaluated + num_non_photos < len(user_photos):
        for n, p in enumerate(user_photos):
            if p['type'] != 'image':
                num_non_photos += 1
                continue

            filename = "static/tmp/" + p.get('id') + ".jpg"
            # if we haven't already downloaded files, clear tmp/ and download them
            if filename not in glob.glob("static/tmp/*.jpg", recursive=True):
                # clear tmp/
                if not files_deleted:
                    files = glob.glob('static/tmp/*')
                    for f in files:
                        os.remove(f)
                    files_deleted = True

                # download photos
                response = requests.get(p["url"])
                # create /tmp folder if it doesn't exist
                if not os.path.exists('static/tmp'):
                    os.makedirs('static/tmp')
                with open(filename, "wb") as f:
                    f.write(response.content)

            # labels = detect_labels_uri(p['url'])

            score = p['score'] if "score" in p.keys() else "unknown"
            Image.open(requests.get(p['url'], stream=True).raw)
            # print(n)
            # if n == 6:
            #		 import pdb; pdb.set_trace()
            photo_scores[n]['url'] = p["url"]
            # print(p["url"])
            # print(requests.post( "https://apis.paralleldots.com/v4/facial_emotion", data={ "api_key": api_key ,"url": p["url"]}).text)
            # analyze_pic(p["url"], filename)
            photo_scores[n]['score'] = None if score == "unknown" else round(
                score * 100, 3)
            photo_scores[n]['filename'] = filename
            # photo_scores[n]['labels'] = labels
            photos_evaluated += 1

    # photo_scores_ordered = []
    # for photo in photo_scores:
    # 	if photo["url"]:
    # 		temp = photo_scores_ordered
    # 		photo_scores_ordered = [photo].append(temp)
    # import pdb;pdb.set_trace()
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
        if column_name in messages_df.columns:
            mean_pct_diff = (messages_df["got_response"][
                (messages_df["is_opener"] == 1) &
                (messages_df[column_name] == 1)].mean() -
                             all_opener_mean) / all_opener_mean
            samples = len(
                messages_df["got_response"][(messages_df["is_opener"] == 1)
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
        key + "\n Samples: " + str(round(value[1], 3))
        for key, value in means_dict.items()
    ]
    y = [value[0] for value in means_dict.values()]

    img = BytesIO()

    _ = plt.bar(x, y)
    # _ = plt.xticks(rotation=45)
    _ = plt.xlabel('Opener Category')
    _ = plt.ylabel('Response Rate vs. Your Average')
    _ = plt.savefig(img, format='png')
    _ = plt.close()

    img.seek(0)

    # add floating text annotations
    # ax = fig.add_subplot(111)
    # ax)
    # for value in means_dict.values():
    #		 ax.text(x + 3, y + .25, "P-value: " + str(value[2]), color='blue', fontweight='bold')

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

    comment_words = " :( " if comment_words == "" else comment_words
    # import pdb;pdb.set_trace()
    wordcloud = WordCloud(width=800,
                          height=800,
                          background_color='white',
                          stopwords=stopwords,
                          min_font_size=10).generate(comment_words)

    # generate the WordCloud image
    img = BytesIO()
    wordcloud.to_image().save(img, 'png')

    return base64.b64encode(img.getvalue()).decode('utf8')
