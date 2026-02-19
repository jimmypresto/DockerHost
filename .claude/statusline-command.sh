#!/usr/bin/env bash
# p10k-style colored chevron status line for Claude Code
# Uses powerline arrow separators and colored segments

input=$(cat)

# --- Extract fields from JSON input ---
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
model=$(echo "$input" | jq -r '.model.display_name // empty')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
remaining_pct=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')
vim_mode=$(echo "$input" | jq -r '.vim.mode // empty')
agent_name=$(echo "$input" | jq -r '.agent.name // empty')
session_name=$(echo "$input" | jq -r '.session_name // empty')

# --- Shorten the directory (show only the basename of the current folder) ---
effective_cwd="${cwd:-$(pwd)}"
short_cwd=$(basename "$effective_cwd")

# --- Git branch (best-effort, skip locks) ---
git_branch=""
if git -C "${cwd:-$(pwd)}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git_branch=$(git -C "${cwd:-$(pwd)}" symbolic-ref --short HEAD 2>/dev/null \
    || git -C "${cwd:-$(pwd)}" rev-parse --short HEAD 2>/dev/null)
fi

# --- ANSI color helpers ---
# Colors: fg=38;5;N  bg=48;5;N  reset=\e[0m
reset='\e[0m'
bold='\e[1m'

# Segment colors (xterm-256 palette)
seg_vim_bg='\e[48;5;33m'      # blue
seg_vim_fg='\e[38;5;15m'      # white
seg_dir_bg='\e[48;5;238m'     # dark gray
seg_dir_fg='\e[38;5;254m'     # light gray
seg_git_bg='\e[48;5;130m'     # orange-brown
seg_git_fg='\e[38;5;15m'      # white
seg_model_bg='\e[48;5;91m'    # purple
seg_model_fg='\e[38;5;255m'   # white
seg_ctx_bg='\e[48;5;22m'      # dark green
seg_ctx_fg='\e[38;5;255m'     # white
seg_ctx_warn_bg='\e[48;5;130m' # orange
seg_ctx_warn_fg='\e[38;5;255m'
seg_ctx_crit_bg='\e[48;5;160m' # red
seg_ctx_crit_fg='\e[38;5;255m'
seg_agent_bg='\e[48;5;23m'    # teal
seg_agent_fg='\e[38;5;255m'
seg_session_bg='\e[48;5;60m'  # slate purple
seg_session_fg='\e[38;5;255m'

# Powerline chevron separators (right-facing filled arrow)
SEP=''    # solid right-pointing arrow (U+E0B0)
SEP_THIN='' # thin separator (U+E0B1)

# --- Build segment function ---
# Usage: segment <bg_color> <fg_color> <text> <next_bg_color>
# Prints the segment body, then the separator in fg=current_bg on bg=next_bg
prev_bg=""
build_segment() {
  local bg="$1"
  local fg="$2"
  local text="$3"
  local next_bg="$4"

  # Print the segment text
  printf "%b%b%b %s %b" "$bg" "$fg" "$bold" "$text" "$reset"

  # Print the powerline arrow separator
  if [ -n "$next_bg" ]; then
    # fg = current segment's bg color number, bg = next segment's bg color number
    # Extract the color number from the escape code for fg use
    local current_bg_num
    current_bg_num=$(echo "$bg" | grep -oP '48;5;\K[0-9]+')
    printf "%b%b%s%b" "$next_bg" "\e[38;5;${current_bg_num}m" "$SEP" "$reset"
  else
    # Last segment: arrow on transparent background
    local current_bg_num
    current_bg_num=$(echo "$bg" | grep -oP '48;5;\K[0-9]+')
    printf "%b%s%b" "\e[38;5;${current_bg_num}m" "$SEP" "$reset"
  fi
}

# --- Determine context color ---
ctx_bg="$seg_ctx_bg"
ctx_fg="$seg_ctx_fg"
if [ -n "$used_pct" ]; then
  if [ "$(echo "$used_pct > 85" | bc 2>/dev/null)" = "1" ] 2>/dev/null || \
     [ "${used_pct%.*}" -gt 85 ] 2>/dev/null; then
    ctx_bg="$seg_ctx_crit_bg"
    ctx_fg="$seg_ctx_crit_fg"
  elif [ "$(echo "$used_pct > 60" | bc 2>/dev/null)" = "1" ] 2>/dev/null || \
       [ "${used_pct%.*}" -gt 60 ] 2>/dev/null; then
    ctx_bg="$seg_ctx_warn_bg"
    ctx_fg="$seg_ctx_warn_fg"
  fi
fi

# --- Assemble the status line ---
line=""

# Vim mode segment (only when vim mode is active)
if [ -n "$vim_mode" ]; then
  if [ "$vim_mode" = "NORMAL" ]; then
    vim_seg_bg='\e[48;5;28m'   # green for NORMAL
    vim_label="N"
  else
    vim_seg_bg='\e[48;5;33m'   # blue for INSERT
    vim_label="I"
  fi
  line+=$(build_segment "$vim_seg_bg" "$seg_vim_fg" "$vim_mode" "$seg_dir_bg")
fi

# Agent segment (only when agent is active)
if [ -n "$agent_name" ]; then
  line+=$(build_segment "$seg_agent_bg" "$seg_agent_fg" "agent:$agent_name" "$seg_dir_bg")
fi

# Session name segment (only when session name is set)
if [ -n "$session_name" ]; then
  line+=$(build_segment "$seg_session_bg" "$seg_session_fg" "$session_name" "$seg_dir_bg")
fi

# Directory segment
line+=$(build_segment "$seg_dir_bg" "$seg_dir_fg" " $short_cwd" "$seg_git_bg")

# Git branch segment (only when in a git repo)
if [ -n "$git_branch" ]; then
  line+=$(build_segment "$seg_git_bg" "$seg_git_fg" " $git_branch" "$seg_model_bg")
  line+=$(build_segment "$seg_model_bg" "$seg_model_fg" "${model:-Claude}" "$ctx_bg")
else
  line+=$(build_segment "$seg_model_bg" "$seg_model_fg" "${model:-Claude}" "$ctx_bg")
fi

# Context window segment
if [ -n "$used_pct" ] && [ -n "$remaining_pct" ]; then
  used_int="${used_pct%.*}"
  ctx_label="ctx ${used_int}%"
else
  ctx_label="ctx --"
fi
line+=$(build_segment "$ctx_bg" "$ctx_fg" "$ctx_label" "")

printf "%b%s\n" "$reset" "$line"
