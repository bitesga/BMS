from discord.ext import commands
import discord
from discord import app_commands
import mongodb
import json

format = "%a, %d %b %Y, %H:%M"

# Texte laden
with open("languages/generalTexts.json", "r", encoding="UTF-8") as f:
  texts = json.load(f)

# LinkButton Klasse
class LinkButton(discord.ui.Button):
  def __init__(self, label, url, emoji=None):
    super().__init__(label=label, style=discord.ButtonStyle.link, url=url, emoji=emoji)


# View Klasse zum Anzeigen der Items wie Buttons und Auswahllisten
class View(discord.ui.View):
    def __init__(self, items):
        super().__init__(timeout=None)
        for item in items:
            self.add_item(item)


# SelectLanguage Klasse
class SelectLanguage(discord.ui.Select):
    def __init__(self, bot, originalInteraction):
        options = [
            discord.SelectOption(label="German", emoji="🇩🇪", value="German 🇩🇪"),
            discord.SelectOption(label="English", emoji="🇬🇧", value="English 🇬🇧"),
            discord.SelectOption(label="Spanish", emoji="🇪🇸", value="Spanish 🇪🇸"),
            discord.SelectOption(label="French", emoji="🇫🇷", value="French 🇫🇷"),
            discord.SelectOption(label="Russian", emoji="🇷🇺", value="Russian 🇷🇺")
        ]
        
        super().__init__(placeholder="Select a language", options=options)
        self.bot = bot
        self.originalInteraction = originalInteraction

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_options = mongodb.findGuildOptions(interaction.guild.id)
        language = self.values[0].lower().split(" ")[0]
        guild_options["language"] = language
        mongodb.saveGuild(guild_options)
        await self.originalInteraction.edit_original_response(embed=currentSettingEmbed(interaction.guild.id))

        # Text in Team Inquiry Channel umändern
        findMatesCategory = None
        i = 0
        while not findMatesCategory and i < len(interaction.guild.categories):
          if "findmates" in interaction.guild.categories[i].name.lower().replace(" ", ""):
            findMatesCategory = interaction.guild.categories[i]
          i += 1

        # Erstellen falls nicht da
        if not findMatesCategory:
          return

        teamInquiriesChannel = None
        i = 0
        while not teamInquiriesChannel and i < len(findMatesCategory.text_channels):
          if "team-inquiries" in findMatesCategory.text_channels[i].name.lower():
            teamInquiriesChannel = findMatesCategory.text_channels[i]
          i += 1

        if teamInquiriesChannel:
          newInquiryChannel = await teamInquiriesChannel.clone()
          await teamInquiriesChannel.delete(reason="language change")
          # Hier neue Nachricht schicken
          await newInquiryChannel.send(embed=buildLanguageEmbed("findTeamsAnnouncement", language))
          

def getNiceFormatLanguage(language):
    if language == "german":
      return "German 🇩🇪"
    elif language == "english":
      return "English 🇬🇧"
    elif language == "spanish":
      return "Spanish 🇪🇸"
    elif language == "russian":
       return "Russian 🇷🇺"
    else:
      return "French 🇫🇷",

def buildLanguageEmbed(content, language):
  description = ""
  for text in texts[content]["content"][language]:
    description += text

  return discord.Embed(title=texts[content]["title"][language], description=description, color=int("ffffff", 16))

def currentSettingEmbed(guild_id):
  guild_options = mongodb.findGuildOptions(guild_id)
  # Sprache anzeigen
  description = f"{getNiceFormatLanguage(guild_options['language'])}"
  
  return discord.Embed(title="Current Language", description=description, color=discord.Color.dark_gray())


class Utility(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot
    
  # Öffnet Server Einstellungen
  @app_commands.checks.has_permissions(administrator=True, manage_channels=True)
  @app_commands.command(description="set the language for the bot")
  async def set_language(self, interaction: discord.Interaction):
    viewItems = [SelectLanguage(self.bot, interaction)]
    await interaction.response.send_message(embed=currentSettingEmbed(interaction.guild.id), view=View(viewItems), ephemeral=True)


  @set_language.error
  async def set_language_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.NoPrivateMessage):
      return await interaction.response.send_message("Command can't be run in Private Messages.", delete_after=5, ephemeral=True)
    else:
      return await interaction.response.send_message(f"Unknown error: {error}", delete_after=5, ephemeral=True)


  # Help Command -> get Support
  @app_commands.command(description="contact info for help")
  async def help(self, interaction: discord.Interaction):
    # Ausgewählte Sprache fetchen
    options = mongodb.findGuildOptions(interaction.guild.id)
    language = options["language"]

    embed = buildLanguageEmbed("helpCommand", language)
    embed.set_image(url="https://media.discordapp.net/attachments/1216040586348593213/1223366470088790046/bms_avatar.jpg")
    viewItems = [LinkButton("Linktree", "https://linktr.ee/bsystems", "<:Linktree:1218980236260278292>")]
    await interaction.response.send_message(embed=embed, view=View(viewItems))

  @help.error
  async def help_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.NoPrivateMessage):
      return await interaction.response.send_message("Command can't be run in Private Messages.", delete_after=5, ephemeral=True)
    else:
      return await interaction.response.send_message(f"Unknown error: {error}", delete_after=5, ephemeral=True)


  # Invite Command -> get Link
  @app_commands.command(description="get the bot invitation link")
  async def invite(self, interaction: discord.Interaction):
    # Ausgewählte Sprache fetchen
    options = mongodb.findGuildOptions(interaction.guild.id)
    language = options["language"]

    viewItems = [LinkButton(texts["inviteLabel"][language], "https://discord.com/oauth2/authorize?client_id=1223344546260193280&permissions=8&scope=bot", "<:discord:1216307276927733800>"),
                 LinkButton(texts["topGGLabel"][language], "https://top.gg/bot/1223344546260193280", "<:topgg:1226193810338611301>")]
    await interaction.response.send_message(embed=buildLanguageEmbed("inviteCommand", language), view=View(viewItems))

  @invite.error
  async def invite_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.NoPrivateMessage):
      return await interaction.response.send_message("Command can't be run in Private Messages.", delete_after=5, ephemeral=True)
    else:
      return await interaction.response.send_message(f"Unknown error: {error}", delete_after=5, ephemeral=True)


async def setup(bot):
  await bot.add_cog(Utility(bot))