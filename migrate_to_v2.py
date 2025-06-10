#!/usr/bin/env python3
"""
Migration Script - From Clusterfuck to Clean Architecture

This script helps migrate from the old broken system to the new event-driven architecture.
Run this AFTER the new system is up and running.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_legion_backend.core.dependencies import get_service_container as get_old_container
from gemini_legion_backend.core.dependencies_v2 import get_service_container_v2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiLegionMigrator:
    """Migrates data from old broken system to clean V2 architecture"""
    
    def __init__(self):
        self.old_container = None
        self.new_container = None
        self.migration_stats = {
            "channels": {"total": 0, "migrated": 0, "failed": 0},
            "minions": {"total": 0, "migrated": 0, "failed": 0},
            "messages": {"total": 0, "migrated": 0, "failed": 0}
        }
    
    async def initialize(self):
        """Initialize both old and new systems"""
        logger.info("Initializing migration...")
        
        # Initialize old system
        from gemini_legion_backend.core.dependencies import initialize_services
        await initialize_services()
        self.old_container = get_old_container()
        
        # Initialize new system
        from gemini_legion_backend.core.dependencies_v2 import initialize_services_v2
        await initialize_services_v2()
        self.new_container = get_service_container_v2()
        
        logger.info("Both systems initialized")
    
    async def migrate_channels(self):
        """Migrate channels from old to new system"""
        logger.info("\n=== MIGRATING CHANNELS ===")
        
        old_channels = await self.old_container.channel_service.list_channels()
        self.migration_stats["channels"]["total"] = len(old_channels)
        
        for channel in old_channels:
            try:
                # Skip if it's a default channel (already created)
                if channel["channel_id"] in ["general", "announcements", "task_coordination"]:
                    logger.info(f"Skipping default channel: {channel['name']}")
                    continue
                
                # Create in new system
                await self.new_container.channel_service.create_channel(
                    channel_id=channel["channel_id"],
                    name=channel["name"],
                    channel_type=channel.get("channel_type", "public"),
                    description=channel.get("description", ""),
                    creator=channel.get("created_by", "migrated")
                )
                
                # Add members
                for member in channel.get("members", []):
                    member_id = member["member_id"] if isinstance(member, dict) else member
                    try:
                        await self.new_container.channel_service.add_member(
                            channel["channel_id"],
                            member_id,
                            role="member",
                            added_by="migration"
                        )
                    except Exception as e:
                        logger.warning(f"Could not add member {member_id}: {e}")
                
                self.migration_stats["channels"]["migrated"] += 1
                logger.info(f"✓ Migrated channel: {channel['name']}")
                
            except Exception as e:
                self.migration_stats["channels"]["failed"] += 1
                logger.error(f"✗ Failed to migrate channel {channel['name']}: {e}")
    
    async def migrate_minions(self):
        """Migrate minions from old to new system"""
        logger.info("\n=== MIGRATING MINIONS ===")
        
        old_minions = await self.old_container.minion_service.list_minions()
        self.migration_stats["minions"]["total"] = len(old_minions)
        
        for minion in old_minions:
            try:
                # Extract persona data
                persona = minion.get("persona", {})
                
                # Create in new system
                await self.new_container.minion_service.spawn_minion(
                    minion_id=minion["minion_id"],
                    name=minion["name"],
                    base_personality=persona.get("base_personality", "Migrated minion"),
                    personality_traits=persona.get("personality_traits", []),
                    quirks=persona.get("quirks", []),
                    response_length=persona.get("response_length", "medium"),
                    catchphrases=persona.get("catchphrases", []),
                    expertise_areas=persona.get("expertise_areas", []),
                    model_name=persona.get("model_name", "gemini-2.0-flash-exp")
                )
                
                self.migration_stats["minions"]["migrated"] += 1
                logger.info(f"✓ Migrated minion: {minion['name']}")
                
            except Exception as e:
                self.migration_stats["minions"]["failed"] += 1
                logger.error(f"✗ Failed to migrate minion {minion['name']}: {e}")
    
    async def migrate_recent_messages(self, limit: int = 100):
        """Migrate recent messages - WARNING: This might cause duplicates"""
        logger.info(f"\n=== MIGRATING RECENT MESSAGES (limit: {limit}) ===")
        logger.warning("WARNING: Message migration might create duplicates if messages were sent during migration")
        
        # Get channels
        channels = await self.new_container.channel_service.list_channels()
        
        for channel in channels:
            channel_id = channel["channel_id"]
            
            try:
                # Get messages from old system
                old_messages = await self.old_container.channel_service.get_messages(
                    channel_id,
                    limit=limit
                )
                
                self.migration_stats["messages"]["total"] += len(old_messages)
                
                # Sort by timestamp (oldest first)
                old_messages.sort(key=lambda m: m.get("timestamp", ""))
                
                # Migrate each message
                for msg in old_messages:
                    try:
                        # Skip if it's very recent (might be duplicate)
                        if "timestamp" in msg:
                            msg_time = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
                            if (datetime.now() - msg_time).total_seconds() < 60:
                                logger.debug(f"Skipping recent message from {msg['sender_id']}")
                                continue
                        
                        # Send through new system
                        await self.new_container.channel_service.send_message(
                            channel_id=channel_id,
                            sender_id=msg.get("sender_id", "unknown"),
                            content=msg.get("content", ""),
                            message_type=msg.get("message_type", "chat")
                        )
                        
                        self.migration_stats["messages"]["migrated"] += 1
                        
                    except Exception as e:
                        self.migration_stats["messages"]["failed"] += 1
                        logger.debug(f"Failed to migrate message: {e}")
                
                logger.info(f"✓ Migrated {self.migration_stats['messages']['migrated']} messages from {channel['name']}")
                
            except Exception as e:
                logger.error(f"✗ Failed to migrate messages from {channel['name']}: {e}")
    
    async def run_migration(self, migrate_messages: bool = False):
        """Run the complete migration"""
        logger.info("🚀 STARTING GEMINI LEGION MIGRATION")
        logger.info("From: Broken duplicate-message clusterfuck")
        logger.info("To: Clean event-driven architecture")
        logger.info("="*50)
        
        start_time = datetime.now()
        
        try:
            # Initialize systems
            await self.initialize()
            
            # Migrate data
            await self.migrate_channels()
            await self.migrate_minions()
            
            if migrate_messages:
                await self.migrate_recent_messages()
            
            # Print summary
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info("\n" + "="*50)
            logger.info("✅ MIGRATION COMPLETE")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info("\nResults:")
            
            for entity, stats in self.migration_stats.items():
                logger.info(f"\n{entity.upper()}:")
                logger.info(f"  Total: {stats['total']}")
                logger.info(f"  Migrated: {stats['migrated']}")
                logger.info(f"  Failed: {stats['failed']}")
            
            logger.info("\n🎉 Your Gemini Legion is now running on clean architecture!")
            logger.info("No more duplicates, no more custom bullshit, just pure ADK patterns")
            
        except Exception as e:
            logger.error(f"\n❌ MIGRATION FAILED: {e}")
            raise
        finally:
            # Cleanup
            if self.old_container:
                from gemini_legion_backend.core.dependencies import shutdown_services
                await shutdown_services()
            
            if self.new_container:
                from gemini_legion_backend.core.dependencies_v2 import shutdown_services_v2
                await shutdown_services_v2()


async def main():
    """Main migration entry point"""
    print("\n🔄 GEMINI LEGION MIGRATION TOOL")
    print("This will migrate your data from the old broken system to the new clean architecture")
    print("\nWARNING: Make sure both systems are not actively being used during migration!")
    
    # Ask about message migration
    migrate_messages = input("\nMigrate recent messages? This might cause duplicates (y/N): ").lower() == 'y'
    
    if input("\nProceed with migration? (y/N): ").lower() != 'y':
        print("Migration cancelled")
        return
    
    # Run migration
    migrator = GeminiLegionMigrator()
    await migrator.run_migration(migrate_messages=migrate_messages)


if __name__ == "__main__":
    asyncio.run(main())
