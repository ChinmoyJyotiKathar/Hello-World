import nltk
from nltk.corpus import brown
import urllib.request
import json
import random

brown_train = brown.tagged_sents(categories='news')
regexp_tagger = nltk.RegexpTagger(
    [(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),
     (r'(-|:|;)$', ':'),
     (r'\'*$', 'MD'),
     (r'(The|the|A|a|An|an)$', 'AT'),
     (r'.*able$', 'JJ'),
     (r'^[A-Z].*$', 'NNP'),
     (r'.*ness$', 'NN'),
     (r'.*ly$', 'RB'),
     (r'.*s$', 'NNS'),
     (r'.*ing$', 'VBG'),
     (r'.*ed$', 'VBD'),
     (r'.*', 'NN')
])
unigram_tagger = nltk.UnigramTagger(brown_train, backoff=regexp_tagger)
bigram_tagger = nltk.BigramTagger(brown_train, backoff=unigram_tagger)
#############################################################################


# This is our semi-CFG; Extend it according to your own needs
#############################################################################
cfg = {}
cfg["NNP+NNP"] = "NNP"
cfg["NN+NN"] = "NNI"
cfg["NNI+NN"] = "NNI"
cfg["JJ+JJ"] = "JJ"
cfg["JJ+NN"] = "NNI"
#############################################################################

class NPExtractor(object):

    def __init__(self, sentence):
        self.sentence = sentence
    # Split the sentence into singlw words/tokens
    def tokenize_sentence(self, sentence):
        tokens = nltk.word_tokenize(sentence)
        return tokens
    # Normalize brown corpus' tags ("NN", "NN-PL", "NNS" > "NN")
    def normalize_tags(self, tagged):
        n_tagged = []
        for t in tagged:
            if t[1] == "NP-TL" or t[1] == "NP":
                n_tagged.append((t[0], "NNP"))
                continue
            if t[1].endswith("-TL"):
                n_tagged.append((t[0], t[1][:-3]))
                continue
            if t[1].endswith("S"):
                n_tagged.append((t[0], t[1][:-1]))
                continue
            n_tagged.append((t[0], t[1]))
        return n_tagged
    # Extract the main topics from the sentence
    def extract(self):
        tokens = self.tokenize_sentence(self.sentence)
        tags = self.normalize_tags(bigram_tagger.tag(tokens))
        merge = True
        while merge:
            merge = False
            for x in range(0, len(tags) - 1):
                t1 = tags[x]
                t2 = tags[x + 1]
                key = "%s+%s" % (t1[1], t2[1])
                value = cfg.get(key, '')
                if value:
                    merge = True
                    tags.pop(x)
                    tags.pop(x)
                    match = "%s %s" % (t1[0], t2[0])
                    pos = value
                    tags.insert(x, (match, pos))
                    break
        matches,imp,noun = [[],[],[]]
        for t in tags:
            if 'NN' in t[1]:
                imp.append(t[0])
                noun.append(t[0])
            if 'VB' in t[1]:
                imp.append(t[0])
        return noun,imp


def movie_find(name):
    ar=""
    for names in name:
        ar += names + "+"
    url='http://www.omdbapi.com/?t='+ar
    request=urllib.request.Request(url)
    response=urllib.request.urlopen(request)
    out=response.read().decode('UTF-8')
    data = json.loads(out)
    if data["Response"] == "True":
        unwanted = ["Response","Title", "Ratings"]
        print("Title: ",data["Title"])
        for x in data:
            if x not in unwanted:
                if data[x]!="N/A":
                    print(x,": ",data[x])
        if "Ratings" in data:
            print("Other Comparisons...")
            for x in data["Ratings"]:
                print("Source: ",x['Source']," - Rating:",x['Value'])
        return True
    else:
        return False


def movielist(name):
    k=0
    for i in range(len(name)):
        arr = []
        for j in range(i, len(name)):
            arr.append(name[j])
            if movie_find(arr):
                k=1
                break
    return k
def movie_find_find(name):
    ar=""
    for names in name:
        ar += names + "+"
    url='http://www.omdbapi.com/?t='+ar
    request=urllib.request.Request(url)
    response=urllib.request.urlopen(request)
    out=response.read().decode('UTF-8')
    data = json.loads(out)
    if data["Response"] == "True":
        return data['Title']
    else:
        return ""


def movielistfind(name):
    for i in range(len(name)):
        arr = []
        flag =0
        for j in range(i, len(name)):
            arr.append(name[j])
            k=movie_find_find(arr)
            if k!="":
                flag = 1
                break
        if flag == 1:
            break
    return k

def wiki(name):
    ar=""
    limit = 5
    for names in name:
        ar += names + "%20"
    url='https://en.wikipedia.org/w/api.php?action=opensearch&search='+ar+'&limit='+str(limit)+'&namespace=0&format=json'
    request=urllib.request.Request(url)
    response=urllib.request.urlopen(request)
    out=response.read().decode('UTF-8')
    data = json.loads(out)
    for i in range(0,len(data[1])):
        print("\nKnow about: "+data[1][i]+"\nLink: "+data[3][i]+"\nDescription: "+data[2][i])






GREETING_KEYWORDS = ["hello", "hi", "greetings", "sup", "what's up","hey","hii","heyy","hay"]

GREETING_RESPONSES = ["Hello !", "Hey there!", "*nods*", "Hi there!"]

def check_for_greeting(sentence):
    
    np_extractor = NPExtractor(sentence)
    noun,imp = np_extractor.extract()
    k = movielistfind(noun)
    if k != "":
        test = input("You mean the movie? "+str(k)+':')
        print()
    if "y" in test.lower():
        movielist(noun)
    else:
        wiki(noun)




def main():
    print("I am InfoBot, you can ask me about facts, data about events, ratings and Info of   movies and many more..")
    while 1:
        array=["Ask me more..", "You have a doubt?, post it here", "Fell free to ask!", "Bring me the questions"]
        
        print(random.choice(array))
        inp=input('you:').strip()
        #wiki(inp)
        #movielist(inp)
        check_for_greeting(inp)
        #np_extractor = NPExtractor(inp)
        #result,verb,noun = np_extractor.extract()



main()
