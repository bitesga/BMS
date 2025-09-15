from discord.ext import commands
import discord, json
from discord import app_commands
import mongodb
import random

# Daten laden
with open("data/challenges.json", "r", encoding="UTF-8") as f:
  bsChallengesList = json.load(f)
  

class bsChallenges(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot

  # Get your Random Challenge
  @app_commands.command(description="get a random bs challenge")
  async def challenge(self, interaction: discord.Interaction):
    # Fetch selected language
    options = mongodb.findGuildOptions(interaction.guild.id)
    language = options["language"]

    challenge = random.choice(bsChallengesList)
    description = challenge["content"][language]
    embed = discord.Embed(title=challenge["title"][language], description=description, color=int("000000", 16))
    embed.set_thumbnail(url="https://i.imgur.com/Eg6oy61.png")
    
    await interaction.response.send_message(embed=embed)

      
  @challenge.error
  async def challenge_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.NoPrivateMessage):
      return await interaction.response.send_message("Command can't be run in Private Messages.", delete_after=5, ephemeral=True)
    else:
      return await interaction.response.send_message(f"Unknown error: {error}", delete_after=5, ephemeral=True)
    
    
async def setup(bot):
  await bot.add_cog(bsChallenges(bot))
