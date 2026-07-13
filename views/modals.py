import discord
from typing import Callable, Optional

class DispatchTitleModal(discord.ui.Modal, title="Create Dispatch"):
    """Modal for entering dispatch information."""
    
    title_input = discord.ui.TextInput(
        label="Dispatch Title",
        placeholder="e.g., Officer Down, Vehicle Pursuit",
        required=True,
        max_length=100
    )
    
    location_input = discord.ui.TextInput(
        label="Location",
        placeholder="e.g., Idlewood Motel",
        required=True,
        max_length=150
    )
    
    situation_input = discord.ui.TextInput(
        label="Situation",
        placeholder="Describe the incident...",
        required=True,
        max_length=1000,
        style=discord.TextInputStyle.paragraph
    )
    
    def __init__(self, callback: Callable):
        super().__init__()
        self.callback_fn = callback
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Called when the modal is submitted."""
        await interaction.response.defer()
        await self.callback_fn(
            interaction,
            self.title_input.value,
            self.location_input.value,
            self.situation_input.value
        )


class UnitSelectionModal(discord.ui.View):
    """View for unit selection yes/no buttons."""
    
    def __init__(self, callback: Callable, unit_type: str):
        super().__init__(timeout=300)
        self.callback_fn = callback
        self.unit_type = unit_type
        self.result: Optional[bool] = None
    
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green, emoji="✅")
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """User selected Yes."""
        self.result = True
        await interaction.response.defer()
        await self.callback_fn(interaction, self.unit_type, True)
    
    @discord.ui.button(label="No", style=discord.ButtonStyle.red, emoji="❌")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """User selected No."""
        self.result = False
        await interaction.response.defer()
        await self.callback_fn(interaction, self.unit_type, False)
