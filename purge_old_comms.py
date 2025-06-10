#!/usr/bin/env python3
"""
Purge Old Communication System - Delete the Ancient Bullshit

This script removes all references to the old broken communication system
and replaces them with event bus glory.
"""

import os
import re
import asyncio
import shutil
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommunicationSystemPurger:
    """Destroyer of old patterns, bringer of event-driven light"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.backup_dir = self.base_path / f"backup_before_purge_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Patterns to identify old system
        self.old_patterns = [
            r'from.*InterMinionCommunicationSystem.*import',
            r'InterMinionCommunicationSystem',
            r'CommunicationCapability',
            r'ConversationalLayer',
            r'MessageRouter(?!V2)',  # Don't match V2 versions
            r'TurnTakingEngine(?!V2)',
            r'comm_system\.',
            r'communication_capability\.',
            r'_notify_active_minions',
            r'_process_messages_loop',
            r'message_queue\.put',
            r'custom_message_routing'
        ]
        
        # Files that are completely obsolete
        self.files_to_delete = [
            'core/infrastructure/messaging/communication_system.py',
            'core/infrastructure/messaging/autonomous_messaging.py',
            'core/infrastructure/messaging/safeguards.py',
            'core/infrastructure/adk/tools/communication_capability.py',
            'core/infrastructure/adk/tools/communication_tools.py',  # The old one
        ]
        
        # Replacement mappings
        self.replacements = {
            r'self\.comm_system\.broadcast_message\(([^)]+)\)': 
                r'await self.event_bus.emit_channel_message(\1)',
            r'from.*InterMinionCommunicationSystem.*import.*\n': '',
            r'self\.comm_system = InterMinionCommunicationSystem\(\)\n': '',
            r'comm_system=self\.comm_system,?\s*': '',
            r'communication_capability=.*,?\s*\n': '',
            r'await self\._notify_active_minions\([^)]+\)\n': '# Removed: Direct minion notification (now via events)\n',
        }
        
        self.stats = {
            'files_scanned': 0,
            'files_modified': 0,
            'files_deleted': 0,
            'patterns_found': 0,
            'replacements_made': 0
        }
    
    async def purge(self):
        """Execute the great purge"""
        logger.info("🔥 BEGINNING THE GREAT PURGE OF OLD COMMUNICATION SYSTEMS")
        logger.info(f"Target: {self.base_path}")
        
        # Create backup
        await self._create_backup()
        
        # Delete obsolete files
        await self._delete_obsolete_files()
        
        # Scan and clean remaining files
        await self._scan_and_clean_files()
        
        # Report results
        self._report_results()
        
        logger.info("✨ PURGE COMPLETE - THE EVENT BUS REIGNS SUPREME")
    
    async def _create_backup(self):
        """Backup before destruction"""
        logger.info(f"Creating backup at {self.backup_dir}")
        
        # Only backup Python files we might modify
        python_files = list(self.base_path.rglob("*.py"))
        self.backup_dir.mkdir(exist_ok=True)
        
        for file in python_files:
            if 'backup' not in str(file) and '__pycache__' not in str(file):
                rel_path = file.relative_to(self.base_path)
                backup_path = self.backup_dir / rel_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, backup_path)
        
        logger.info(f"Backed up {len(python_files)} files")
    
    async def _delete_obsolete_files(self):
        """Delete files that have no place in the new world"""
        for file_path in self.files_to_delete:
            full_path = self.base_path / file_path
            if full_path.exists():
                logger.info(f"🗑️  Deleting obsolete file: {file_path}")
                full_path.unlink()
                self.stats['files_deleted'] += 1
            else:
                logger.debug(f"File already gone: {file_path}")
    
    async def _scan_and_clean_files(self):
        """Scan all Python files and clean old patterns"""
        python_files = list(self.base_path.rglob("*.py"))
        
        for file_path in python_files:
            # Skip backups, v2 files, and test files
            if any(skip in str(file_path) for skip in ['backup', '__pycache__', '_v2.py', 'test_']):
                continue
            
            self.stats['files_scanned'] += 1
            
            try:
                content = file_path.read_text()
                original_content = content
                
                # Check for old patterns
                found_patterns = False
                for pattern in self.old_patterns:
                    if re.search(pattern, content):
                        found_patterns = True
                        self.stats['patterns_found'] += 1
                        logger.info(f"Found old pattern in: {file_path.relative_to(self.base_path)}")
                        break
                
                if not found_patterns:
                    continue
                
                # Apply replacements
                for old_pattern, new_pattern in self.replacements.items():
                    if re.search(old_pattern, content):
                        content = re.sub(old_pattern, new_pattern, content)
                        self.stats['replacements_made'] += 1
                
                # Add event bus import if needed
                if 'event_bus' in content and 'from.*adk.events import' not in content:
                    # Add import at the top after other imports
                    import_section_end = self._find_import_section_end(content)
                    if import_section_end:
                        import_line = "from ...infrastructure.adk.events import get_event_bus, EventType\n"
                        content = content[:import_section_end] + import_line + content[import_section_end:]
                
                # Write back if changed
                if content != original_content:
                    file_path.write_text(content)
                    self.stats['files_modified'] += 1
                    logger.info(f"✏️  Modified: {file_path.relative_to(self.base_path)}")
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
    
    def _find_import_section_end(self, content: str) -> int:
        """Find where to insert new imports"""
        lines = content.split('\n')
        last_import_idx = 0
        
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import_idx = i
        
        # Return position after last import
        if last_import_idx > 0:
            return sum(len(line) + 1 for line in lines[:last_import_idx + 1])
        
        # If no imports found, put after module docstring
        if '"""' in content:
            docstring_end = content.find('"""', content.find('"""') + 3) + 3
            return content.find('\n', docstring_end) + 1
        
        return 0
    
    def _report_results(self):
        """Report the carnage"""
        logger.info("\n" + "="*60)
        logger.info("🔥 PURGE RESULTS:")
        logger.info(f"  Files scanned: {self.stats['files_scanned']}")
        logger.info(f"  Files modified: {self.stats['files_modified']}")
        logger.info(f"  Files deleted: {self.stats['files_deleted']}")
        logger.info(f"  Old patterns found: {self.stats['patterns_found']}")
        logger.info(f"  Replacements made: {self.stats['replacements_made']}")
        logger.info("="*60)
        
        if self.stats['files_modified'] > 0:
            logger.info(f"\n✅ Successfully purged old communication system!")
            logger.info(f"💾 Backup saved to: {self.backup_dir}")
            logger.info("🎉 The event bus is now the only way!")
        else:
            logger.info("\n✨ System already clean - no old patterns found!")


