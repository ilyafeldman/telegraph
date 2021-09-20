from pyvis.network import Network

def create_graph(edge_df , iterations_number , channel_name):
    got_net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
    edge_data = zip(edge_df['source'], edge_df['target'] , edge_df['source_node_size'])
    for row in edge_data:
        src , trgt , size = [row[i] for i in (0,1,2)]
        source_node_link = "<a href=\'http://t.me/s/" + src + "'>" + src + "</a>"
        target_node_link = "<a href=\'http://t.me/s/" + trgt + "'>" + trgt + "</a>"
        got_net.add_node(src, src, title=source_node_link , value=size)
        if trgt[-3:].lower() == 'bot':
            got_net.add_node(trgt, trgt, title=target_node_link , value=size/10 , shape='triangle')
        else:
            got_net.add_node(trgt, trgt, title=target_node_link , value=size/10)
        got_net.add_edge(src, trgt)
    got_net.show_buttons()
    got_net.show('{} iteration for {}.html'.format(str(iterations_number),channel_name))
    print('graph ready')
    return