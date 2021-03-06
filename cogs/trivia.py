"""Commands for the trivia module"""
import discord
from discord.ext import commands
import json
import urllib.request
import random
import asyncio
import aiohttp


class TriviaCog(commands.Cog, name='trivia'):
    """
    Commands for the Trivia Querstions
    """

    def __init__(self, bot):
        self.bot = bot
        self.TOKEN_ID = ""

    @commands.command(
        name="trivia",
        brief="gets a random trivia question",
    )
    @commands.bot_has_permissions(manage_messages=True)
    async def trivia(self, ctx):
        quiz_var = random.randrange(9, 32)

        data = [6]
        data = await self.url_request(quiz_var)
        embed = discord.Embed(title="TRIVIA", )

        embed.add_field(name="Category:", value=data[0], inline=True)
        embed.add_field(name="Difficulty", value=data[1], inline=True)
        embed.add_field(name="Question", value=data[2], inline=False)
        embed.add_field(name="1: " + data[3], value="______", inline=False)
        embed.add_field(name="2: " + data[4], value="______ ", inline=False)
        embed.add_field(name="3: " + data[5], value="______ ", inline=False)
        embed.add_field(name="4: " + data[6], value="______ ", inline=False)
        embed.set_footer(text="Choose your answers, you have 15 seconds")
        message = await ctx.send(embed=embed)
        await message.add_reaction("1️⃣")
        await message.add_reaction("2️⃣")
        await message.add_reaction("3️⃣")
        await message.add_reaction("4️⃣")
        await asyncio.sleep(15)
        message = await self.bot.get_channel(ctx.channel.id).fetch_message(
            message.id)

        if data[7] == 1:
            entrants = [
                u for u in await message.reactions[0].users().flatten()
                if not u.bot
            ]
        elif data[7] == 2:
            entrants = [
                u for u in await message.reactions[1].users().flatten()
                if not u.bot
            ]
        elif data[7] == 3:
            entrants = [
                u for u in await message.reactions[2].users().flatten()
                if not u.bot
            ]
        elif data[7] == 4:
            entrants = [
                u for u in await message.reactions[3].users().flatten()
                if not u.bot
            ]

        if len(entrants) > 0:
            names = ""
            for f in entrants:
                names = names + (f"{f.name}, ")
                with open('scores.txt','r+') as json_file:
                  data = json.load(json_file)
                if not data[f.id]:
                  data[id] = 10
                else:
                    data[id]+=10

                with open('scores.txt', 'w') as outfile:
                  json.dump(data, outfile)
            body = "Use !score to check your score and !trivia stats to check the leaderboard!"
            message = await ctx.send(
                embed=discord.Embed(
                    title=f"Congrats {names} got it right",
                    description=body
                ))
        else:
            body = f"The correct answer was {data[7]}, react with ✅ to play again"
            message = await ctx.send(
                embed=discord.Embed(
                    title="No one got the right answer",
                    description=body,
                ))
        await message.add_reaction("✅")

        def check(reaction, user):
            return reaction.message.channel == ctx.channel and not user.bot and reaction.message == message

        try:
            reaction, user = await self.bot.wait_for(
                'reaction_add', timeout=15, check=check)
            if reaction.emoji:
                await self.trivia(ctx)
        except asyncio.TimeoutError:
            await ctx.send(
                embed=discord.Embed(title="No one wanted to play again", ))

    @commands.command(
        name="score",
        brief="returns your score",
    )
    async def score(self, ctx):
        """Command to get users score"""
        with open('scores.txt','r+') as json_file:
          data = json.load(json_file)
        print(data)
        score = data[str(ctx.author.id)]
        if not score:
            score = 0
        embed = discord.Embed(
            title=f"Your Score, {ctx.author.name}",
            description=f"{score} points",
        )
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(
        name="leaderboard",
        brief="returns bot trivia leaderboard",
    )
    async def leaderboard(self, ctx):
        
        with open('scores.txt','r+') as json_file:
          data = json.load(json_file)

        leaders = ""

        for count, info in enumerate(data[:10], 1):
            print(info[0])
            name = self.bot.get_user(int(info[0])).name
            leaders += f"**{count}** {name} with {info[1]} points\n"
        embed = discord.Embed(
            title="Leaderboard",
            description=leaders,
        )
        await ctx.send(embed=embed)

    @trivia.error
    async def trivia_error(self, ctx, error):
        await ctx.send(
            embed=discord.Embed(
                title='Error',
                description="Please notify a server administrator to add this permission. This permission adds an anticheat measure to the trivia game and makes the game fairer for all."
            ))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        msg = await self.bot.get_channel(payload.channel_id).fetch_message(
            payload.message_id)
        if msg.author.name == "Public Bot-Testing":
            message = await self.bot.get_channel(
                payload.channel_id).fetch_message(payload.message_id)

            for reaction in message.reactions:
                if (not payload.member.bot
                        and payload.member in await reaction.users().flatten()
                        and reaction.emoji != payload.emoji.name):
                    await message.remove_reaction(reaction.emoji,
                                                  payload.member)


    async def url_request(self,value: int):
        """Returns data for trivia questions"""
        url = ("https://opentdb.com/api.php?amount=1&category=" + str(value) +
              "&type=multiple&token=" + self.TOKEN_ID)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        responsecode = data["response_code"]
        if str(responsecode) == "4":
            url2 = f"https://opentdb.com/api_token.php?command=reset&token={self.TOKEN_ID}"

        elif str(responsecode) == "3":
            url2 = "https://opentdb.com/api_token.php?command=request"
            response2 = urllib.request.urlopen(url2)
            data2 = json.load(response2)
            self.TOKEN_ID = data2["token"]
            data = await self.url_request(value)
            return data
        else:
            question = data["results"]
            for f in question:
                data[0] = f["category"]
                data[1] = f["difficulty"]
                correct_answer = f["correct_answer"]
                answers = f["incorrect_answers"]
                data[2] = f["question"]

            answers.append(correct_answer)

            random.shuffle(answers)

            correct = correct_answer

            answers[0] = answers[0].replace("&#039;", "'")
            answers[1] = answers[1].replace("&#039;", "'")
            answers[2] = answers[2].replace("&#039;", "'")
            answers[3] = answers[3].replace("&#039;", "'")

            if answers[0] == correct:
                correct = 1
            if answers[1] == correct:
                correct = 2
            if answers[2] == correct:
                correct = 3
            if answers[3] == correct:
                correct = 4

            answers[0] = answers[0].replace("&amp;", "&")
            answers[1] = answers[1].replace("&amp;", "&")
            answers[2] = answers[2].replace("&amp;", "&")
            answers[3] = answers[3].replace("&amp;", "&")

            data[3] = answers[0]
            data[4] = answers[1]
            data[5] = answers[2]
            data[6] = answers[3]
            data[7] = correct

            data[2] = data[2].replace("&quot;", '"')
            data[2] = data[2].replace("&#039;", "'")

            return data


def setup(bot):
    """Load the bot Cog"""
    bot.add_cog(TriviaCog(bot))
