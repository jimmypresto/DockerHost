# Backup Claude Configuration

Back up Claude Code skills, MCP settings, and configuration files to a remote SMB share with intelligent merging.

## Capabilities

- Mount SMB share automatically (with guest access)
- Back up skills directory to remote location
- Intelligently merge settings.json files (MCP servers + permissions)
- Preserve existing remote configurations
- Create timestamped backups before overwriting
- Generate backup summary documentation
- Sync both local and remote configurations

## Workflow

When this skill is invoked:

1. **Get Backup Configuration**
   - Ask for SMB share path (default: `smb://jimmy-gmktec/DockerHost/claude/`)
   - Ask for backup subdirectory (default: `.claude`)
   - Optionally allow custom mount point

2. **Mount SMB Share**
   - Check if share is already mounted at `/Volumes/{share_name}/`
   - If not mounted, use `open` command to auto-mount
   - Verify mount success before proceeding

3. **Analyze Existing Remote Configuration**
   - Check if remote `.claude` directory exists
   - Read remote `settings.json` to identify what's there
   - Check for existing skills directory
   - Read `CLAUDE.md` or other documentation files

4. **Analyze Local Configuration**
   - Read local `~/.claude/settings.json`
   - List all skills in `~/.claude/skills/`
   - Identify what needs to be backed up

5. **Intelligent Merge Strategy**

   **For settings.json:**
   - If remote has `mcpServers` and local has `mcpServers`: merge unique servers
   - If remote has `permissions` and local doesn't: add permissions from remote
   - If local has `permissions` and remote doesn't: add permissions from local
   - Merge other top-level keys (model, theme, etc.)
   - Create merged version with all configurations

   **For skills:**
   - Check if skill exists remotely
   - If exists: compare modification times, ask user if should overwrite
   - If new: copy directly
   - Preserve all skill files (skill.md, skill.json, README.md, etc.)

6. **Backup Existing Remote Files**
   - Before overwriting any remote file, create backup with timestamp:
     - `settings.json` → `settings.json.backup-YYYYMMDD-HHMMSS`
   - Keep up to last 5 backups, delete older ones

7. **Perform Backup**
   - Copy merged `settings.json` to remote
   - Copy all skills from `~/.claude/skills/` to remote
   - Optionally backup other files:
     - `settings.local.json` (if exists)
     - Custom keybindings, themes, etc.

8. **Update Local Configuration**
   - Backup local settings.json before overwriting
   - Copy merged settings back to local to keep them in sync
   - Both local and remote now have identical merged configuration

9. **Generate Backup Summary**
   - Create `BACKUP-SUMMARY.md` in remote `.claude` directory
   - Include:
     - Backup timestamp
     - List of files backed up
     - Merge strategy used
     - File sizes and counts
     - Restoration instructions

10. **Report Results**
    - Show summary of what was backed up
    - Display any merge conflicts or warnings
    - Provide path to backup summary document

## Merge Algorithm Details

### Settings.json Merge

```javascript
merged = {
  // Merge MCP servers (union of both)
  mcpServers: {
    ...remote.mcpServers,
    ...local.mcpServers
  },

  // Merge permissions (union of allow/deny lists)
  permissions: {
    allow: [...new Set([
      ...(remote.permissions?.allow || []),
      ...(local.permissions?.allow || [])
    ])],
    deny: [...new Set([
      ...(remote.permissions?.deny || []),
      ...(local.permissions?.deny || [])
    ])]
  },

  // Prefer local for user preferences
  model: local.model || remote.model,
  theme: local.theme || remote.theme,

  // Include any other top-level keys
  ...remote,
  ...local
}
```

## File Preservation

**Always Preserved (Never Overwritten):**
- Remote `CLAUDE.md` (project-specific documentation)
- Remote `settings.local.json` (machine-specific overrides)
- Remote `.gitignore`, `README.md`, etc.

**Backed Up Before Overwrite:**
- Remote `settings.json` → `settings.json.backup-YYYYMMDD-HHMMSS`
- Local `settings.json` → `settings.json.backup-YYYYMMDD-HHMMSS`

