import json
import discord
import asyncio

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


# Função para criar o canal de notificações de trocas
async def create_trade_notifications_channel(guild, bot):
    # Verifica se o canal já existe nas configurações
    settings = await load_trade_notification_channels()
    channel_id = settings.get('trade_notifications_channel_id')

    if channel_id:
        # Verifica se o canal existe no servidor
        channel = guild.get_channel(channel_id)
        if channel:
            return channel

        # Canal não existe mais, perguntar ao usuário se deseja recriá-lo
        owner_id = settings.get('trade_notifications_channel_owner_id')
        if owner_id:
            owner = guild.get_member(owner_id)
            if owner:
                try:
                    message = await owner.send("O canal de notificações de trocas foi deletado. Deseja criar um novo canal?")
                    await message.add_reaction('✅')  # Reação de V (checkmark)
                    await message.add_reaction('❌')  # Reação de X (crossmark)

                    def check(reaction, user):
                        return user == owner and str(reaction.emoji) in ['✅', '❌']

                    reaction, _ = await bot.wait_for('reaction_add', timeout=60, check=check)
                    if str(reaction.emoji) == '✅':
                        del settings['trade_notifications_channel_id']
                        del settings['trade_notifications_channel_owner_id']
                        await save_trade_notification_channels()
                        return await create_trade_notifications_channel(guild, bot)
                    else:
                        await owner.send("Entendido. Se precisar criar o canal novamente, utilize o comando %criarcanal.")
                        return None
                except asyncio.TimeoutError:
                    await owner.send("Tempo limite excedido. Se precisar criar o canal novamente, utilize o comando %criarcanal.")
                    return None

    # Canal não está definido, perguntar ao usuário se deseja criar um novo canal
    owner = guild.owner
    if owner:
        try:
            message = await owner.send("O canal de notificações de trocas não está definido. Deseja criar um novo canal?")
            await message.add_reaction('✅')  # Reação de V (checkmark)
            await message.add_reaction('❌')  # Reação de X (crossmark)

            def check(reaction, user):
                return user == owner and str(reaction.emoji) in ['✅', '❌']

            reaction, _ = await bot.wait_for('reaction_add', timeout=60, check=check)
            if str(reaction.emoji) == '✅':
                # Defina a categoria desejada para o canal de notificações
                category = guild.categories[0]
                channel = await category.create_text_channel('trocas-notificacoes')
                settings['trade_notifications_channel_id'] = channel.id
                settings['trade_notifications_channel_owner_id'] = owner.id
                await save_trade_notification_channels()
                return channel
            else:
                await owner.send("Entendido. Caso deseje criar o canal posteriormente, utilize o comando %criarcanal.")
                return None
        except asyncio.TimeoutError:
            await owner.send("Tempo limite excedido. Caso deseje criar o canal posteriormente, utilize o comando %criarcanal.")
            return None

    return None