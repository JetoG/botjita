import discord
import asyncio
import os

from discord.ext import commands
from bot_json import get_trade_notifications_channel, load_trade_notification_channels
from bot_repeatable import verifica_canal_membros, verifica_canal_trade


class InicarComandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Função de Limpar o chat.
    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clean(self, ctx, limit: int = None):
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
            reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=30)
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


    @commands.Cog.listener()
    async def clean_error(self, ctx, error):
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
    @commands.command()
    async def help(self, ctx):
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
            reaction, _ = await self.bot.wait_for("reaction_add", check=check, timeout=30)
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

                    **%criarcanaltrocas** - __Comando para criar o canal de Trocas__.
                    O Comando cria o canal de trocas para utilizar com o comando %troca.
                    Este canal é mais utilizado para servidores de Minecraft, mas, pode ser utilizado para outros propósitos.
                    *Este comando só pode ser utilizado por cargos que tem Administração e o Dono.*

                    **%criarcanalmembros** - __Comando para criar o canal de Membros__.
                    O Comando cria o canal de trocas para utilizar com o comando %troca.
                    O canal criado contabiliza a quantidade de membros do servidor.
                    *Este comando só pode ser utilizado por cargos que tem Administração e o Dono.*
                    ''',
                )
                embed.title = ':two: __**%HELP - Comandos!**__'
                mc = await ctx.channel.send(embed=embed)
                await mc.add_reaction('✅')  # Reação para fechar o comando
                await mc.add_reaction('⬅️')  # Reação para voltar

                def checar_confirmação(reaction, user):
                    return user == ctx.author and reaction.message.id == mc.id

                try:
                    reaction, _ = await self.bot.wait_for("reaction_add", check=checar_confirmação, timeout=30)
                    if str(reaction.emoji) == '✅':
                        await mc.delete()
                    elif str(reaction.emoji) == '⬅️':
                        await mc.delete()
                        await self.bot.process_commands(ctx.message)
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
                    reaction, _ = await self.bot.wait_for("reaction_add", check=checar_confirmação, timeout=30)
                    if str(reaction.emoji) == '✅':
                        await mc.delete()
                    elif str(reaction.emoji) == '⬅️':
                        await mc.delete()
                        await self.bot.process_commands(ctx.message)
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
                    reaction, _ = await self.bot.wait_for("reaction_add", check=checar_confirmação, timeout=30)
                    if str(reaction.emoji) == '✅':
                        await mc.delete()
                        await img.delete()
                    elif str(reaction.emoji) == '⬅️':
                        await mc.delete()
                        await img.delete()
                        await self.bot.process_commands(ctx.message)
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
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def criarcanaltrocas(self, ctx):
        await ctx.message.delete()
        guild = ctx.guild
        channel = await verifica_canal_trade(guild, self.bot)
        if channel:
            certo = await ctx.send(f"O canal de notificações de trocas foi criado com sucesso: {channel.mention}")
            await asyncio.sleep(3)
            await certo.delete()
        else:
            errado = await ctx.send("Não foi possível criar o canal de notificações de trocas ou o canal já existe.")
            await asyncio.sleep(3)
            await errado.delete()

    # Comando para criar o canal de notificações de trocas
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def criarcanalmembros(self, ctx):
        guild = ctx.guild
        channel = await verifica_canal_membros(guild)
        if channel:
            await ctx.send(f"O canal de Membros foi criado com sucesso: {channel.mention}")
        else:
            await ctx.send("Não foi possível criar o canal de Membros ou o canal já existe.")


    # Função de Troca do Servidor
    @commands.command()
    async def troca(self, ctx):
        await ctx.message.delete()
        # Verificar se o canal de notificações de trocas existe
        trade_channel = await get_trade_notifications_channel(ctx.guild)
        if not trade_channel:
            message = await ctx.send("O canal de notificações de trocas não está disponível ou não existe.")
            await asyncio.sleep(3)
            await message.delete()
            return

        # Criar um canal temporário exclusivo para a pessoa que iniciou a troca
        trade_temp_channel = await ctx.guild.create_text_channel('troca-temp')

        # Perguntar com quem a pessoa deseja trocar
        await trade_temp_channel.send("Com quem você deseja trocar? Mencione a pessoa ou digite o nome.")

        def check(message):
            return message.author == ctx.author and message.channel == trade_temp_channel

        try:
            user2_message = await self.bot.wait_for('message', check=check, timeout=60.0)
            user2 = None
            if user2_message.mentions:
                user2 = user2_message.mentions[0]
            else:
                user2 = discord.utils.get(
                    ctx.guild.members, name=user2_message.content)
            if not user2:
                await trade_temp_channel.send("Não foi possível encontrar a pessoa mencionada. Por favor, tente novamente.")
                return
        except asyncio.TimeoutError:
            await trade_temp_channel.send("Tempo limite excedido. Por favor, tente novamente.")
            return

        # Perguntar sobre o item oferecido e a quantidade
        await trade_temp_channel.send("Qual item você está oferecendo?")

        try:
            user1_item_message = await self.bot.wait_for('message', check=check, timeout=60.0)
            user1_item = user1_item_message.content
        except asyncio.TimeoutError:
            await trade_temp_channel.send("Tempo limite excedido. Por favor, tente novamente.")
            return

        await trade_temp_channel.send("Qual é a quantidade desse item?")

        try:
            user1_quantity_message = await self.bot.wait_for('message', check=check, timeout=60.0)
            user1_quantity = int(user1_quantity_message.content)
        except asyncio.TimeoutError:
            await trade_temp_channel.send("Tempo limite excedido. Por favor, tente novamente.")
            return
        except ValueError:
            await trade_temp_channel.send("A quantidade deve ser um número inteiro. Por favor, tente novamente.")
            return

        # Perguntar sobre o item desejado e a quantidade
        await trade_temp_channel.send(f"Qual item você deseja de {user2.mention}?")

        try:
            user2_item_message = await self.bot.wait_for('message', check=check, timeout=60.0)
            user2_item = user2_item_message.content
        except asyncio.TimeoutError:
            await trade_temp_channel.send("Tempo limite excedido. Por favor, tente novamente.")
            return

        await trade_temp_channel.send(f"Qual é a quantidade desse item que você deseja de {user2.mention}?")

        try:
            user2_quantity_message = await self.bot.wait_for('message', check=check, timeout=60.0)
            user2_quantity = int(user2_quantity_message.content)
        except asyncio.TimeoutError:
            await trade_temp_channel.send("Tempo limite excedido. Por favor, tente novamente.")
            return
        except ValueError:
            await trade_temp_channel.send("A quantidade deve ser um número inteiro. Por favor, tente novamente.")
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
        trade_channel_id = await get_trade_notifications_channel(ctx.guild)
        if not trade_channel_id:
            await trade_temp_channel.send("O canal de notificações de trocas não está disponível ou não existe.")
            return
        else:
            await trade_temp_channel.send("Canal de Trocas encontrado, Iniciando EpicTroca!")
            await trade_temp_channel.send("Este canal será apagado em 5 segundos!")
            await asyncio.sleep(5)
            await trade_temp_channel.delete()

        trade_channel = self.bot.get_channel(int(trade_channel_id))
        trade_channel_embed = discord.Embed(
            title="EpicTroca",
            description="Uma nova EpicTroca foi iniciada:",
            color=discord.Color.blue()
        )
        trade_channel_embed.add_field(
            name="Ofertante", value=ctx.author.mention, inline=False)
        trade_channel_embed.add_field(
            name="Item Oferecido", value=user1_item, inline=True)
        trade_channel_embed.add_field(
            name="Quantidade", value=user1_quantity, inline=True)
        trade_channel_embed.add_field(
            name="Solicitado", value=user2.mention, inline=False)
        trade_channel_embed.add_field(
            name="Item Desejado", value=user2_item, inline=True)
        trade_channel_embed.add_field(
            name="Quantidade", value=user2_quantity, inline=True)

        trade_notification_message = await trade_channel.send(embed=trade_channel_embed)

        # Adicionar reações ao embed do canal de trocas
        # Reação de V (checkmark)
        await trade_notification_message.add_reaction('✅')
        # Reação de X (crossmark)
        await trade_notification_message.add_reaction('❌')

        # Aguardar reação de aceitação ou cancelamento da troca
        def check_reaction(reaction, user):
            return user == user2 and str(reaction.emoji) in ['✅', '❌']

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check_reaction)
            if str(reaction.emoji) == '✅':
                await trade_notification_message.delete()
                trade_completed_embed = discord.Embed(
                    title="EpicTroca Concluida!",
                    description="Ambos usuários aceitaram a EpicTroca:",
                    color=discord.Color.green()
                )
                trade_completed_embed.add_field(
                    name="Ofertante", value=ctx.author.mention, inline=False)
                trade_completed_embed.add_field(
                    name="Item Oferecido", value=user1_item, inline=True)
                trade_completed_embed.add_field(
                    name="Quantidade", value=user1_quantity, inline=True)
                trade_completed_embed.add_field(
                    name="Solicitado", value=user2.mention, inline=False)
                trade_completed_embed.add_field(
                    name="Item Desejado", value=user2_item, inline=True)
                trade_completed_embed.add_field(
                    name="Quantidade", value=user2_quantity, inline=True)

                await trade_channel.send(embed=trade_completed_embed)
                msgc = await trade_channel.send(f'Caro {ctx.author.mention} a Troca aceita por {user2.mention}')
                await asyncio.sleep(5)
                await msgc.delete()
            else:
                await trade_notification_message.delete()
                trade_canceled_embed = discord.Embed(
                    title="EpicTroca Cancelada",
                    description=(f"Infelizmente {user2.mention} cancelou a EpicTroca:"),
                    color=discord.Color.red()
                )
                trade_canceled_embed.add_field(
                    name="Ofertante", value=ctx.author.mention, inline=False)
                trade_canceled_embed.add_field(
                    name="Item Oferecido", value=user1_item, inline=True)
                trade_canceled_embed.add_field(
                    name="Quantidade", value=user1_quantity, inline=True)
                trade_canceled_embed.add_field(
                    name="Solicitado", value=user2.mention, inline=False)
                trade_canceled_embed.add_field(
                    name="Item Desejado", value=user2_item, inline=True)
                trade_canceled_embed.add_field(
                    name="Quantidade", value=user2_quantity, inline=True)

                await trade_channel.send(embed=trade_canceled_embed)
                await trade_channel.send(f"Caro {ctx.author.mention}, infelizmente {user2.mention} cancelou a troca.")
        except asyncio.TimeoutError:
            await trade_notification_message.delete()
            msgtrade = await trade_channel.send("Tempo limite excedido. A EpicTroca foi cancelada.")
            await asyncio.sleep(3)
            await msgtrade.delete()

