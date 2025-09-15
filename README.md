# Brawl Mates System

![Brawl Stars Logo](https://example.com/brawl-stars-logo.png) <!-- Optional: Add a logo -->

A powerful Discord bot for Brawl Stars that helps you find teammates, manage profiles, and conquer challenges. Completely free and open-source!

## 🌟 Features

- **Team Search**: Find suitable teammates for your Brawl Stars adventures
- **Profiles**: Manage and display your Brawl Stars profiles
- **Challenges**: Stay updated with the latest Brawl Stars challenges
- **Map Info**: Get detailed information about current maps and modes
- **Random Brawlers**: Discover new brawlers with our randomizer
- **Multi-language**: Supports multiple languages for global players

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- A Discord bot token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Brawl Stars API key (from [Supercell Developer](https://developer.supercell.com/))

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/BMS.git
   cd BMS
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `data/env.json.example` to `data/env.json`
   - Add your Discord token and Brawl Stars API key:
     ```json
     {
       "TOKEN": "your-discord-bot-token",
       "BsApi": "your-brawl-stars-api-key"
     }
     ```

4. **Start the bot**:
   ```bash
   python BMS.py
   ```

## 📖 Usage

After starting, you can invite the bot to your Discord server. Use the following commands:

### Team Finding
- `/quick_mates` - Post a new quick search for teammates
- `/find_mates` - Post a new casual inquiry for teammates
- `/find_esport` - Post a new esport inquiry for competitive teams
- `/cancel_search` - Remove your latest search posts

### Profile Management
- `/brawl_profile` - Get your Brawl Stars profile's meta info
- `/brawl_ranks` - Get your Brawl Stars profile's brawler ranks
- `/brawl_mastery` - Get your Brawl Stars profile's brawler masterys
- `/save_id` - Save your Brawl Stars ID (#) for result tracking

### Challenges & Random
- `/challenge` - Get a random Brawl Stars challenge
- `/random_brawlers` - Get random brawlers (with filters)

### Utility
- `/get_invite_link` - Look up invite link for a server (admin only)
- `/set_language` - Set the language for the bot
- `/help` - Contact info for help
- `/invite` - Get the bot invitation link

For more details on each command, use `/help` in Discord.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to your branch: `git push origin feature/new-feature`
5. Create a Pull Request

### Development Guidelines
- Use clear, descriptive commit messages
- Add tests for new features
- Keep the code clean and documented
- Respect the existing code structure

---

**Note**: Make sure to never commit sensitive data (like tokens) to the repository. Always use `.gitignore` and environment variables.

Have fun brawling! ⚔️
