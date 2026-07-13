import discord
from discord.ext import commands
from database.database import Database
from config import Config
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

config = Config()

class DispatchBot(commands.Bot):
    """Main Discord bot class for SAPD Dispatch."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        self.db: Database = None
    
    async def setup_hook(self):
        """Setup hook called before the bot connects."""
        logger.info("Setting up bot...")
        
        # Initialize database
        self.db = Database()
        await self.db.initialize()
        logger.info("Database initialized")
        
        # Load cogs
        cogs_path = Path(__file__).parent / 'cogs'
        for cog_file in cogs_path.glob('*.py'):
            if cog_file.name.startswith('_'):
                continue
            
            cog_name = cog_file.stem
            try:
                await self.load_extension(f'cogs.{cog_name}')
                logger.info(f"Loaded cog: {cog_name}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog_name}: {e}")
        
        # Sync commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user}")
        logger.info(f"Bot ID: {self.user.id}")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        
        # Set status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for dispatches 🚨"
        )
        await self.change_presence(activity=activity)
    
    async def on_error(self, event, *args, **kwargs):
        """Called when an error occurs."""
        logger.error(f"Error in {event}", exc_info=True)
    
    async def close(self):
        """Cleanup on bot shutdown."""
        if self.db:
            await self.db.close()
        await super().close()


def main():
    """Main entry point."""
    token = config.get_token()
    bot = DispatchBot()
    
    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
