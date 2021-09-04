import requests as req , re , pandas as pd

def connect(source):
    url = 'https://t.me/s/' + source
    request = req.get(url)
    html = request.text
    print('connected to' , source)
    return html

def targets(html , source):
    regex = re.compile(r'href=.https://t.me/\w+')
    data = []
    for target in regex.findall(html):
        target = target.rsplit('/' , 1)[1]
        if target.lower() != source.lower():
            data.append([source, target])
    edge_df = pd.DataFrame(data , columns=['source', 'target'])
    print('got targets from' , source)
    return edge_df

def subs (html , source):
    regex = re.compile(r'class=.counter_value.>[^<]+')
    try:
        string = regex.findall(html)[0]
        number = convert_str_to_number(string.rsplit('>' , 1)[1])
        print('got ' , number ,  'subs from ' , source)
        return number
    except:
        print('cant get subs for' , source)
    return

# note: connect , targets and subs functions can be edited per social network

def convert_str_to_number(x):
    total_stars = 0
    num_map = {'K':1000, 'M':1000000, 'B':1000000000}
    if x.isdigit():
        total_stars = int(x)
    else:
        if len(x) > 1:
            total_stars = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_stars)

def finals(source):
    html = connect(source)
    size = subs(html , source)
    edge_df = targets(html , source)
    edge_df['source_node_size'] = size
    edge_df['edge_size'] = edge_df.groupby(['target'])['source'].transform('count')
    edge_df = edge_df.drop_duplicates(subset=['target'])
    print('passed finals for' , source)
    return edge_df

def loop(df , i , start_channel_name):
    final_df  = pd.DataFrame()
    targets = df['target']
    for target in targets:
        edge_df = finals(target)
        final_df = final_df.append(edge_df)
        print('current length = ' , len(final_df))
    final_df.to_csv(str(i) + ' iteration for ' + start_channel_name + '.csv')
    i += 1
    print('iteration' , i)
    loop(final_df , i , start_channel_name)
    return

channel_name = input()
loop(finals(channel_name) , 0 , channel_name)