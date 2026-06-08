#!/data/data/com.termux/files/usr/bin/bash
# Note20 Termux bootstrap — runs non-interactively
set -e

echo "=== Phase 1: Update repos ==="
yes | pkg update
yes | pkg upgrade

echo "=== Phase 2: Core packages ==="
pkg install -y git python nodejs openssh tmux wget curl jq nano

echo "=== Phase 3: Monitoring + search ==="
pkg install -y btop ripgrep fd tree bat

echo "=== Phase 4: Build tools ==="
pkg install -y clang make cmake

echo "=== Phase 5: API + containers ==="
pkg install -y termux-api proot-distro

echo "=== Phase 6: Audio pipeline ==="
pkg install -y sox ffmpeg

echo "=== Phase 7: Storage access ==="
termux-setup-storage <<< "y" || true

echo "=== Phase 8: Install Ubuntu proot ==="
proot-distro install ubuntu

echo "=== Phase 9: Dotfiles ==="
cat >> ~/.bashrc << 'RCEOF'
export PATH="$HOME/.local/bin:$PATH"
[ -f ~/.bash_aliases ] && . ~/.bash_aliases
RCEOF

cat > ~/.bash_aliases << 'ALEOF'
alias hermv='cd ~/storage/shared/Documents/Hermes_Phone_Vault && ls'
alias qr='cd ~/storage/audiobooks/QuickRef_Vault && ls'
alias kali='proot-distro login kali'
alias ubuntu='proot-distro login ubuntu'
alias dash='tmux new-session -d -s dash "btop" \; split-window -h \; attach'
alias lock='termux-wake-lock'
alias unlock='termux-wake-unlock'
ALEOF

cat > ~/.tmux.conf << 'TMEOF'
set -g mouse on
set -g history-limit 10000
set -g base-index 1
setw -g pane-base-index 1
set -g status-style 'bg=#333333 fg=#aaaaaa'
TMEOF

echo "=== Phase 10: Ubuntu proot setup ==="
proot-distro login ubuntu -- bash -c "
  echo 'nameserver 8.8.8.8' > /etc/resolv.conf
  apt update -y
  apt upgrade -y
  apt install -y python3-pip python3-venv build-essential git curl wget cmake
  echo 'Ubuntu proot ready'
"

echo "=== Phase 11: Verify ==="
echo "Packages: $(dpkg -l | grep '^ii' | wc -l)"
echo "proot-distro list:"
proot-distro list
echo ""
echo "=== BOOTSTRAP COMPLETE ==="
echo "Run 'termux-setup-storage' manually if ~/storage is empty"
echo "Then: bash /sdcard/setup-models.sh from proot Ubuntu for Gemma/whisper"