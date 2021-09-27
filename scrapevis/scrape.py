from asyncio.tasks import sleep
from os import wait
from numpy import source
import requests as req , re , pandas as pd , aiohttp , asyncio
from tqdm.asyncio import trange, tqdm
from tqdm import tqdm
from bs4 import BeautifulSoup
from random import randint

exception_list = ['durov', 'username', 'telegram', 'communityrules', 'jobsbot', 'antiscam', 'tandroidapk', 'botfather', 'quizbot']

def connect(source): # returns an html page of a channel
    url = 'https://t.me/s/' + source
    request = req.get(url)
    html = request.text.lower()
    print('connect' , source)
    return html

def get_targets(soup , source): # returns a source-target dataframe per channel
    html = str(soup)
    regex = re.compile(r'href=.https://t.me/\w+')
    data = []
    for target in regex.findall(html):
        target = target.rsplit('/' , 1)[1]
        if target.lower() != source.lower():
            if target.lower() not in exception_list:
                data.append([source.lower() , target.lower()])
            else:
                print('exception')
    return data

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
        edge_df = get_targets(html , source)
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
            df = df.replace(r'^s*$', float(' '), regex = True)
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

def get_text(soup): #used in get_message_info to get message's text
    try:
        message_text = soup.find(class_= ['tgme_widget_message_text' , 'js-message_text']).text
        message_text = str(message_text).replace('\n', ' ')
        return message_text
    except:
        return ''
        
def get_date(soup): #used in get_message_info to get message's publish date
    try:
        message_date = soup.find('time' , class_ = 'datetime')
        message_date = message_date['datetime']
        return message_date
    except:
        return ''

def get_views(soup): #used in get_message_info to get message's view count
    try:
        message_views = soup.find(class_= 'tgme_widget_message_views').text
        message_views = convert_str_to_number(message_views)
        return message_views
    except:
        return ''

def link_list(url , last_id , limit): #gets links to all the channel's messages
    limit = last_id - limit
    if limit < 1:
        limit = 1
    links = []
    for i in range(last_id , limit , -1):
        url2 = url + str(i) + '?embed=1'
        links.append(url2)
    return links

def lockcheck(soup): #used to check if telegram restricted access to the site
    if soup.find(class_= 'tgme_widget_message_error') != None:
        return True
    else:
        return False

async def get_message_info(url , session , flag , source):
    message_data = []
    edge_data =[]
    async with session.get(url , ssl=False) as response:
        html = await response.text()
    soup = BeautifulSoup(html, 'html.parser')
    if lockcheck(soup) == True:
        sleeptime = randint(5,25)
        await asyncio.sleep(sleeptime)
        flag.set()
    else:
        flag.set()
        text = get_text(soup)
        date = get_date(soup)
        views = get_views(soup)
        message_data = [url , text , date , views]
        edge_data = get_targets(soup , source)
    return message_data , edge_data

async def get_message_info_sem(url , session , sem , flag , source):
    async with sem:
        return await get_message_info(url , session , flag , source)

async def get_data(source , limit):
    html = connect(source)
    url , last_id = last_message_url(html , source)
    links = link_list(url , last_id , limit)
    sem = asyncio.Semaphore(3)
    flag = asyncio.Event()
    async with aiohttp.ClientSession() as session:
        tasks = []
        total_messages_data = []
        total_edge_data = []
        for link in links:
            task = asyncio.ensure_future(get_message_info_sem(link , session , sem , flag ,source))
            tasks.append(task)
        for f in tqdm(asyncio.as_completed(tasks) , total=len(tasks)):
            await flag.wait()
            message_data , edge_data = await f
            total_messages_data.append(message_data)
            total_edge_data.append(edge_data)
    data_df = pd.DataFrame(total_messages_data , columns=['link' , 'text' , 'date' , 'views'])
    total_edge_data = [val for sublist in total_edge_data for val in sublist]
    edge_df = pd.DataFrame(total_edge_data , columns=['source' , 'target'])
    nan_value = float("NaN")
    data_df.replace("", nan_value, inplace=True)
    data_df.dropna(inplace=True)
    data_df = data_df.drop_duplicates(subset='text')
    return data_df , edge_df