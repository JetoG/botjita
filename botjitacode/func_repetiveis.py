import discord
import asyncio
from func_utils import *

async def verifica_canal_membros(guild):
        channel_id = await get_member_count_channel(guild)
        if not channel_id:
            channel = await create_member_count_channel(guild)
        else:
            channel = guild.get_channel(int(channel_id))
