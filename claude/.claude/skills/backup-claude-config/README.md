# Backup Claude Configuration Skill

A Claude Code skill for backing up your Claude skills, MCP settings, and configuration files to a remote SMB share with intelligent merging capabilities.

## Installation

The skill is already installed at: `~/.claude/skills/backup-claude-config/`

## Features

### 🔄 Intelligent Merging
- Combines MCP servers from both local and remote configurations
- Merges permission allow/deny lists without duplicates
- Preserves user preferences (model, theme) from local config
- Non-destructive (creates timestamped backups before overwriting)

### 📁 Comprehensive Backup
- Skills directory (all your custom skills)
- Settings.json (MCP servers, permissions, preferences)
- Optional: keybindings, themes, custom configs

### 🛡️ Safe Operations
- Always creates `.backup-YYYYMMDD-HHMMSS` files before overwriting
- Preserves important remote files (CLAUDE.md, settings.local.json)
- Validates SMB mount before proceeding
- Shows merge preview before applying changes

### 📊 Documentation
- Generates `BACKUP-SUMMARY.md` with complete backup report
- Includes restoration instructions
- Lists all merged configurations and preserved files

### 🔁 Bidirectional Sync
- Backs up local to remote
- Updates local with merged config
- Keeps both locations in sync

## Requirements

- **macOS** (uses `open` command for SMB mounting)
- **SMB share** with guest write access
- **Network connectivity** to SMB host
- **Disk space** on remote share

## Usage

### Basic Usage

```
/backup-claude-config
```

Claude will interactively guide you through:
1. SMB share path (with default suggestion)
2. Mount verification
3. Configuration analysis
4. Merge preview
5. Backup execution
6. Summary report

### Example Session

```
User: /backup-claude-config

Claude: I'll back up your Claude configuration to the SMB share.

        SMB share path?
        (default: smb://jimmy-gmktec/DockerHost/claude/)
User: [Enter]

Claude: ✅ Mounted at /Volumes/DockerHost

        📊 Configuration Analysis:

        Local (~/.claude/):
        - 2 skills: youtube-audio-download, backup-claude-config
        - MCP servers: filesystem, fetch
        - Model: sonnet

        Remote (/Volumes/DockerHost/claude/.claude/):
        - 0 skills (directory doesn't exist)
        - Permissions: 40 allow rules, 11 deny rules
        - settings.local.json exists

        🔄 Merge Strategy:
        ✓ Add MCP servers from local
        ✓ Add permissions from remote
        ✓ Copy all skills (2 new)
        ✓ Sync model preference

        Proceed with backup? (y/n)
User: y

Claude: 🔄 Creating backup...
        ✓ Backed up remote settings.json → .backup-20260207-190000
        ✓ Backed up local settings.json → .backup-20260207-190000
        ✓ Copied merged settings.json to remote
        ✓ Updated local settings.json with merge
        ✓ Copied skills/youtube-audio-download (3 files)
        ✓ Copied skills/backup-claude-config (3 files)
        ✓ Generated BACKUP-SUMMARY.md

        ✅ Backup complete!

        📄 Summary: /Volumes/DockerHost/claude/.claude/BACKUP-SUMMARY.md

        Files backed up:
        - settings.json (merged, 1.8 KB)
        - 2 skills (6 files, 25.1 KB)

        Both local and remote are now in sync.
```

## Configuration

### Default SMB Path

The skill defaults to: `smb://jimmy-gmktec/DockerHost/claude/`

You can customize this during invocation or modify the default in the skill.

### Default Backup Directory

Remote backups go to: `.claude/` subdirectory within the SMB share

Example full path: `/Volumes/DockerHost/claude/.claude/`

## How Merging Works

### Settings.json Merge Algorithm

```
Merged Configuration = {
  // MCP Servers: Union of both
  mcpServers: {
    filesystem: (from local),
    fetch: (from local),
    ...any from remote
  },

  // Permissions: Union of allow/deny lists
  permissions: {
    allow: [unique items from both local and remote],
    deny: [unique items from both local and remote]
  },

  // User Preferences: Local takes precedence
  model: (from local) || (from remote),
  theme: (from local) || (from remote),

  // Other keys: Local overrides remote
  ...other settings
}
```

### Skills Merge

- New skills → Copied directly
- Existing skills → Compare timestamps, ask user
- Deleted skills → Preserved on remote (safe operation)

## Files Always Preserved

These files are **never overwritten** (always preserved):

