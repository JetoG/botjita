import discord
import asyncio
from func_utils import get_member_count_channel, create_member_count_channel, get_trade_notifications_channel, create_trade_notifications_channel

# ENVIAR NOTIFICAÇÕES
async def enviar_notificacoes(recipients, title, description):
    embed = discord.Embed(title=title, description=description)
    for recipient in recipients:
        await recipient.send(embed=embed)

# CANAL MEMBROS
# Função para verificar o canal de membros no evento on_ready
async def verifica_canal_membros_on_ready(guild):
    channel_id = await get_member_count_channel(guild)
    if not channel_id:
        print(f"AVISO: O canal de membros não existe no servidor {guild.name}.")
        return None
     
    channel = guild.get_channel(int(channel_id))
    return channel


# Função de Verificação e de Criar o canal ao entrar no Servidor
async def verifica_canal_membros(guild):
    channel_id = await get_member_count_channel(guild)
    if not channel_id:
        channel = await create_member_count_channel(guild)
    else:
        channel = guild.get_channel(int(channel_id))


# CANAL TROCAS
# Função para verificar o canal de trocas no evento on_ready
async def verifica_canal_trade_on_ready(guild):
    channel_id = await get_trade_notifications_channel(guild)
    if not channel_id:
        print(f"AVISO: O canal de trocas não existe no servidor {guild.name}.")
        return None

    channel = guild.get_channel(int(channel_id))
    return channel
    

# Função de Verificação e de Criar o canal ao entrar no Servidor
async def verifica_canal_trade(guild):
    channel_id = await get_trade_notifications_channel(guild)
    if not channel_id:
        channel = await create_trade_notifications_channel(guild)
    else:
        channel = guild.get_channel(int(channel_id))