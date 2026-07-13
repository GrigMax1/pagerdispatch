import discord
from discord.ext import commands
from database.database import Database
from config import Config
import logging

logger = logging.getLogger(__name__)
config = Config()

class LoggingCog(commands.Cog):
    """Handles logging of dispatch actions to database and Discord."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = None
    
    async def cog_load(self):
        """Initialize database connection."""
        self.db = self.bot.db
    
    async def log_to_database(
        self,
        dispatch_id: int,
        action: str,
        user_name: str,
        user_id: int,
        details: str = None
    ) -> None:
        """Log action to database."""
        try:
            await self.db.log_action(dispatch_id, action, user_name, user_id, details)
            logger.info(f"Logged action: {action} for dispatch {dispatch_id}")
        except Exception as e:
            logger.error(f"Error logging action: {e}")
    
    async def log_to_discord(
        self,
        embed: discord.Embed
    ) -> None:
        """Log action to Discord log channel."""
        try:
            log_channel_id = config.log_channel_id
            if not log_channel_id:
                return
            
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error sending log to Discord: {e}")
    
    def create_log_embed(
        self,
        action: str,
        dispatch_number: str,
        user_name: str,
        details: str = None
    ) -> discord.Embed:
        """Create an embed for logging."""
        embed = discord.Embed(
            title=f"📋 {action}",
            description=f"Dispatch {dispatch_number}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="👤 User", value=user_name, inline=True)
        
        if details:
            embed.add_field(name="📝 Details", value=details, inline=False)
        
        return embed

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LoggingCog(bot))
