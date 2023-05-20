import json
import discord
import asyncio

channel_file = 'botjitacode/member_count_channels.json'

# Função JSON que carrega a lista de canais dos servidor que contem contagem de membros.
async def load_member_count_channels():
    global member_count_channels

    try:
        with open(channel_file, 'r') as file:
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

    with open(channel_file, 'w') as file:
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
    await update_member_count(channel)

    member_count_channels[str(guild.id)] = str(channel.id)
    await save_member_count_channels()

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
