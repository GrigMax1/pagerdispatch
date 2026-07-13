from typing import Optional
import discord
from config import Config

config = Config()

class PermissionManager:
    """Manages role-based permissions for the dispatch system."""
    
    @staticmethod
    def is_supervisor(member: discord.Member) -> bool:
        """Check if member is a supervisor."""
        supervisor_roles = config.supervisor_role_ids
        return any(role.id in supervisor_roles for role in member.roles)
    
    @staticmethod
    def is_officer(member: discord.Member) -> bool:
        """Check if member is at least an officer."""
        police_role_id = config.police_role_id
        supervisor_roles = config.supervisor_role_ids
        
        has_police_role = any(role.id == police_role_id for role in member.roles)
        is_supervisor = any(role.id in supervisor_roles for role in member.roles)
        
        return has_police_role or is_supervisor
    
    @staticmethod
    def can_close_dispatch(member: discord.Member) -> bool:
        """Check if member can close dispatches."""
        return PermissionManager.is_supervisor(member)
    
    @staticmethod
    def can_create_dispatch(member: discord.Member) -> bool:
        """Check if member can create dispatches."""
        return PermissionManager.is_officer(member)
    
    @staticmethod
    def can_use_panic_alarm(member: discord.Member) -> bool:
        """Check if member can use panic alarm."""
        return PermissionManager.is_officer(member)
    
    @staticmethod
    def can_setup_console(member: discord.Member) -> bool:
        """Check if member can setup the dispatch console."""
        return member.guild_permissions.administrator
