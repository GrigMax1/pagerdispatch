import discord
from typing import Callable, Dict
from utils.permissions import PermissionManager

class DispatchButtonsView(discord.ui.View):
    """Persistent buttons for officer responses on dispatches."""
    
    def __init__(self, dispatch_id: int, callbacks: Dict[str, Callable]):
        super().__init__(timeout=None)
        self.dispatch_id = dispatch_id
        self.callbacks = callbacks
    
    @discord.ui.button(
        label="Responding",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="btn_responding"
    )
    async def responding_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        """Handle Responding button click."""
        if 'responding' in self.callbacks:
            await self.callbacks['responding'](interaction, self.dispatch_id)
    
    @discord.ui.button(
        label="En Route",
        style=discord.ButtonStyle.primary,
        emoji="🚓",
        custom_id="btn_en_route"
    )
    async def en_route_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        """Handle En Route button click."""
        if 'en_route' in self.callbacks:
            await self.callbacks['en_route'](interaction, self.dispatch_id)
    
    @discord.ui.button(
        label="On Scene",
        style=discord.ButtonStyle.primary,
        emoji="📍",
        custom_id="btn_on_scene"
    )
    async def on_scene_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        """Handle On Scene button click."""
        if 'on_scene' in self.callbacks:
            await self.callbacks['on_scene'](interaction, self.dispatch_id)
    
    @discord.ui.button(
        label="Taking Command",
        style=discord.ButtonStyle.primary,
        emoji="👮",
        custom_id="btn_command"
    )
    async def command_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        """Handle Taking Command button click."""
        if 'command' in self.callbacks:
            await self.callbacks['command'](interaction, self.dispatch_id)
    
    @discord.ui.button(
        label="Unable",
        style=discord.ButtonStyle.danger,
        emoji="❌",
        custom_id="btn_unable"
    )
    async def unable_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        """Handle Unable button click."""
        if 'unable' in self.callbacks:
            await self.callbacks['unable'](interaction, self.dispatch_id)
    
    @discord.ui.button(
        label="Close Dispatch",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id="btn_close"
    )
    async def close_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        """Handle Close Dispatch button click (Supervisor only)."""
        if not PermissionManager.can_close_dispatch(interaction.user):
            await interaction.response.send_message(
                "❌ You don't have permission to close dispatches.",
                ephemeral=True
            )
            return
        
        if 'close' in self.callbacks:
            await self.callbacks['close'](interaction, self.dispatch_id)
