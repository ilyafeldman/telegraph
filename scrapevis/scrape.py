import requests as req , re , pandas as pd , time , config
from bs4 import BeautifulSoup
from selenium import webdriver

exception_list = ['durov', 'username', 'telegram', 'communityrules', 'jobsbot', 'antiscam', 'tandroidapk', 'botfather', 'quizbot']

def connect(source):
    url = 'https://t.me/s/' + source
    request = req.get(url)
    html = request.text
    print('connect' , source)
    return html

def targets(html , source):
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

def getsize(html , source):
    regex = re.compile(r'class=.counter_value.>[^<]+')
    try:
        string = regex.findall(html)[0]
        number = convert_str_to_number(string.rsplit('>' , 1)[1])
        print('subs_got' , source , number)
        return number
    except:
        print('subs_skip' , source)
    return

# Note: connect , targets and size functions can be edited per social network

def convert_str_to_number(x):
    total_stars = 0
    num_map = {'K':1000, 'M':1000000, 'B':1000000000}
    if x.isdigit():
        total_stars = int(x)
    else:
        if len(x) > 1:
            total_stars = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_stars)

def get_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    texts = soup.find_all(class_= ['tgme_widget_message_text' , 'js-message_text' , 'before_footer'])
    cleantexts = []
    for dirtytext in texts:
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', str(dirtytext))
        cleantexts.append(cleantext)
    print(len(cleantexts))

def scroller(source , scrolls):
    driver = webdriver.Chrome(config.executable_path)
    driver.get("https://t.me/s/" + source)
    time.sleep(2)
    for i in range(1,scrolls):
        driver.execute_script("window.scrollTo(50000,1)")
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        end_check = soup.find(class_= ['tgme_widget_message_text' , 'js-message_text' , 'before_footer']).text 
        if end_check == 'Channel created':
            break
    html = driver.page_source
    print(len(html))
    return html

def first_run(source , scrolls):
    html = scroller(source , scrolls)
    edge_df = targets(html , source)
    if source[-3:].lower() != 'bot':
        size = getsize(html , source)
        edge_df['source_node_size'] = size
    edge_df['edge_size'] = edge_df.groupby(['target'])['source'].transform('count')
    edge_df = edge_df.drop_duplicates(subset=['target'])
    print('first_run' , source)
    return edge_df

def loop(df , i , start_channel_name, iter_number):
    iter = iter_number
    if i < iter:
        targets = df['target']
        for target in targets:
            if target not in df['source'].values:
                if target.lower() not in exception_list:
                    edge_df = first_run(target)
                    df = df.append(edge_df)
                    print('length' , len(df))
                else:
                    print('exception' , target)
            else:
                print('duplicate')
        if i+1==iter:
            df.to_csv('{} iteration for {}.csv'.format(str(i+1),start_channel_name))
            return df
        i += 1
        print('iteration' , i)
        loop(df , i , start_channel_name, iter)
        return df
    else: return df