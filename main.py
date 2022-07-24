import botpy
from botpy.message import Message
from config import *
import random, time
import httpx
from jike_util import jike_post
from flomo import save_to_flomo
from site_parser import parse_site

class ABSClient(botpy.Client):
    async def on_at_message_create(self, message: Message):
        await message.reply(content=f'<@{message.author.id}>叫我干嘛？')
    async def on_message_create(self, message: Message):
        botpy.logger.info("receive message %s" % message.content)
        message.content = message.content
        attachments = []
        if 'attachments' in dir(message):
            attachments = ['https://' + a.url for a in message.attachments]
        if message.content.startswith("抽签 "):
            choice_list = message.content.split(' ')[1:]
            await self.api.post_message(channel_id=message.channel_id, content="<@{}> {}".format(message.author.id, random.choice(choice_list)))
        # if '#' in message.content and len(message.content) > 20 and message.author.id == owner_id:
        #     status_code = save_to_flomo(message.content)
        #     if status_code == 200:
        #         await message.reply("<@{}> {}".format(message.author.id, 'saved to flomo'), message)
        #     else:
        #         await message.reply("<@{}> {}".format(message.author.id, 'save to flomo failed'), message)
        if '.jike' in message.content and message.author.id == owner_id:
            result = jike_post(message.content.replace('.jike', ''), attachments)
            if result['success']:
                await message.reply(content=f'<@{message.author.id}>send to jike succeed')
            else:
                await message.reply(content=f'<@{message.author.id}>send to jike failed, error code: {result["error"]}')
        if 'http' in message.content:
            items = parse_site(message.content)
            for i in items:
                await self.api.post_message(channel_id=message.channel_id,
                    content=f"{i['title']}\n{i['content']}\nby {i['author']}")

intents = botpy.Intents(public_guild_messages=True, guild_messages=True) 
client = ABSClient(intents=intents)
client.run(appid=app_id, token=token)
