import shutil
import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import json
import os

BOT_PREFIX = '$'

bot = commands.Bot(command_prefix=BOT_PREFIX)


@bot.event
async def on_ready():
    print("Bot is online!!!")


# hello message
@bot.command(name='hemlo', help='This command returns a random welcome message')
async def hello(ctx):
    await ctx.send("Hemlo!! type $help to get the commands")


# connect to a voice server
@bot.command(pass_context=True, name='join', help='Joins a voice server')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("Connect to a voice channel bruh!!!")
        return

    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send(f"Joined {channel}")


# leave a voice server
@bot.command(pass_context=True, name='leave', help='Leaves a voice server')
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send(f"Left {channel}")
    else:
        await ctx.send("I am asked to leave even though i am not in any channel :(")


# pause an audio
@bot.command(pass_context=True, name='pause', help='pauses the current audio')
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.pause()
        await ctx.send("Music paused")
    else:
        await ctx.send("What should I pause bruh!!?")


# resume an audio
@bot.command(pass_context=True, name='resume', help='Resumes the audio')
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
        await ctx.send("Resumed music")
    else:
        await ctx.send("Music not paused bruh!!")


# PLAYING..

@bot.command(pass_context=True, name='play', help='To play a youtube url')
async def play(ctx, url: str):
    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                # printing number of songs in queue
                #playing next song
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 15

            else:
                queues.clear()
                return

        else:
            queues.clear()

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            #removing old song file
            queues.clear()
    except PermissionError:
        await ctx.send("ERROR: Music playing")
        return

    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            #remove queue folder
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")
    await ctx.send("Getting everything ready now")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # downloading audio
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            # renaming file
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 15

    nname = name.rsplit("-", 2)
    # playing
    await ctx.send(f"Playing: {nname[0]}")


queues = {}


@bot.command(pass_context=True, name='queue', help='To add a song to queue')
async def queue(ctx, url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # download audio
        ydl.download([url])
    await ctx.send("Adding song " + str(q_num) + " to the queue")


# next audio
@bot.command(pass_context=True, name='next', help='Plays the next audio in queue')
async def next(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("Next song ")
    else:
        await ctx.send("Nothing to stop!! ")


# hiding the token
if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": ""}
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f)

token = configData["Token"]

bot.run(token)
