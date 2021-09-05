import requests as req , re , pandas as pd
from pyvis.network import Network

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
            data.append([source.lower(), target.lower()])
    edge_df = pd.DataFrame(data , columns=['source', 'target'])
    print('targets' , source)
    return edge_df

def subs (html , source):
    regex = re.compile(r'class=.counter_value.>[^<]+')
    try:
        string = regex.findall(html)[0]
        number = convert_str_to_number(string.rsplit('>' , 1)[1])
        print('subs_got' , source , number)
        return number
    except:
        print('subs_skip' , source)
    return

# Note: connect , targets and subs functions can be edited per social network

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
    edge_df = targets(html , source)
    if source[-3:].lower() != 'bot':
        size = subs(html , source)
        edge_df['source_node_size'] = size
    edge_df['edge_size'] = edge_df.groupby(['target'])['source'].transform('count')
    edge_df = edge_df.drop_duplicates(subset=['target'])
    print('finals' , source)
    return edge_df

def loop(df , i , start_channel_name, iter_number):
    exception_list = ['durov', 'username', 'telegram', 'communityrules', 'jobsbot', 'antiscam', 'tandroidapk', 'botfather', 'quizbot']
    iter = iter_number
    if i < iter:
        targets = df['target']
        for target in targets:
            if target not in df['source'].values:
                if target not in exception_list:
                    edge_df = finals(target)
                    df = df.append(edge_df)
                    print('length' , len(df))
                else:
                    print('exception' , target)
            else:
                print('duplicate')
        if i+1==iter:
            df.to_csv('{} iteration for {}.csv'.format(str(i+1),start_channel_name))
        i += 1
        print('iteration' , i)
        loop(df , i , start_channel_name, iter)
        return
    else: return "finished"

def create_graph(iterations_number , channel_name):
    got_net = Network(height='750px', width='100%', bgcolor='#222222', font_color='whitw')
    edge_df = pd.read_csv('{} iteration for {}.csv'.format(str(iterations_number), channel_name))
    edge_data = zip(edge_df['source'], edge_df['target'], edge_df['edge_size'] , edge_df['source_node_size'])
    for row in edge_data:
        src , trgt , w , size = [row[i] for i in (0,1,2,3)]
        source_node_link = "<a href=\'http://t.me/s/" + src + "'>" + src + "</a>"
        target_node_link = "<a href=\'http://t.me/s/" + trgt + "'>" + trgt + "</a>"
        got_net.add_node(src, src, title=source_node_link , value=size)
        if trgt[-3:].lower() == 'bot':
            got_net.add_node(trgt, trgt, title=target_node_link , value=size/10 , shape='triangle')
        else:
            got_net.add_node(trgt, trgt, title=target_node_link , value=size/10)
        got_net.add_edge(src, trgt, value=w)
    got_net.show_buttons()
    got_net.show('{} iteration for {}.html'.format(str(iterations_number),channel_name))
    return

channel_name = input("Enter the channel name: ")
iterations_number = int(input("Enter the number of iterations: "))

loop(finals(channel_name) , 0 , channel_name, iterations_number)
create_graph(iterations_number , channel_name)
