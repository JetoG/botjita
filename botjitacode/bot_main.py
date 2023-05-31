from datetime import datetime
import discord
import asyncio
import os
import dotenv
import traceback

dotenv.load_dotenv()
from discord.ext import commands
from bot_json import load_member_count_channels, get_member_count_channel, update_member_count, update_json_member_channel, update_json_trade_channel, get_trade_notifications_channel, load_trade_notification_channels
from bot_repeatable import verifica_canal_membros_on_ready, verifica_canal_membros, verifica_canal_trade_on_ready, verifica_canal_trade
from bot_commands import InicarComandos
# Configuraçãoes e Importação JSON dos Canais.
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!!', intents=intents)
token = str(os.getenv("TOKEN"))


# Dicionário para armazenar os canais de contagem (ID do servidor e ID do canal)
member_count_channels = {}
trade_notification_channels = {}


bot.remove_command("help")
# Função de quando o bot está online e pronto para uso.

@bot.event
async def on_ready():
    await bot.add_cog(InicarComandos(bot))
    await load_trade_notification_channels()
    await load_member_count_channels()
    for guild in bot.guilds:
        await verifica_canal_membros_on_ready(guild)
        await verifica_canal_trade_on_ready(guild)
        channel_id = await get_member_count_channel(guild)
        if channel_id:
            channel = guild.get_channel(int(channel_id))
            await update_member_count(channel)

        channel_id = await get_trade_notifications_channel(guild)
        if channel_id:
            channel = guild.get_channel(int(channel_id))

    await bot.change_presence(activity=discord.Game("!!help"))
    print(f"Bot {bot.user} está pronto!")
    print(discord.__version__)


# Função de criar um canal de membros quando o BOT entrar em um servidor.
@bot.event
async def on_guild_join(guild):
    await verifica_canal_membros(guild)
    await verifica_canal_trade(guild)
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
            embed.set_thumbnail(url=member.default_avatar.url)
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


@bot.event
async def on_guild_channel_delete(channel):
    await update_json_member_channel(channel)
    await update_json_trade_channel(channel)


@bot.event
async def on_error(event, *args, **kwargs):
    error_message = traceback.format_exc()
    error_embed = discord.Embed(
        title="Erro",
        description=f"Ocorreu um erro durante o processamento de um evento: {event}",
        color=discord.Color.red()
    )
    error_embed.add_field(name="Mensagem de Erro", value=error_message, inline=False)
    error_embed.set_footer(text="Data do erro: " + str(datetime.now()))
    
    channel_id = 1112454746767360080 
    channel = bot.get_channel(channel_id)
    
    if channel:
        error_msg = await channel.send(embed=error_embed)
        await error_msg.add_reaction('✅')  # Adiciona a reação de erro corrigido
        
        def check(reaction, user):
            return (
                reaction.message.id == error_msg.id
                and str(reaction.emoji) == '✅'
                and user.id == 261270488955879434  # Substitua pelo seu ID de usuário
            )
        
        try:
            reaction, _ = await bot.wait_for('reaction_add', check=check)  # Espera pela reação por tempo indeterminado
        except asyncio.TimeoutError:
            pass
        else:
            try:
                message = await channel.fetch_message(error_msg.id)
                await message.delete()  # Deleta a mensagem de erro reagida se ela ainda existir
            except discord.NotFound:
                pass  # A mensagem de erro já foi excluída por algum motivo
    else:
        print(f"Canal de log de erros não encontrado: {channel_id}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignora mensagens de comando inválido
    
    error_message = str(error)
    error_embed = discord.Embed(
        title="Erro",
        description=f"Ocorreu um erro durante o processamento do comando.",
        color=discord.Color.red()
    )
    error_embed.add_field(name="Mensagem de Erro", value=error_message, inline=False)
    error_embed.set_footer(text="Data do erro: " + str(datetime.now()))
    
    channel_id = 1112454746767360080  # ID do canal onde as mensagens de erro serão enviadas
    channel = bot.get_channel(channel_id)
    
    if channel:
        error_message = await channel.send(embed=error_embed)
        await error_message.add_reaction('✅')  # Adiciona a reação de erro corrigido
        
        def check(reaction, user):
            return (
                reaction.message.id == error_message.id
                and str(reaction.emoji) == '✅'
                and user.id == 261270488955879434  # Substitua pelo seu ID de usuário
            )
        
        try:
            reaction, _ = await bot.wait_for('reaction_add', check=check)  # Espera pela reação por tempo indeterminado
        except asyncio.TimeoutError:
            pass
        else:
            try:
                message = await channel.fetch_message(error_message.id)
                await message.delete()  # Deleta a mensagem de erro reagida se ela ainda existir
            except discord.NotFound:
                pass  # A mensagem de erro já foi excluída por algum motivo
    else:
        print(f"Canal de log de erros não encontrado: {channel_id}")

    raise error  # Re-levanta o erro para que ele seja tratado pelo tratador padrão de erros do bot



async def reconnect_bot():
    print('Bot desconectado, tentando reconectar...')
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        try:
            await bot.start(token)
            break
        except discord.ConnectionClosed:
            print('Conexão fechada.')
            attempts += 1
            print(f'Tentativa de reconexão: {attempts}/{max_attempts}')
            await asyncio.sleep(5)

    if attempts == max_attempts:
        # Código para enviar uma notificação em um canal específico
        channel_id = 1112454933644595280
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send('O bot falhou em se reconectar após várias tentativas.')
        else:
            print(f'Canal de notificação não encontrado: {channel_id}')


@bot.event
async def on_disconnect():
    user_id = 261270488955879434
    user = bot.get_user(user_id)
    
    if user:
        mention = user.mention
        channel_id = 1112454933644595280
        channel = bot.get_channel(channel_id)
        
        if channel:
            await channel.send(f'{mention} Bot desconectado, tentando reconectar.')
        else:
            print(f'Canal de notificação não encontrado: {channel_id}')

    await reconnect_bot()

bot.run(token)
