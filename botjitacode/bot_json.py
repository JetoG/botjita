import json
import discord
import asyncio
from discord.ext import commands

channel_member_file = 'botjitacode/member_count_channels.json'

# Função JSON que carrega a lista de canais dos servidor que contem contagem de membros.
async def load_member_count_channels():
    global member_count_channels

    try:
        with open(channel_member_file, 'r') as file:
            data = file.read()
            if data:
                member_count_channels = json.loads(data)
            else:
                member_count_channels = {}
    except FileNotFoundError:
        member_count_channels = {}

# Função JSON que salva o canal de contagem no arquivo.
async def save_member_count_channels():
    global member_count_channels

    with open(channel_member_file, 'w') as file:
        json.dump(member_count_channels, file)

# Função JSON que pega o canal de contagem.
async def get_member_count_channel(guild):
    global member_count_channels

    return member_count_channels.get(str(guild.id))

# Função que cria o canal de contagem de membros.
async def create_member_count_channel(guild):
    global member_count_channels

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, read_message_history=True, add_reactions=True, send_messages=False, manage_messages=False, manage_channels=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, read_message_history=True, add_reactions=True),
        guild.owner: discord.PermissionOverwrite(
            read_messages=True, read_message_history=True, add_reactions=True, send_messages=True, manage_messages=True)
    }

    channel = await guild.create_text_channel(name='member-count', overwrites=overwrites, position=0)
    
    member_count_channels[str(guild.id)] = str(channel.id)
    await save_member_count_channels()

    # Carregar as novas configurações do arquivo JSON
    await load_member_count_channels()
    await update_member_count(channel)

    return channel

# Função que atualiza a contagem de membros.
async def update_member_count(channel):
    member_count = channel.guild.member_count
    try:
        await channel.edit(name=f'🧮┃membros: [{member_count}]')
    except discord.HTTPException as e:
        if e.status == 429:  # Limite de Tentativas Excedido
            retry_after = e.retry_after
            print(
                f"Estamos com o Limite de Tentativas. Tentando novamente em {retry_after} segundos.")
            await asyncio.sleep(retry_after)
            await update_member_count(channel)
        else:
            raise e
        
async def update_json_member_channel(guild):
    # Carregar as configurações do arquivo JSON
    await load_member_count_channels()
    
    # Verifique se o canal excluído é o canal de membros
    guild_id = str(guild.id)
    channel_id = member_count_channels.get(guild_id)
    channel = guild.get_channel(int(channel_id)) if channel_id else None

    if not channel:
        # Canal não existe mais, remova a entrada correspondente do arquivo JSON
        member_count_channels.pop(guild_id, None)   
    
    # Salvar as configurações no arquivo JSON
    await save_member_count_channels()
    # Carregar as novas configurações do arquivo JSON
    await load_member_count_channels()


channel_trade_file = 'botjitacode/trade_notification_channels.json'


# Função para carregar as configurações do arquivo JSON
async def load_trade_notification_channels():
    global trade_notification_channels

    try:
        with open(channel_trade_file, 'r') as file:
            data = file.read()
            if data:
                trade_notification_channels = json.loads(data)
            else:
                trade_notification_channels = {}
    except FileNotFoundError:
        trade_notification_channels = {}

    return trade_notification_channels


# Função JSON que salva o canal de troca no arquivo.
async def save_trade_notification_channels():
    global trade_notification_channels

    with open(channel_trade_file, 'w') as file:
        json.dump(trade_notification_channels, file)


# Função JSON que pega o canal de trade.
async def get_trade_notifications_channel(guild):
    trade_notification_channels = await load_trade_notification_channels()
    return trade_notification_channels.get(str(guild.id))

# Função para criar o canal de notificações de trocas
async def create_trade_notifications_channel(guild, bot):
    global trade_notification_channels

    channel = await guild.create_text_channel('🏦┃trocas-do-server', position=0)
    trade_notification_channels[str(guild.id)] = str(channel.id)
    await save_trade_notification_channels()
    await load_trade_notification_channels()
    await send_trade_embed(channel, bot)

    return channel

async def send_trade_embed(channel, bot):
    embed = discord.Embed(
        title="Trocas",
        description="Digite **_!!troca_** para iniciar uma troca",
        color=discord.Color.dark_green()
    )

    await channel.send(embed=embed)


async def update_json_trade_channel(guild):
    # Carregar as configurações do arquivo JSON
    await load_trade_notification_channels()
    
    # Verifique se o canal excluído ainda existe no servidor
    canal_deletado = str(guild.id) #Pega o ID do canal excluido!
    
    #Tenta pegar o canal do ID de trade, com base no deletado
    channel_id = trade_notification_channels.get(canal_deletado) 
        
    channel = guild.get_channel(int(channel_id)) if channel_id else None
    
    if not channel:
        # Canal não existe mais, remova a entrada correspondente do arquivo JSON
        trade_notification_channels.pop(canal_deletado, None)
    
    # Salvar as configurações no arquivo JSON
    await save_trade_notification_channels()
    # Carregar as novas configurações do arquivo JSON
    await load_trade_notification_channels()


