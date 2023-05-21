import discord
import asyncio

from discord.ext import commands
from func_utils import load_member_count_channels, get_member_count_channel, update_member_count, create_trade_notifications_channel
from func_repetiveis import verifica_canal_membros

# Configuraçãoes e Importação JSON dos Canais.
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='%', intents=intents)
token = ''


# Dicionário para armazenar os canais de contagem (ID do servidor e ID do canal)
member_count_channels = {}
trade_notification_channels = {}

# Função de quando o bot está online e pronto para uso.


@bot.event
async def on_ready():
    await load_member_count_channels()
    for guild in bot.guilds:
        await verifica_canal_membros(guild)

    await bot.change_presence(activity=discord.Game("%help"))
    print(f"Bot {bot.user} está pronto!")


# Função de criar um canal de membros quando o BOT entrar em um servidor.
@bot.event
async def on_guild_join(guild):
    await verifica_canal_membros(guild)
    print(f'Bot {bot.user} entrou no servidor: {guild.name} (ID: {guild.id})')


# Função de avisar quando um membro entra no servidor.
@bot.event
async def on_member_join(member):
    guild = member.guild
    member_count = guild.member_count
    channel_id = await get_member_count_channel(guild)
    if channel_id:
        channel = guild.get_channel(int(channel_id))
        await update_member_count(channel)

        embed = discord.Embed(
            description=f'''
            Espero que goste do servidor! 
            Total de membros: {member_count}''', color=discord.Color.green(),
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        else:
            embed.set_thumbnail(url=member.default_avatar_url)
        embed.title = f'Bem-Vindo(a)! {member.display_name}'
        embed.set_footer(text=f'ID do usuário: {member.id}')
        await channel.send(embed=embed)

# Função de avisar quando um membro sai do servidor.


@bot.event
async def on_member_remove(member):
    guild = member.guild
    member_count = guild.member_count
    channel_id = await get_member_count_channel(guild)

    if channel_id:
        channel = guild.get_channel(int(channel_id))
        await update_member_count(channel)

        embed = discord.Embed(
            description=f'''
            É uma pena que não gostou do servidor! 
            Total de membros: {member_count}''', color=discord.Color.red(),
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        else:
            embed.set_thumbnail(url=member.default_avatar_url)
        embed.title = f'Adeus! {member.display_name}'
        embed.set_footer(text=f'ID do usuário: {member.id}')
        await channel.send(embed=embed)


# Função de Limpar o chat.
@bot.command()
@commands.has_permissions(administrator=True)
@commands.bot_has_permissions(manage_messages=True)
async def clean(ctx, limit: int = None):
    channel = ctx.channel
    await ctx.message.delete()
    if limit is None:
        embed = discord.Embed(
            description='''
            Você realmente deseja deletar **TODAS** as mensagens deste canal? 
            Essa ação é __irreversível__.''',
            color=discord.Color.from_rgb(128, 128, 128)
        )
        embed.title = ':wastebasket: __**%CLEAN - Apagador de Mensagens!**__'
        embed.set_footer(text=f"{ctx.author.name}")
    else:
        embed = discord.Embed(
            description=f'''
            Você realmente deseja deletar as últimas **{limit}** mensagens deste canal? 
            Essa ação é __irreversível__.''',
            color=discord.Color.from_rgb(128, 128, 128)
        )
        embed.title = ':wastebasket: __**%CLEAN - Apagador de Mensagens!**__'
        embed.set_footer(text=f"{ctx.author.name}")

    confirmation_message = await ctx.send(embed=embed)
    await confirmation_message.add_reaction('✅')  # Reação para confirmar
    await confirmation_message.add_reaction('❌')  # Reação para cancelar

    def check(reaction, user):
        return user == ctx.author and reaction.message.id == confirmation_message.id

    try:
        reaction, _ = await bot.wait_for("reaction_add", check=check, timeout=30)
        if str(reaction.emoji) == '✅':
            await confirmation_message.delete()
            embed = discord.Embed(
                description='Mandando Mensagens para o Além... :milky_way:',
                color=discord.Color.purple()
            )
            await ctx.send(embed=embed)
            await asyncio.sleep(1.5)

            if limit is None:
                messages = await channel.purge(limit=None)
            else:
                messages = await channel.purge(limit=limit + 1)

            embed = discord.Embed(
                description=f"**{len(messages) - 1}** Mensagens viraram **POEIRA CÓSMICA**! :comet:",
                color=discord.Color.from_rgb(93, 173, 236)
            )
            embed.set_footer(text='Bom Trabalho!')
            success_message = await ctx.send(embed=embed)

            await asyncio.sleep(3)
            await success_message.delete()
        elif str(reaction.emoji) == '❌':
            await confirmation_message.delete()

            embed = discord.Embed(
                description=f"O Comando foi Cancelado.",
                color=discord.Color.red()
            )
            cancel_message = await ctx.send(embed=embed)
            await asyncio.sleep(2)
            await cancel_message.delete()
    except asyncio.TimeoutError:
        await confirmation_message.delete()

        embed = discord.Embed(
            description=f"Tempo de resposta expirado. Comando Cancelado. :alarm_clock:",
            color=discord.Color.yellow()
        )
        timeout_message = await ctx.send(embed=embed)
        await asyncio.sleep(2)
        await timeout_message.delete()


@clean.error
async def clean_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.message.delete()
        embed = discord.Embed(
            description=f"Desculpa, você não tem permissão para usar este comando.",
            color=discord.Color.red()
        )
        error_message = await ctx.send(embed=embed)
        await asyncio.sleep(2)
        await error_message.delete()
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.message.delete()
        embed = discord.Embed(
            description=f"Desculpa, o bot não tem permissão para apagar mensagens.",
            color=discord.Color.red()
        )
        error_message = await ctx.send(embed=embed)
        await asyncio.sleep(2)
        await error_message.delete()


# Função de help, para informar os comandos do BOT.
@bot.remove_command('help')
@bot.command()
async def help(ctx):
    try:
        await ctx.message.delete()
    except discord.errors.NotFound:
        pass

    embed = discord.Embed(
        description='''
            :one: - Comandos

            :two: - Quem é Jeto?

            :three: - Quem é Luxxas?

            ''',
        color=discord.Color.dark_blue()
    )
    embed.title = ':question: __**%HELP - Em que posso Ajudá-lo?!**__'
    embed.set_footer(text=f"Comando executado por {ctx.author.name}")
    mc = await ctx.channel.send(embed=embed)
    await mc.add_reaction('1️⃣')  # Reação para Comandos
    await mc.add_reaction('2️⃣')  # Reação para Quem é Jeto?
    await mc.add_reaction('3️⃣')  # Reação para Quem é Luxxas?
    await mc.add_reaction('❌')  # Reação para cancelar

    def check(reaction, user):
        return user == ctx.author and reaction.message.id == mc.id

    try:
        reaction, _ = await bot.wait_for("reaction_add", check=check, timeout=30)
        if str(reaction.emoji) == '1️⃣':
            await mc.delete()
            embed = discord.Embed(
                description='''
                **%help** - __Comando de Ajuda__.
                -- Você esta utilizando ele agora :laughing::satisfied:
                
                **%clean** - __Comando para limpar o chat__.
                -- Se digitiar um número ele apagará a quantidade de mensagens especificadas.
                *Este comando só pode ser utilizado por cargos que tem Administração e o Dono.*

                **%troca** - __Comando de Troca__.
                -- Este comando inicia uma troca com a pessoa que você mencionar, cuidado a troca tem tempo limite!
                ''',
            )
            embed.title = ':two: __**%HELP - Comandos!**__'
            mc = await ctx.channel.send(embed=embed)
            await mc.add_reaction('✅')  # Reação para fechar o comando
            await mc.add_reaction('⬅️')  # Reação para voltar

            def checar_confirmação(reaction, user):
                return user == ctx.author and reaction.message.id == mc.id

            try:
                reaction, _ = await bot.wait_for("reaction_add", check=checar_confirmação, timeout=30)
                if str(reaction.emoji) == '✅':
                    await mc.delete()
                elif str(reaction.emoji) == '⬅️':
                    await mc.delete()
                    await bot.process_commands(ctx.message)
            except asyncio.TimeoutError:
                await mc.delete()
                embed = discord.Embed(
                    description=f"Tempo de resposta expirado. Comando Cancelado. :alarm_clock:",
                    color=discord.Color.yellow()
                )
                timeout_message = await ctx.send(embed=embed)
                await asyncio.sleep(2)
                await timeout_message.delete()
        elif str(reaction.emoji) == '2️⃣':
            await mc.delete()
            embed = discord.Embed(
                description='''
                Jeto é a pessoa que me criou e que teve a ideia de iniciar o Servidor de Minecraft.
                Junto do Luxxas eles criaram esse servidor do Discord.
                ''',
                color=0x0000FF
            )
            embed.title = ':two: __**%HELP - Quem é Jeto?**__'
            mc = await ctx.channel.send(embed=embed)
            await mc.add_reaction('✅')  # Reação para fechar o comando
            await mc.add_reaction('⬅️')  # Reação para voltar

            def checar_confirmação(reaction, user):
                return user == ctx.author and reaction.message.id == mc.id

            try:
                reaction, _ = await bot.wait_for("reaction_add", check=checar_confirmação, timeout=30)
                if str(reaction.emoji) == '✅':
                    await mc.delete()
                elif str(reaction.emoji) == '⬅️':
                    await mc.delete()
                    await bot.process_commands(ctx.message)
            except asyncio.TimeoutError:
                await mc.delete()
                embed = discord.Embed(
                    description=f"Tempo de resposta expirado. Comando Cancelado. :alarm_clock:",
                    color=discord.Color.yellow()
                )
                timeout_message = await ctx.send(embed=embed)
                await asyncio.sleep(2)
                await timeout_message.delete()
        elif str(reaction.emoji) == '3️⃣':
            await mc.delete()
            embed = discord.Embed(
                description='''
                Luxxas é o Master Gado?
                Sim! Claro!
                Não tenha Dúvidas.
                Precisa de Provas?
                Aqui está:
                ''',
                color=0xFF0000
            )
            embed.title = ':three: __**%HELP - Quem é Luxxas?**__'
            mc = await ctx.channel.send(embed=embed)
            img = await ctx.send('https://prnt.sc/3TXFLmqmLpi6')
            await mc.add_reaction('✅')  # Reação para fechar o comando
            await mc.add_reaction('⬅️')  # Reação para voltar

            def checar_confirmação(reaction, user):
                return user == ctx.author and reaction.message.id == mc.id

            try:
                reaction, _ = await bot.wait_for("reaction_add", check=checar_confirmação, timeout=30)
                if str(reaction.emoji) == '✅':
                    await mc.delete()
                    await img.delete()
                elif str(reaction.emoji) == '⬅️':
                    await mc.delete()
                    await img.delete()
                    await bot.process_commands(ctx.message)
            except asyncio.TimeoutError:
                await mc.delete()
                await img.delete()
                embed = discord.Embed(
                    description=f"Tempo de resposta expirado. Comando Cancelado. :alarm_clock:",
                    color=discord.Color.yellow()
                )
                timeout_message = await ctx.send(embed=embed)
                await asyncio.sleep(2)
                await timeout_message.delete()
        elif str(reaction.emoji) == '❌':
            await mc.delete()
            embed = discord.Embed(
                description=f"O Comando foi Cancelado.",
                color=discord.Color.red()
            )
            cancel_message = await ctx.send(embed=embed)
            await asyncio.sleep(2)
            await cancel_message.delete()
    except asyncio.TimeoutError:
        await mc.delete()
        embed = discord.Embed(
            description=f"Tempo de resposta expirado. Comando Cancelado. :alarm_clock:",
            color=discord.Color.yellow()
        )
        timeout_message = await ctx.send(embed=embed)
        await asyncio.sleep(2)
        await timeout_message.delete()


# Comando para criar o canal de notificações de trocas
@bot.command()
@commands.has_permissions(administrator=True)
async def criarcanal(ctx):
    guild = ctx.guild
    channel = await create_trade_notifications_channel(guild, bot)

    if channel:
        await ctx.send(f"O canal de notificações de trocas foi criado com sucesso: {channel.mention}")
    else:
        await ctx.send("Não foi possível criar o canal de notificações de trocas.")


# Função de Troca do Servidor
@bot.command()
async def troca(ctx):
    # Verificar se o canal de notificações de trocas existe e criar se necessário
    trade_channel = await create_trade_notifications_channel(ctx.guild, bot)
    if not trade_channel:
        await ctx.send("O canal de notificações de trocas não está disponível.")
        return

    # Perguntar com quem a pessoa deseja trocar
    await ctx.send("Com quem você deseja trocar? Mencione a pessoa ou digite o nome.")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        user2_message = await bot.wait_for('message', check=check, timeout=60.0)
        user2 = None
        if user2_message.mentions:
            user2 = user2_message.mentions[0]
        else:
            user2 = discord.utils.get(
                ctx.guild.members, name=user2_message.content)
        if not user2:
            await ctx.send("Não foi possível encontrar a pessoa mencionada. Por favor, tente novamente.")
            return
    except asyncio.TimeoutError:
        await ctx.send("Tempo limite excedido. Por favor, tente novamente.")
        return

    # Perguntar sobre o item oferecido e a quantidade
    await ctx.send("Qual item você está oferecendo?")

    try:
        user1_item_message = await bot.wait_for('message', check=check, timeout=60.0)
        user1_item = user1_item_message.content
    except asyncio.TimeoutError:
        await ctx.send("Tempo limite excedido. Por favor, tente novamente.")
        return

    await ctx.send("Qual é a quantidade desse item?")

    try:
        user1_quantity_message = await bot.wait_for('message', check=check, timeout=60.0)
        user1_quantity = int(user1_quantity_message.content)
    except asyncio.TimeoutError:
        await ctx.send("Tempo limite excedido. Por favor, tente novamente.")
        return
    except ValueError:
        await ctx.send("A quantidade deve ser um número inteiro. Por favor, tente novamente.")
        return

    # Perguntar sobre o item desejado e a quantidade
    await ctx.send(f"Qual item você deseja de {user2.mention}?")

    try:
        user2_item_message = await bot.wait_for('message', check=check, timeout=60.0)
        user2_item = user2_item_message.content
    except asyncio.TimeoutError:
        await ctx.send("Tempo limite excedido. Por favor, tente novamente.")
        return

    await ctx.send(f"Qual é a quantidade desse item que você deseja de {user2.mention}?")

    try:
        user2_quantity_message = await bot.wait_for('message', check=check, timeout=60.0)
        user2_quantity = int(user2_quantity_message.content)
    except asyncio.TimeoutError:
        await ctx.send("Tempo limite excedido. Por favor, tente novamente.")
        return
    except ValueError:
        await ctx.send("A quantidade deve ser um número inteiro. Por favor, tente novamente.")
        return

    # Armazenar as informações da troca
    trade_data = {
        'user1': ctx.author,
        'user1_item': user1_item,
        'user1_quantity': user1_quantity,
        'user2': user2,
        'user2_item': user2_item,
        'user2_quantity': user2_quantity
    }

    # Enviar notificação para o canal de trocas
    trade_channel_embed = discord.Embed(
        title="Nova Troca",
        description="Uma nova troca foi iniciada:",
        color=discord.Color.blue()
    )
    trade_channel_embed.add_field(
        name="Usuário 1", value=ctx.author.mention, inline=False)
    trade_channel_embed.add_field(
        name="Item oferecido", value=user1_item, inline=False)
    trade_channel_embed.add_field(
        name="Quantidade", value=user1_quantity, inline=False)
    trade_channel_embed.add_field(
        name="Usuário 2", value=user2.mention, inline=False)
    trade_channel_embed.add_field(
        name="Item desejado", value=user2_item, inline=False)
    trade_channel_embed.add_field(
        name="Quantidade", value=user2_quantity, inline=False)

    trade_notification_message = await trade_channel.send(embed=trade_channel_embed)

    # Enviar notificação para os usuários envolvidos
    user1_embed = discord.Embed(
        title="Nova Troca",
        description="Você iniciou uma nova troca:",
        color=discord.Color.blue()
    )
    user1_embed.add_field(name="Item oferecido",
                          value=user1_item, inline=False)
    user1_embed.add_field(
        name="Quantidade", value=user1_quantity, inline=False)
    user1_embed.add_field(name="Usuário 2", value=user2.mention, inline=False)
    user1_embed.add_field(name="Item desejado", value=user2_item, inline=False)
    user1_embed.add_field(
        name="Quantidade", value=user2_quantity, inline=False)

    await ctx.author.send(embed=user1_embed)

    user2_embed = discord.Embed(
        title="Nova Troca",
        description=f"Você foi mencionado em uma nova troca por {ctx.author.mention}:",
        color=discord.Color.blue()
    )
    user2_embed.add_field(
        name="Usuário 1", value=ctx.author.mention, inline=False)
    user2_embed.add_field(name="Item oferecido",
                          value=user1_item, inline=False)
    user2_embed.add_field(
        name="Quantidade", value=user1_quantity, inline=False)
    user2_embed.add_field(name="Item desejado", value=user2_item, inline=False)
    user2_embed.add_field(
        name="Quantidade", value=user2_quantity, inline=False)

    await user2.send(embed=user2_embed)

    # Adicionar reações ao embed do canal de trocas
    # Reação de V (checkmark)
    await trade_notification_message.add_reaction('✅')
    # Reação de X (crossmark)
    await trade_notification_message.add_reaction('❌')

    # Aguardar reação de aceitação ou cancelamento da troca
    def check_reaction(reaction, user):
        return user == user2 and str(reaction.emoji) in ['✅', '❌']

    try:
        reaction, _ = await bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
        if str(reaction.emoji) == '✅':
            await trade_channel.send(f"{user2.mention} aceitou a troca! A troca foi concluída.")
        else:
            await trade_channel.send(f"{user2.mention} cancelou a troca. A troca foi cancelada.")
    except asyncio.TimeoutError:
        await trade_channel.send("Tempo limite excedido. A troca foi cancelada.")

bot.run(token)
