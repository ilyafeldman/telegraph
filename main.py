from Telegram.telegraph.get_data_scrape import first_run
from get_data_scrape import loop , first_run
from give_graph_pyvis import create_graph

channel_name = input("Enter the channel name: ")
iterations_number = int(input("Enter the number of iterations: "))

create_graph(loop(first_run(channel_name) , 0 , channel_name, iterations_number) , iterations_number , channel_name)