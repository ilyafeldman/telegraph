#from typing import final
from tqdm import tqdm
from telethon import TelegramClient , events , sync
import pandas as pd , config , re

client = TelegramClient(config.username, config.api_id , config.api_hash)
client.start()

#Getting all the data from a channel
def channel_data(channel_name , total_messages):
    if channel_name[-3:] != 'bot':
        data = []
        exceptions = [None , channel_name , 'durov', 'username', 'telegram', 'communityrules', 'jobsbot', 'antiscam', 'tandroidapk', 'botfather', 'quizbot']
        try:
            for message in tqdm(client.get_messages(channel_name, limit=total_messages) , desc=channel_name):
                txt_trgt_list = txt_trgt(message , exceptions)
                if txt_trgt_list != None:
                    for target in txt_trgt_list:
                        data.append(target)
                fwd_trgt_str = fwd_trgt(message , exceptions)
                if fwd_trgt_str != None:
                    data.append(fwd_trgt_str)
        except:
            pass
        df = pd.DataFrame({
            "source": channel_name,
            "target": data
        })
        return df

#Getting 't.me/_____' or @_____ from message text
def txt_trgt(message , exceptions):
    text = message.text
    link_regex = re.compile(r't.me/\w+')
    at_regex = re.compile(r'@[a-zA-Z0-9]+')
    msg_matches = []
    if text != None:
        
        for match in link_regex.findall(text):
            match = match.rsplit('/' , 1)[1]
            match = match.lower()
            if match not in exceptions:
                msg_matches.append(match)
        
        for match in at_regex.findall(text): 
            match = match.rsplit('@' , 1)[1]
            match = match.lower()
            if match not in exceptions:
                msg_matches.append(match)
        
        return msg_matches
        

#If the message is forwarded from another user, getting its username
def fwd_trgt(message , exceptions):
    fwd = message.fwd_from
    if fwd != None:
        try: fwd_id = fwd.from_id.channel_id
        except: fwd_id = fwd.from_id.user_id 
        try: fwd_name = client.get_entity(int(str(fwd_id)))
        except: fwd_name = client.get_entity((str(fwd_id)))
        fwd_trgt_str = (str(fwd_name.username)).lower()
        if fwd_trgt_str not in exceptions:
            return fwd_trgt_str
        else:
            return None

def loop(df , i , start_channel_name, iter_number , total_messages):
    iter = iter_number
    if i < iter:
        for target in df['target']:
            if target not in df['source'].values:
                edge_df = channel_data(target , total_messages)
                df = df.append(edge_df)
        if i+1==iter:
            df.to_csv('{} iteration for {}.csv'.format(str(i+1),start_channel_name))
            return df
        i += 1
        loop(df , i , start_channel_name, iter , total_messages)
        return df
    else: return df

def get_data(channel_name , total_messages , iterations_number):
    channel_edge_df =  channel_data(channel_name , total_messages)
    looped_edges = loop(channel_edge_df , 0 , channel_name , iterations_number , total_messages)
    print(looped_edges)
    return looped_edges


channel_name = input('channel name: ')
total_messages = int(input('total messages: '))
iterations_number = int(input("Enter the number of iterations: "))

get_data(channel_name , total_messages , iterations_number)