- `CLAUDE.md` - Project-specific documentation
- `settings.local.json` - Machine-specific overrides
- `.gitignore`, `README.md` - Project files

## Backup Retention

The skill automatically manages backups:
- **Keeps:** Last 5 timestamped backups per file
- **Deletes:** Backups older than 30 days
- **Asks:** Confirmation before deleting old backups

## Troubleshooting

### SMB Mount Fails

```
Error: Could not mount smb://jimmy-gmktec/DockerHost/claude/
```

**Solutions:**
1. Check network connectivity: `ping jimmy-gmktec`
2. Verify SMB share exists: `smbclient -L jimmy-gmktec -U guest`
3. Try manual mount: `open smb://jimmy-gmktec/DockerHost/claude/`
4. Check if already mounted: `ls /Volumes/`

### Permission Denied

```
Error: Permission denied writing to /Volumes/DockerHost/claude/.claude/
```

**Solutions:**
1. Verify guest write access is enabled on SMB share
2. Check remote directory permissions
3. Try unmounting and remounting: `diskutil unmount /Volumes/DockerHost`

### Merge Conflicts

If the skill detects conflicting configurations, it will:
1. Show a diff of the differences
2. Ask which version to prefer
3. Allow manual merge

## Backup Structure

After running the skill:

```
Remote: /Volumes/DockerHost/claude/.claude/
├── settings.json                           (merged)
├── settings.json.backup-20260207-190000    (before merge)
├── settings.json.backup-20260207-180000    (older backup)
├── settings.local.json                     (preserved)
├── skills/
│   ├── youtube-audio-download/
│   │   ├── skill.md
│   │   ├── skill.json
│   │   └── README.md
│   └── backup-claude-config/
│       ├── skill.md
│       ├── skill.json
│       └── README.md
├── BACKUP-SUMMARY.md                       (generated report)
└── CLAUDE.md                               (preserved)

Local: ~/.claude/
├── settings.json                           (merged - same as remote)
├── settings.json.backup-20260207-190000    (before merge)
├── skills/
│   ├── youtube-audio-download/
│   └── backup-claude-config/
└── [other local directories not backed up]
```

## What Gets Backed Up

### ✅ Always Backed Up
- `settings.json` (merged)
- `skills/` directory (all skills)

### 🔲 Optional (Can Enable)
- Custom keybindings
- Custom themes
- Plugin configurations

### ❌ Never Backed Up (Ephemeral)
- `cache/`
- `debug/`
- `history.jsonl`
- `projects/` (too large, project-specific)
- `downloads/`
- `session-env/`
- `todos/`

## Restoration

To restore from a backup:

### Restore Everything

```bash
# Copy skills back
cp -r /Volumes/DockerHost/claude/.claude/skills ~/.claude/

# Copy merged settings
cp /Volumes/DockerHost/claude/.claude/settings.json ~/.claude/
```

### Restore from Specific Backup

```bash
# List available backups
ls -lt /Volumes/DockerHost/claude/.claude/settings.json.backup-*

# Restore specific backup
cp /Volumes/DockerHost/claude/.claude/settings.json.backup-20260207-190000 \
   ~/.claude/settings.json
```

## Advanced Usage

### Selective Backup

When prompted, you can choose what to backup:
- Skills only
- Settings only
- Both (default)

### Dry Run Mode

To preview what would be backed up without actually doing it:
```
User: /backup-claude-config --dry-run
```

### Restore Mode

To restore from remote to local (reverse direction):
```
User: /backup-claude-config --restore
```

## Scheduling Automatic Backups

To run backups automatically (requires cron or launchd setup):

```bash
# Add to crontab (example: daily at 2 AM)
0 2 * * * /usr/local/bin/claude /backup-claude-config --auto
```

## Version History

**v1.0.0** - Initial release
- Intelligent settings.json merging
- Skills directory backup
- Timestamped backups
- Backup summary generation
- Bidirectional sync

## Support

For issues or questions about this skill:
1. Check `/Volumes/DockerHost/claude/.claude/BACKUP-SUMMARY.md` for last backup status
2. Review timestamped backup files
3. Verify SMB mount and permissions

## Related Skills

- **youtube-audio-download** - Download and enhance YouTube audio

## Notes

- Backup is **idempotent** (safe to run multiple times)
- Merge operation is **non-destructive** (always creates backups)
- Both local and remote stay **in sync** after backup
- SMB share must support **guest write access**
- Backup summary includes **restoration instructions**

## License

Created for personal use with Claude Code.
