import re
import pandas as pd
import spacy
from bertopic import BERTopic
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def cleaning(df):
    df.text = df.apply(lambda row: re.sub(r"http\S+", "", row.text).lower(), 1)
    df.text = df.apply(lambda row: " ".join(re.sub("[^a-zA-Z]+", " ", row.text).split()), 1)
    df.drop_duplicates(subset='text' , inplace=True)
    return df

def topics(df):
    texts = df.text.to_list()
    topic_model = BERTopic(verbose=True , nr_topics="auto")
    topics , probs = topic_model.fit_transform(texts)
    topic_descriptions = []
    for topic in topics:
        description = topic_model.get_topic(topic)
        topic_descriptions.append(description)
    df = df.assign(topic_id = topics)
    df = df.assign(topic_description = topic_descriptions)
    return df

def entities(df):
    nlp = spacy.load("en_core_web_sm")
    total1 = []
    total2 = []
    for row in df['text']:
        doc = nlp(row)
        ents_per_doc = []
        ent_w_descr_per_doc = []
        for entity in doc.ents:
            ents_per_doc.append(entity)
            ent_w_descr = entity.text + '-' + spacy.explain(entity.label_)
            ent_w_descr_per_doc.append(ent_w_descr)
        total1.append(ents_per_doc)
        total2.append(ent_w_descr_per_doc)     
    df = df.assign(entities = total1)
    df = df.assign(entities_with_description = total2)
    return df

def sentiment(df):
    analyzer = SentimentIntensityAnalyzer()
    sentims = []
    for row in df['text']:
        sentim = analyzer.polarity_scores(row)
        sentims.append(int(sentim['compound']*100))
    df = df.assign(text_sentiment = sentims)
    return df