**Synced (Copied in Both Directions):**
- Skills directory
- Merged settings.json

## Error Handling

- If SMB mount fails, provide troubleshooting steps
- If remote directory doesn't exist, create it
- If merge conflicts detected, show diff and ask user
- If disk space low, warn before proceeding
- If permissions denied, suggest using guest access

## Example Usage

### Basic Backup

```
User: /backup-claude-config

Claude: I'll back up your Claude configuration to the SMB share.
        SMB path? (default: smb://jimmy-gmktec/DockerHost/claude/)
User: [Enter for default]

Claude: Mounting SMB share...
        ✅ Mounted at /Volumes/DockerHost

        Analyzing configurations...
        Local: 1 skill, MCP servers (filesystem, fetch)
        Remote: permissions config, settings.local.json

        Merge strategy:
        - Combine MCP servers from local
        - Combine permissions from remote
        - Sync skills directory

        Proceed? (y/n)
User: y

Claude: Backing up settings.json (created backup)
        Copying skills/youtube-audio-download...
        Updating local settings with merge...

        ✅ Backup complete!
        Summary: /Volumes/DockerHost/claude/.claude/BACKUP-SUMMARY.md
```

### Custom SMB Path

```
User: /backup-claude-config

Claude: SMB path? (default: smb://jimmy-gmktec/DockerHost/claude/)
User: smb://myserver/backups/claude/

Claude: Mounting smb://myserver/backups/claude/...
        [continues with backup process]
```

## Backup Summary Template

The generated `BACKUP-SUMMARY.md` includes:

```markdown
# Claude Configuration Backup Summary

**Backup Date:** 2026-02-07 18:56:00
**Source:** ~/.claude/
**Destination:** /Volumes/DockerHost/claude/.claude/

## Files Backed Up

### Settings
- settings.json (merged: 1.8 KB)
  - MCP servers: filesystem, fetch
  - Permissions: 40 allow rules, 11 deny rules
  - Backup created: settings.json.backup-20260207-185600

### Skills
- youtube-audio-download/ (3 files, 12.5 KB)

## Merge Actions
- ✅ Added mcpServers from local
- ✅ Added permissions from remote
- ✅ Synced model preference

## Files Preserved
- settings.local.json (not modified)
- CLAUDE.md (not modified)

## Restoration
[Instructions to restore from backup]
```

## Directory Structure After Backup

```
SMB Share: /Volumes/DockerHost/claude/.claude/
├── settings.json                    (merged)
├── settings.json.backup-*           (timestamped backups)
├── settings.local.json              (preserved)
├── skills/
│   ├── youtube-audio-download/
│   ├── backup-claude-config/
│   └── [other skills...]
├── BACKUP-SUMMARY.md
└── [other preserved files]

Local: ~/.claude/
├── settings.json                    (merged - same as remote)
├── settings.json.backup-*           (timestamped backup)
├── skills/
│   ├── youtube-audio-download/
│   ├── backup-claude-config/
│   └── [other skills...]
└── [other local files]
```

## Advanced Options

### Selective Backup

Ask user what to backup:
- [ ] Skills directory
- [ ] Settings (with merge)
- [ ] Custom keybindings
- [ ] Themes
- [ ] MCP server configs only

### Restore Mode

If remote has newer configuration, offer to restore:
```
Claude: Remote settings are newer (modified 2 hours ago)
        Local settings modified 1 day ago

        Options:
        1. Backup local to remote (overwrite remote)
        2. Restore remote to local (overwrite local)
        3. Merge both directions

        Choice?
```

## Cleanup Old Backups

Automatically manage backup retention:
- Keep last 5 timestamped backups
- Delete backups older than 30 days
- Show list before deleting, ask confirmation

## Notes

- SMB share must allow guest write access
- Backup is incremental (only changed files)
- Merge is non-destructive (creates backups first)
- Both local and remote stay in sync
- Safe to run multiple times (idempotent)

## Requirements

- macOS (uses `open` command for SMB mounting)
- SMB share with write access
- Sufficient disk space on remote share
- Network connectivity to SMB host
