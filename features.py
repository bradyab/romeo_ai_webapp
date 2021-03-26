import requests
from PIL import Image

# opener plots
import matplotlib
# prevent inline printing, which crashes the repl
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# wordcloud
from wordcloud import WordCloud, STOPWORDS
import gensim
import spacy

sp = spacy.load('en_core_web_sm')
stop_words = sp.Defaults.stop_words | set(["", " "])

def get_fb_id(access_token):
    if "error" in access_token:
        return {"error": "access token could not be retrieved"}
    """Gets facebook ID from access token"""
    req = requests.get('https://graph.facebook.com/me?access_token=' +
                       access_token)
    return req.json()["id"]

		
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
			photo_scores[n]['score'] = round(score*100, 3)
			ranking += 1
	
	# photo_scores_ordered = []
	# for photo in photo_scores:
	# 	if photo["url"]:
	# 		temp = photo_scores_ordered
	# 		photo_scores_ordered = [photo].append(temp)

	return photo_scores #_ordered


def get_opener_plot(means_dict):
	x = [
		key + "\n P-value: " + str(round(value[2], 3))
		for key, value in means_dict.items()
	]
	y = [value[0] for value in means_dict.values()]

	img = BytesIO()

	_ = plt.bar(x,y)
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
