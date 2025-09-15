from discord.ext import commands
import discord, json
from discord import app_commands
import mongodb
import random
from typing import Literal
import requests

brawlers = requests.get("https://api.brawlapi.com/v1/brawlers").json()["list"]

# ENV Daten laden
with open("data/challenges.json", "r", encoding="UTF-8") as f:
  bsChallenges = json.load(f)
  

brawler_classes = [
  app_commands.Choice(name="Damage Dealer", value=1),
  app_commands.Choice(name="Tank", value=2),
  app_commands.Choice(name="Marksman", value=3),
  app_commands.Choice(name="Artillery", value=4),
  app_commands.Choice(name="Controller", value=5),
  app_commands.Choice(name="Assassin", value=6),
  app_commands.Choice(name="Support", value=7),
  app_commands.Choice(name="Unknown", value=8),
]

brawler_rarities = [
  app_commands.Choice(name="Rare", value=2),
  app_commands.Choice(name="Super Rare", value=3),
  app_commands.Choice(name="Epic", value=4),
  app_commands.Choice(name="Mythic", value=5),
  app_commands.Choice(name="Legendary", value=6)
]

class randomBrawlers(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot
    
  # Get your Random Brawler
  @app_commands.command(description="get random brawlers")
  @app_commands.choices(brawler_class=brawler_classes, brawler_rarity=brawler_rarities)
  async def random_brawlers(self, interaction: discord.Interaction, amount: Literal[1, 2, 3, 5]=1, brawler_class: app_commands.Choice[int]=None, brawler_rarity: app_commands.Choice[int]=None):
    randomPicks = []

    # Liste ggf. filtern
    if brawler_class and brawler_rarity:
        brawlersToChooseFrom = []
        for brawler in brawlers:
           if brawler_class.name == brawler["class"]["name"] and brawler_rarity.name == brawler["rarity"]["name"]:
              brawlersToChooseFrom.append(brawler)

    elif brawler_class:
        brawlersToChooseFrom = []
        for brawler in brawlers:
           if brawler_class.name == brawler["class"]["name"]:
              brawlersToChooseFrom.append(brawler)

    elif brawler_rarity:
        brawlersToChooseFrom = []
        for brawler in brawlers:
           if brawler_rarity.name == brawler["rarity"]["name"]:
              brawlersToChooseFrom.append(brawler)

    else:
        brawlersToChooseFrom = brawlers

    # Random Picks raussuchen
    if len(brawlersToChooseFrom) <= amount:
       randomPicks = brawlersToChooseFrom
    else:
        for _ in range(amount):
            newBrawler = random.choice(brawlersToChooseFrom)
            # So oft neuen Brawler ziehen bis man einen hat der nicht schon in der liste ist
            while newBrawler in randomPicks:
                newBrawler = random.choice(brawlersToChooseFrom)
               
            randomPicks.append(newBrawler)

    # Embeds machen und schicken
    randomPicksEmbeds = []
    for brawler in randomPicks:
        embed = discord.Embed(title=brawler["name"], color=int(brawler["rarity"]["color"].removeprefix("#"), 16))
        embed.set_thumbnail(url=brawler["imageUrl"])
        randomPicksEmbeds.append(embed)

    await interaction.response.send_message(embeds=randomPicksEmbeds)
      
  @random_brawlers.error
  async def random_brawlers_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.NoPrivateMessage):
      return await interaction.response.send_message("Command can't be run in Private Messages.", delete_after=5, ephemeral=True)
    else:
      return await interaction.response.send_message(f"Unknown error: {error}", delete_after=5, ephemeral=True)
    
    
async def setup(bot):
  await bot.add_cog(randomBrawlers(bot))