import discord
from discord.ext import commands
from discord import app_commands
from database.database import Database
from config import Config
from utils.permissions import PermissionManager
from utils.embeds import DispatchEmbedBuilder
from views.dispatch_console import DispatchConsoleView
import logging

logger = logging.getLogger(__name__)
config = Config()

class SetupCog(commands.Cog):
    """Handles setup commands for the dispatch system."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = None
    
    async def cog_load(self):
        """Initialize database connection."""
        self.db = self.bot.db
    
    @app_commands.command(
        name="setup_dispatch",
        description="Create the permanent dispatch console (Admin only)"
    )
    async def setup_dispatch(self, interaction: discord.Interaction) -> None:
        """Setup the dispatch console."""
        if not PermissionManager.can_setup_console(interaction.user):
            await interaction.response.send_message(
                "❌ You must be an administrator to use this command.",
                ephemeral=True
            )
            return
        
        try:
            await interaction.response.defer()
            
            # Check if console already exists
            existing_console = await self.db.get_setting('dispatch_console_message_id')
            if existing_console:
                await interaction.followup.send(
                    "ℹ️ Dispatch console already exists. Use `/setup_dispatch_force` to recreate it.",
                    ephemeral=True
                )
                return
            
            # Get the target channel
            channel_id = config.dispatch_console_channel_id
            if not channel_id:
                await interaction.followup.send(
                    "❌ Dispatch console channel not configured. Update config.json",
                    ephemeral=True
                )
                return
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                await interaction.followup.send(
                    "❌ Could not find dispatch console channel.",
                    ephemeral=True
                )
                return
            
            # Create the console embed
            embed = DispatchEmbedBuilder.create_console_embed()
            
            # Create the view with callbacks
            view = DispatchConsoleView(
                create_callback=self.bot.get_cog('DispatchCog').handle_create_dispatch,
                panic_callback=self.bot.get_cog('DispatchCog').handle_panic_alarm
            )
            
            # Send the message
            message = await channel.send(embed=embed, view=view)
            
            # Save console message ID to database
            await self.db.set_setting('dispatch_console_message_id', str(message.id))
            
            await interaction.followup.send(
                f"✅ Dispatch console created in <#{channel_id}>",
                ephemeral=True
            )
            logger.info(f"Dispatch console created by {interaction.user.name}")
        
        except Exception as e:
            logger.error(f"Error setting up dispatch console: {e}")
            await interaction.followup.send(
                f"❌ Error creating console: {str(e)}",
                ephemeral=True
            )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SetupCog(bot))
