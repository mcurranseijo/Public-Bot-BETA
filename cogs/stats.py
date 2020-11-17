import discord
import psutil
from discord import Embed
from discord.ext import commands
from datetime import datetime


class help(commands.Cog, name='stats'):

  def __init__(self, bot):
      self.bot = bot
      self.bot.remove_command('help')

  @commands.command()
  async def getuser(self,ctx,user: discord.Member = None):
    if not user:
      user = ctx.author
    embed = Embed(title = f"Stats for {user.name}",descrtiption=f"Summoned by {ctx.author.name}",color=user.color) 
    embed.set_thumbnail(url = user.avatar_url)
    fields=[
      ('Name',user.name,True),
      ('ID',user.id,True),
      ('Created At',user.created_at.strftime("%A, %B %d %Y @ %H:%M:%S %p")
,False),
      ('Is Bot?',user.bot,True),
      ('Joined At',user.joined_at.strftime("%A, %B %d %Y @ %H:%M:%S %p"),True),
      ('Status',user.status,True)
      ]
    for name,value,inline in fields:
      embed.add_field(name=name,value=value,inline=inline)
    await ctx.send(embed=embed)


  @commands.command(name='bot',brief='returns info about the bot')
  async def getbot(self,ctx):
    embed = Embed(title='Info For Public Bot',url='https://github.com/mcurranseijo/Public-Bot-BETA',descrtiption='This bot is being ran by Keegan#6959 on a hostsapling server. If you need assistance feel free to DM me.')
    await ctx.send(f"{psutil.virtual_memory()[0]}")
    await ctx.send(f"{str(100-psutil.virtual_memory()[1]/psutil.virtual_memory()[0]*100)[0:5]}%")
    await ctx.send(f"{psutil.virtual_memory()[]}")
    await ctx.send(f"{psutil.cpu_percent()}%")
    await ctx.send(len(self.bot.guilds))
    await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(help(bot))