from scrape import loop , first_run , get_data
from my_pyvis import create_graph


channel_name = input('Enter the channel name: ')
iterations_number = int(input('Enter the number of iterations: '))
total_messages = int(input('Enter number of messages: '))

#create_graph(loop(first_run(channel_name , scrolls) , 0 , channel_name, iterations_number , scrolls) , iterations_number , channel_name)

get_data(channel_name , total_messages)