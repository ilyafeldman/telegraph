import asyncio
from scrape import get_data

async def main():
    channel_name = input('Enter the channel name: ')
    total_messages = int(input('Enter number of messages: '))
    
    texts_df = await get_data(channel_name, total_messages)
    print(texts_df)

asyncio.run(main())