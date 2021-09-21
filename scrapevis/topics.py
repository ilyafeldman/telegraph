from bertopic import BERTopic
import re
import pandas as pd
from datetime import datetime
from scrape import get_text , scroller


texts_df = get_text(scroller('durov' , 2))

texts_df.text = texts_df.apply(lambda row: re.sub(r"http\S+", "", row.text).lower(), 1)
#texts_df.text = texts_df.apply(lambda row: " ".join(filter(lambda x:x[0]!="@", row.text.split())), 1)
texts_df.text = texts_df.apply(lambda row: " ".join(re.sub("[^a-zA-Z]+", " ", row.text).split()), 1)
timestamps = texts_df.date.to_list()
texts = texts_df.text.to_list()

print(texts)