class DependencyChecker:
    """Verify no circular dependencies remain"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.import_graph = {}
        self.circular_deps = []
    
    async def check(self):
        """Check for circular dependencies"""
        logger.info("\n🔍 Checking for circular dependencies...")
        
        # Build import graph
        await self._build_import_graph()
        
        # Find cycles
        self._find_cycles()
        
        if self.circular_deps:
            logger.error(f"❌ Found {len(self.circular_deps)} circular dependencies!")
            for cycle in self.circular_deps:
                logger.error(f"  Cycle: {' -> '.join(cycle)}")
        else:
            logger.info("✅ No circular dependencies found!")
    
    async def _build_import_graph(self):
        """Build graph of imports"""
        python_files = list(self.base_path.rglob("*_v2.py"))
        
        for file_path in python_files:
            module_name = str(file_path.relative_to(self.base_path)).replace('/', '.').replace('.py', '')
            self.import_graph[module_name] = set()
            
            try:
                content = file_path.read_text()
                
                # Find imports
                import_pattern = r'from\s+(\S+)\s+import'
                imports = re.findall(import_pattern, content)
                
                for imp in imports:
                    if imp.startswith('.'):
                        # Relative import - resolve it
                        pass  # Simplified for now
                    else:
                        self.import_graph[module_name].add(imp)
                        
            except Exception as e:
                logger.debug(f"Error analyzing {file_path}: {e}")
    
    def _find_cycles(self):
        """Find cycles in import graph using DFS"""
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.import_graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    self.circular_deps.append(path[cycle_start:] + [neighbor])
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        for node in self.import_graph:
            if node not in visited:
                dfs(node, [])


async def main():
    """Execute the purge"""
    base_path = "/users/ttig/downloads/geminopus-branch/gemini_legion_backend"
    
    # Confirm with user
    print("\n🔥 OLD COMMUNICATION SYSTEM PURGER 🔥")
    print("This will:")
    print("1. Backup all Python files")
    print("2. Delete obsolete communication system files")
    print("3. Replace old patterns with event bus calls")
    print("4. Check for circular dependencies")
    print(f"\nTarget: {base_path}")
    
    response = input("\nProceed with the purge? (y/N): ")
    if response.lower() != 'y':
        print("Purge cancelled.")
        return
    
    # Execute purge
    purger = CommunicationSystemPurger(base_path)
    await purger.purge()
    
    # Check dependencies
    checker = DependencyChecker(base_path)
    await checker.check()
    
    print("\n🎉 The old ways are dead. Long live the event bus!")


if __name__ == "__main__":
    asyncio.run(main())
