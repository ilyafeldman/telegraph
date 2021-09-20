from scrape import loop , first_run
from my_pyvis import create_graph


channel_name = input('Enter the channel name: ')
iterations_number = int(input('Enter the number of iterations: '))
scrolls = int(input('Enter number of page scrolls (more is better, but takes longer): '))

create_graph(loop(first_run(channel_name , scrolls) , 0 , channel_name, iterations_number) , iterations_number , channel_name)