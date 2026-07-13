import discord
from typing import Callable

class DispatchConsoleView(discord.ui.View):
    """Main dispatch console with Create Dispatch and Panic Alarm buttons."""
    
    def __init__(self, create_callback: Callable, panic_callback: Callable):
        super().__init__(timeout=None)
        self.create_callback = create_callback
        self.panic_callback = panic_callback
    
    @discord.ui.button(
        label="Create Dispatch",
        style=discord.ButtonStyle.primary,
        emoji="🚨",
        custom_id="create_dispatch"
    )
    async def create_dispatch_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        """Handle Create Dispatch button click."""
        await self.create_callback(interaction)
    
    @discord.ui.button(
        label="Panic Alarm",
        style=discord.ButtonStyle.danger,
        emoji="🚨",
        custom_id="panic_alarm"
    )
    async def panic_alarm_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        """Handle Panic Alarm button click."""
        await self.panic_callback(interaction)


class CategorySelectView(discord.ui.View):
    """Select menu for dispatch categories."""
    
    def __init__(self, callback: Callable):
        super().__init__(timeout=300)
        self.callback = callback
    
    @discord.ui.select(
        placeholder="Select dispatch category...",
        custom_id="category_select",
        min_values=1,
        max_values=1,
    )
    async def select_category(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ) -> None:
        """Handle category selection."""
        await interaction.response.defer()
        await self.callback(interaction, select.values[0])
    
    def set_options(self, options: list):
        """Set the select menu options."""
        if self.children:
            self.children[0].options = options
