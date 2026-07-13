import discord
from datetime import datetime
from config import Config
from utils.helpers import TimeHelper, DispatchCategories

config = Config()

class DispatchEmbedBuilder:
    """Builds embeds for dispatch messages."""
    
    @staticmethod
    def create_console_embed() -> discord.Embed:
        """Create the dispatch console embed."""
        embed = discord.Embed(
            title="🚔 SAPD DISPATCH CONSOLE",
            description="Welcome to the San Andreas Police Department Dispatch System\n\nClick a button below to get started.",
            color=config.embed_color
        )
        
        embed.set_thumbnail(url=config.department_logo_url)
        embed.add_field(
            name="📋 Instructions",
            value="**Create Dispatch** - Report an emergency or operation\n**Panic Alarm** - Activate emergency response",
            inline=False
        )
        embed.set_footer(text=config.footer_text)
        embed.timestamp = TimeHelper.get_current_time()
        
        return embed
    
    @staticmethod
    def create_dispatch_embed(
        dispatch_number: str,
        category: str,
        title: str,
        location: str,
        situation: str,
        created_by: str,
        swat_required: bool,
        detectives_required: bool,
        traffic_required: bool,
        status: str,
        created_at: datetime
    ) -> discord.Embed:
        """Create a dispatch embed."""
        category_data = DispatchCategories.get_category_data(category)
        emoji = category_data.get('emoji', '📋')
        category_name = category_data.get('name', category)
        
        embed = discord.Embed(
            title=f"{emoji} {title}",
            description=situation,
            color=config.embed_color
        )
        
        embed.add_field(
            name="📍 Dispatch",
            value=dispatch_number,
            inline=True
        )
        
        embed.add_field(
            name="📁 Category",
            value=category_name,
            inline=True
        )
        
        embed.add_field(
            name="📌 Location",
            value=location,
            inline=False
        )
        
        embed.add_field(
            name="⚫ SWAT",
            value="✅ Required" if swat_required else "❌ Not Required",
            inline=True
        )
        
        embed.add_field(
            name="🕵️ Detectives",
            value="✅ Required" if detectives_required else "❌ Not Required",
            inline=True
        )
        
        embed.add_field(
            name="🚧 Traffic Division",
            value="✅ Required" if traffic_required else "❌ Not Required",
            inline=True
        )
        
        embed.add_field(
            name="👮 Created By",
            value=created_by,
            inline=True
        )
        
        status_emoji = '🟢' if status == 'Active' else '⚫'
        embed.add_field(
            name="📊 Status",
            value=f"{status_emoji} {status}",
            inline=True
        )
        
        embed.add_field(
            name="🕐 Time",
            value=TimeHelper.format_time(created_at),
            inline=True
        )
        
        embed.set_footer(text=config.footer_text)
        embed.timestamp = TimeHelper.get_current_time()
        
        return embed
    
    @staticmethod
    def add_officer_statuses(
        embed: discord.Embed,
        responding: list,
        en_route: list,
        on_scene: list,
        command: list
    ) -> discord.Embed:
        """Add officer status sections to embed."""
        responding_names = ', '.join([o['user_name'] for o in responding]) if responding else 'None'
        en_route_names = ', '.join([o['user_name'] for o in en_route]) if en_route else 'None'
        on_scene_names = ', '.join([o['user_name'] for o in on_scene]) if on_scene else 'None'
        command_names = ', '.join([o['user_name'] for o in command]) if command else 'None'
        
        embed.add_field(
            name="✅ Responding",
            value=responding_names,
            inline=False
        )
        
        embed.add_field(
            name="🚓 En Route",
            value=en_route_names,
            inline=False
        )
        
        embed.add_field(
            name="📍 On Scene",
            value=on_scene_names,
            inline=False
        )
        
        embed.add_field(
            name="👮 Command",
            value=command_names,
            inline=False
        )
        
        return embed
