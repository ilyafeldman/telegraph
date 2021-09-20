from get_data import get_data
from get_graph import get_graph

channel_name = input('channel name: ')
total_messages = int(input('total messages: '))
iterations_number = int(input("Enter the number of iterations: "))

get_graph(get_data(channel_name , total_messages , iterations_number))