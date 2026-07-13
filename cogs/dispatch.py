import discord
from discord.ext import commands
from discord import app_commands
from database.database import Database
from config import Config
from utils.permissions import PermissionManager
from utils.embeds import DispatchEmbedBuilder
from utils.helpers import (
    DispatchCategories,
    DispatchStatuses,
    LogActions,
    TimeHelper
)
from views.dispatch_console import CategorySelectView
from views.dispatch_buttons import DispatchButtonsView
from views.modals import DispatchTitleModal, UnitSelectionModal
import logging
from typing import Optional

logger = logging.getLogger(__name__)
config = Config()

class DispatchCog(commands.Cog):
    """Main dispatch system cog."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Database = None
        self.pending_dispatches: dict = {}  # Track pending dispatch data
    
    async def cog_load(self):
        """Initialize database connection."""
        self.db = self.bot.db
    
    # ==================== Create Dispatch Flow ====================
    
    async def handle_create_dispatch(self, interaction: discord.Interaction) -> None:
        """Handle Create Dispatch button click."""
        if not PermissionManager.can_create_dispatch(interaction.user):
            await interaction.response.send_message(
                "❌ You don't have permission to create dispatches.",
                ephemeral=True
            )
            return
        
        # Create category select view
        view = CategorySelectView(callback=self.handle_category_select)
        view.set_options(DispatchCategories.get_select_options())
        
        await interaction.response.send_message(
            "Please select a dispatch category:",
            view=view,
            ephemeral=True
        )
    
    async def handle_category_select(
        self,
        interaction: discord.Interaction,
        category: str
    ) -> None:
        """Handle category selection."""
        # Show modal for dispatch details
        modal = DispatchTitleModal(callback=self.handle_dispatch_modal_submit)
        await interaction.response.send_modal(modal)
        
        # Store selected category for later
        self.pending_dispatches[interaction.user.id] = {'category': category}
    
    async def handle_dispatch_modal_submit(
        self,
        interaction: discord.Interaction,
        title: str,
        location: str,
        situation: str
    ) -> None:
        """Handle dispatch modal submission."""
        try:
            # Get stored category
            pending = self.pending_dispatches.get(interaction.user.id, {})
            category = pending.get('category', 'emergency')
            
            # Prompt for SWAT required
            await interaction.followup.send(
                "⚫ **SWAT Required?**",
                view=UnitSelectionModal(
                    callback=lambda inter, unit, result: self.handle_unit_selection(
                        inter, title, location, situation, category, unit, result
                    ),
                    unit_type='swat'
                ),
                ephemeral=True
            )
        
        except Exception as e:
            logger.error(f"Error in dispatch modal submission: {e}")
            await interaction.followup.send(
                f"❌ Error processing dispatch: {str(e)}",
                ephemeral=True
            )
    
    async def handle_unit_selection(
        self,
        interaction: discord.Interaction,
        title: str,
        location: str,
        situation: str,
        category: str,
        unit_type: str,
        result: bool
    ) -> None:
        """Handle unit selection and prompt for next unit."""
        try:
            # Store result
            pending = self.pending_dispatches.get(interaction.user.id, {})
            
            if unit_type == 'swat':
                pending['swat_required'] = result
                
                # Prompt for Detectives
                await interaction.followup.send(
                    "🕵️ **Detectives Required?**",
                    view=UnitSelectionModal(
                        callback=lambda inter, unit, res: self.handle_unit_selection(
                            inter, title, location, situation, category, unit, res
                        ),
                        unit_type='detective'
                    ),
                    ephemeral=True
                )
            
            elif unit_type == 'detective':
                pending['detectives_required'] = result
                
                # Prompt for Traffic Division
                await interaction.followup.send(
                    "🚧 **Traffic Division Required?**",
                    view=UnitSelectionModal(
                        callback=lambda inter, unit, res: self.handle_unit_selection(
                            inter, title, location, situation, category, unit, res
                        ),
                        unit_type='traffic'
                    ),
                    ephemeral=True
                )
            
            elif unit_type == 'traffic':
                pending['traffic_required'] = result
                
                # All units selected, create dispatch
                await self.create_dispatch(
                    interaction,
                    title,
                    location,
                    situation,
                    category,
                    pending.get('swat_required', False),
                    pending.get('detectives_required', False),
                    pending.get('traffic_required', False)
                )
                
                # Clean up pending data
                del self.pending_dispatches[interaction.user.id]
        
        except Exception as e:
            logger.error(f"Error in unit selection: {e}")
            await interaction.followup.send(
                f"❌ Error processing selection: {str(e)}",
                ephemeral=True
            )
    
    async def create_dispatch(
        self,
        interaction: discord.Interaction,
        title: str,
        location: str,
        situation: str,
        category: str,
        swat_required: bool,
        detectives_required: bool,
        traffic_required: bool
    ) -> None:
        """Create and send the dispatch."""
        try:
            # Get next dispatch number
            dispatch_number = await self.db.get_next_dispatch_number()
            
            # Get dispatch channel
            dispatch_channel_id = config.dispatch_channel_id
            if not dispatch_channel_id:
                await interaction.followup.send(
                    "❌ Dispatch channel not configured.",
                    ephemeral=True
                )
                return
            
            dispatch_channel = self.bot.get_channel(dispatch_channel_id)
            if not dispatch_channel:
                await interaction.followup.send(
                    "❌ Could not find dispatch channel.",
                    ephemeral=True
                )
                return
            
            # Create dispatch embed
            created_at = TimeHelper.get_current_time()
            embed = DispatchEmbedBuilder.create_dispatch_embed(
                dispatch_number,
                category,
                title,
                location,
                situation,
                interaction.user.name,
                swat_required,
                detectives_required,
                traffic_required,
                DispatchStatuses.ACTIVE,
                created_at
            )
            
            # Create button view
            callbacks = {
                'responding': self.handle_officer_response,
                'en_route': self.handle_officer_en_route,
                'on_scene': self.handle_officer_on_scene,
                'command': self.handle_officer_command,
                'unable': self.handle_officer_unable,
                'close': self.handle_close_dispatch
            }
            view = DispatchButtonsView(dispatch_id=0, callbacks=callbacks)  # dispatch_id will be set after creation
            
            # Send dispatch to channel
            dispatch_message = await dispatch_channel.send(embed=embed, view=view)
            
            # Store dispatch in database
            dispatch_id = await self.db.create_dispatch(
                dispatch_number,
                category,
                title,
                location,
                situation,
                interaction.user.name,
                swat_required,
                detectives_required,
                traffic_required,
                dispatch_message.id
            )
            
            # Update view with correct dispatch_id
            view.dispatch_id = dispatch_id
            
            # Log action
            logging_cog = self.bot.get_cog('LoggingCog')
            if logging_cog:
                await logging_cog.log_to_database(
                    dispatch_id,
                    LogActions.DISPATCH_CREATED,
                    interaction.user.name,
                    interaction.user.id,
                    f"Category: {category}"
                )
                
                log_embed = logging_cog.create_log_embed(
                    LogActions.DISPATCH_CREATED,
                    dispatch_number,
                    interaction.user.name,
                    f"Category: {category}, Location: {location}"
                )
                await logging_cog.log_to_discord(log_embed)
            
            # Send role mentions
            mentions = self.get_role_mentions(swat_required, detectives_required, traffic_required)
            if mentions:
                await dispatch_channel.send(mentions)
            
            # Confirm creation
            await interaction.followup.send(
                f"✅ Dispatch {dispatch_number} created successfully!",
                ephemeral=True
            )
            
            logger.info(f"Dispatch {dispatch_number} created by {interaction.user.name}")
        
        except Exception as e:
            logger.error(f"Error creating dispatch: {e}")
            await interaction.followup.send(
                f"❌ Error creating dispatch: {str(e)}",
                ephemeral=True
            )
    
    # ==================== Panic Alarm ====================
    
    async def handle_panic_alarm(self, interaction: discord.Interaction) -> None:
        """Handle Panic Alarm button click."""
        if not PermissionManager.can_use_panic_alarm(interaction.user):
            await interaction.response.send_message(
                "❌ You don't have permission to use panic alarm.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            # Create panic dispatch
            await self.create_dispatch(
                interaction,
                title="PANIC ALARM",
                location="Unknown",
                situation="Officer activated emergency panic button.",
                category='emergency',
                swat_required=True,
                detectives_required=False,
                traffic_required=False
            )
            
            # Log panic alarm
            logging_cog = self.bot.get_cog('LoggingCog')
            if logging_cog:
                await logging_cog.log_to_database(
                    0,  # Will be set in create_dispatch
                    LogActions.PANIC_ALARM,
                    interaction.user.name,
                    interaction.user.id
                )
        
        except Exception as e:
            logger.error(f"Error handling panic alarm: {e}")
            await interaction.followup.send(
                f"❌ Error activating panic alarm: {str(e)}",
                ephemeral=True
            )
    
    # ==================== Officer Response Handlers ====================
    
    async def handle_officer_response(self, interaction: discord.Interaction, dispatch_id: int) -> None:
        """Handle officer responding button."""
        await interaction.response.defer()
        await self.update_officer_status(
            interaction,
            dispatch_id,
            DispatchStatuses.RESPONDING,
            LogActions.OFFICER_RESPONDING
        )
    
    async def handle_officer_en_route(self, interaction: discord.Interaction, dispatch_id: int) -> None:
        """Handle officer en route button."""
        await interaction.response.defer()
        await self.update_officer_status(
            interaction,
            dispatch_id,
            DispatchStatuses.EN_ROUTE,
            LogActions.OFFICER_EN_ROUTE
        )
    
    async def handle_officer_on_scene(self, interaction: discord.Interaction, dispatch_id: int) -> None:
        """Handle officer on scene button."""
        await interaction.response.defer()
        await self.update_officer_status(
            interaction,
            dispatch_id,
            DispatchStatuses.ON_SCENE,
            LogActions.OFFICER_ON_SCENE
        )
    
    async def handle_officer_command(self, interaction: discord.Interaction, dispatch_id: int) -> None:
        """Handle officer taking command button."""
        await interaction.response.defer()
        await self.update_officer_status(
            interaction,
            dispatch_id,
            DispatchStatuses.TAKING_COMMAND,
            LogActions.OFFICER_TAKING_COMMAND
        )
    
    async def handle_officer_unable(self, interaction: discord.Interaction, dispatch_id: int) -> None:
        """Handle officer unable button."""
        await interaction.response.defer()
        await self.update_officer_status(
            interaction,
            dispatch_id,
            DispatchStatuses.UNABLE,
            LogActions.OFFICER_UNABLE
        )
    
    async def update_officer_status(
        self,
        interaction: discord.Interaction,
        dispatch_id: int,
        status: str,
        log_action: str
    ) -> None:
        """Update officer status on a dispatch."""
        try:
            # Check if officer already has this status
            existing_responses = await self.db.get_officers_by_status(dispatch_id, status)
            officer_already_responded = any(r['user_id'] == interaction.user.id for r in existing_responses)
            
            if officer_already_responded:
                # Remove response
                await self.db.remove_officer_response(dispatch_id, interaction.user.id)
                action_text = f"removed {status}"
            else:
                # Add or update response
                await self.db.add_officer_response(
                    dispatch_id,
                    interaction.user.id,
                    interaction.user.name,
                    status
                )
                action_text = f"set to {status}"
            
            # Log action
            logging_cog = self.bot.get_cog('LoggingCog')
            if logging_cog:
                await logging_cog.log_to_database(
                    dispatch_id,
                    log_action,
                    interaction.user.name,
                    interaction.user.id
                )
            
            # Get dispatch to update embed
            dispatch = await self.db.get_dispatch(dispatch_id)
            if dispatch:
                await self.refresh_dispatch_embed(dispatch_id)
                await interaction.followup.send(
                    f"✅ Status {action_text}",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ Dispatch not found.",
                    ephemeral=True
                )
        
        except Exception as e:
            logger.error(f"Error updating officer status: {e}")
            await interaction.followup.send(
                f"❌ Error updating status: {str(e)}",
                ephemeral=True
            )
    
    async def handle_close_dispatch(self, interaction: discord.Interaction, dispatch_id: int) -> None:
        """Handle close dispatch button (Supervisor only)."""
        try:
            if not PermissionManager.can_close_dispatch(interaction.user):
                await interaction.response.send_message(
                    "❌ You don't have permission to close dispatches.",
                    ephemeral=True
                )
                return
            
            await interaction.response.defer()
            
            # Update dispatch status
            await self.db.update_dispatch_status(
                dispatch_id,
                DispatchStatuses.CLOSED,
                interaction.user.name
            )
            
            # Log action
            logging_cog = self.bot.get_cog('LoggingCog')
            if logging_cog:
                dispatch = await self.db.get_dispatch(dispatch_id)
                if dispatch:
                    await logging_cog.log_to_database(
                        dispatch_id,
                        LogActions.DISPATCH_CLOSED,
                        interaction.user.name,
                        interaction.user.id
                    )
            
            # Refresh embed
            await self.refresh_dispatch_embed(dispatch_id)
            
            await interaction.followup.send(
                "✅ Dispatch closed successfully.",
                ephemeral=True
            )
            
            logger.info(f"Dispatch {dispatch_id} closed by {interaction.user.name}")
        
        except Exception as e:
            logger.error(f"Error closing dispatch: {e}")
            await interaction.followup.send(
                f"❌ Error closing dispatch: {str(e)}",
                ephemeral=True
            )
    
    # ==================== Utility Methods ====================
    
    async def refresh_dispatch_embed(self, dispatch_id: int) -> None:
        """Refresh dispatch embed with updated officer statuses."""
        try:
            dispatch = await self.db.get_dispatch(dispatch_id)
            if not dispatch:
                return
            
            # Get officer responses by status
            responding = await self.db.get_officers_by_status(dispatch_id, DispatchStatuses.RESPONDING)
            en_route = await self.db.get_officers_by_status(dispatch_id, DispatchStatuses.EN_ROUTE)
            on_scene = await self.db.get_officers_by_status(dispatch_id, DispatchStatuses.ON_SCENE)
            command = await self.db.get_officers_by_status(dispatch_id, DispatchStatuses.TAKING_COMMAND)
            
            # Create updated embed
            embed = DispatchEmbedBuilder.create_dispatch_embed(
                dispatch['dispatch_number'],
                dispatch['category'],
                dispatch['title'],
                dispatch['location'],
                dispatch['situation'],
                dispatch['created_by'],
                bool(dispatch['swat_required']),
                bool(dispatch['detectives_required']),
                bool(dispatch['traffic_required']),
                dispatch['status'],
                dispatch['created_at']
            )
            
            # Add officer statuses
            embed = DispatchEmbedBuilder.add_officer_statuses(
                embed,
                responding,
                en_route,
                on_scene,
                command
            )
            
            # Get dispatch message and update it
            dispatch_channel_id = config.dispatch_channel_id
            dispatch_channel = self.bot.get_channel(dispatch_channel_id)
            if dispatch_channel:
                try:
                    message = await dispatch_channel.fetch_message(dispatch['message_id'])
                    
                    # Recreate view
                    callbacks = {
                        'responding': self.handle_officer_response,
                        'en_route': self.handle_officer_en_route,
                        'on_scene': self.handle_officer_on_scene,
                        'command': self.handle_officer_command,
                        'unable': self.handle_officer_unable,
                        'close': self.handle_close_dispatch
                    }
                    view = DispatchButtonsView(dispatch_id=dispatch_id, callbacks=callbacks)
                    
                    await message.edit(embed=embed, view=view)
                except discord.NotFound:
                    logger.warning(f"Dispatch message {dispatch['message_id']} not found")
        
        except Exception as e:
            logger.error(f"Error refreshing dispatch embed: {e}")
    
    def get_role_mentions(self, swat: bool, detectives: bool, traffic: bool) -> str:
        """Generate role mentions based on dispatch requirements."""
        mentions = []
        
        # Always mention police role
        police_role_id = config.police_role_id
        if police_role_id:
            mentions.append(f"<@&{police_role_id}>")
        
        if swat:
            swat_role_id = config.swat_role_id
            if swat_role_id:
                mentions.append(f"<@&{swat_role_id}>")
        
        if detectives:
            detective_role_id = config.detective_role_id
            if detective_role_id:
                mentions.append(f"<@&{detective_role_id}>")
        
        if traffic:
            traffic_role_id = config.traffic_role_id
            if traffic_role_id:
                mentions.append(f"<@&{traffic_role_id}>")
        
        return " ".join(mentions)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DispatchCog(bot))
