import requests as req , re , pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

exception_list = ['durov', 'username', 'telegram', 'communityrules', 'jobsbot', 'antiscam', 'tandroidapk', 'botfather', 'quizbot']

def connect(source): # returns an html page of a channel
    url = 'https://t.me/s/' + source
    request = req.get(url)
    html = request.text.lower()
    print('connect' , source)
    return html

def targets(html , source): # returns a source-target dataframe per channel
    regex = re.compile(r'href=.https://t.me/\w+')
    data = []
    for target in regex.findall(html):
        target = target.rsplit('/' , 1)[1]
        if target.lower() != source.lower():
            if target.lower() not in exception_list:
                data.append([source.lower(), target.lower()])
            else:
                print('exception')
    edge_df = pd.DataFrame(data , columns=['source', 'target'])
    print('targets' , source)
    return edge_df

def getsize(html , source): #returns a number of subscribers of a channel 
    regex = re.compile(r'class=.counter_value.>[^<]+')
    try:
        string = regex.findall(html)[0]
        number = convert_str_to_number(string.rsplit('>' , 1)[1])
        print('subs_got' , source , number)
        return number
    except:
        print('subs_skip' , source)
    return

def convert_str_to_number(x): # converts a '9.0K' type string to '9000' integer
    total_stars = 0
    num_map = {'K':1000, 'M':1000000, 'B':1000000000}
    if x.isdigit():
        total_stars = int(x)
    else:
        if len(x) > 1:
            total_stars = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_stars)

def first_run(source , scrolls): # actually runs the functions needed for first cirlce targets
    if source[-3:].lower() != 'bot':
        html = connect(source , scrolls)
        edge_df = targets(html , source)
        size = getsize(html , source)
        edge_df['source_node_size'] = size
    #edge_df['edge_size'] = edge_df.groupby(['target'])['source'].transform('count')
    #edge_df = edge_df.drop_duplicates(subset=['target'])
        print('first_run' , source)
        return edge_df
    else:
        pass

def loop(df , i , start_channel_name, iter_number , scrolls): # runs n cirles per channel
    iter = iter_number
    if i < iter:
        targets = df['target']
        for target in targets:
            if target not in df['source'].values:
                if target.lower() not in exception_list:
                    edge_df = first_run(target , scrolls)
                    df = df.append(edge_df)
                    print('length' , len(df))
                else:
                    print('exception' , target)
            else:
                print('duplicate')
        if i+1==iter:
            df = df.dropna(inplace = True)
            df = df.replace(r'^s*$', float('NaN'), regex = True)
            df.to_csv('{} iteration for {}.csv'.format(str(i+1),start_channel_name))
            return df
        i += 1
        print('iteration' , i)
        loop(df , i , start_channel_name, iter)
        return df
    else: return df

def last_message_url(html , source): # returns url info needed to iterate on messages in a channel
    url = 'href="https://t.me/' + source +'/'
    regex = re.escape(url) + r'\d+'
    last_id_link = re.findall(regex , html)[-1]
    last_id = int(last_id_link.rsplit('/' , 1)[1])
    url = url.strip('href=')
    url = url[1 : : ]
    return url , last_id

def get_message_info(url , last_id , limit): # returns message data
    limit = last_id - limit
    if limit < 1:
        limit = 1
    message_data = []
    for i in tqdm(range(last_id , limit , -1)):
        url2 = url + str(i) + '?embed=1'
        request = req.get(url2)
        html = request.text.lower()
        soup = BeautifulSoup(html, 'html.parser')
        try:
            text = get_text(soup)
        except:
            text = 'NaN'
        date = get_date(soup)
        views = get_views(soup)
        message_data.append([url2 , text , date , views])
    data_df = pd.DataFrame(message_data , columns=['link' , 'text' , 'date' , 'views'])
    data_df = data_df.drop_duplicates(subset='text')
    return data_df

def get_text(soup): #used in get_message_info
    message_text = soup.find(class_= ['tgme_widget_message_text' , 'js-message_text']).text
    message_text = str(message_text).replace('\n', ' ')
    return message_text

def get_date(soup): #used in get_message_info
    message_date = soup.find('time' , class_ = 'datetime')
    message_date = message_date['datetime']
    return message_date

def get_views(soup): #used in get_message_info
    message_views = soup.find(class_= 'tgme_widget_message_views').text
    message_views = convert_str_to_number(message_views)
    return message_views

def get_data(source , total_messages):
    html = connect(source)
    url , last_id = last_message_url(html , source)
    data_df = get_message_info(url , last_id , total_messages)
    return data_df