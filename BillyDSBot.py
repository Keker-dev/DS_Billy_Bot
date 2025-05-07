from config import settings
import discord, os
from pytubefix import YouTube
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=settings["prefix"], intents=intents)
pl_ffmpeg = "ffmpeg/bin/ffmpeg.exe"


def download_audio(url):
    try:
        audio = YouTube(url)
        output = audio.streams.get_audio_only().download()
        if os.path.exists("music.mp3"):
            os.remove("music.mp3")
        os.rename(output, "music.mp3")
        return audio.title
    except Exception as e:
        print(e)
        return None


@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} is ready!")


@bot.command(name='ping', help='Показывает задержку в твоём развитии.')
async def ping(ctx):
    await ctx.send(f'**Pong!** Задержка в твоём развитии: {round(bot.latency * 1000)}ms')


@bot.command(description="Придёт к тебе.")
async def join(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        return await ctx.send('Ты не в войсе!')
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)


@bot.command(name='play', help='Побрынчу')
async def play(ctx, url):
    if ctx.voice_client is None:
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            return await ctx.send('Ты не в войсе!')
        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            audio_name = download_audio(url)
            if not audio_name:
                return await ctx.send('Не нашёл твою ссылку, ♂️boy♂️.')
            voice_channel.play(discord.FFmpegPCMAudio(executable=pl_ffmpeg, source="music.mp3"), bitrate=192)
        await ctx.send(f'**Сейчас играю:** {audio_name}')
    except Exception as e:
        print(e)
        await ctx.send(f"Я не хочу.")


@bot.command(name='stop', help='Перестану петь.')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("Я и так не пел.")


@bot.command(description="Я уйду, но запомню это.")
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client is None:
        await ctx.send("Я и так отдыхал.")
    else:
        await voice_client.disconnect()


if __name__ == '__main__':
    bot.run(settings["token"])
