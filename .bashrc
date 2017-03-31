### ~/.bashrc

## If not running interactively, don't do anything
[ -z "$PS1" ] && return

## Common bash setup

# Report status of terminated background jobs immediately
set -b

# Auto-update LINES and COLUMNS
shopt -s checkwinsize

# Append to history file, ignoring spaces and duplicates, expand history, useful timestamp format
shopt -s histappend
HISTCONTROL="erasedups:ignoreboth"
HISTSIZE=1000
HISTFILESIZE=2000
HISTTIMEFORMAT='%F %T '

# Don't record some commands
export HISTIGNORE="&:[ ]*:exit:ls:bg:fg:history:clear"

# Save multi-line commands as one command
shopt -s cmdhist

# Match filenames in case-insensitive fashion
shopt -s nocaseglob

# Don't search PATH for possible completions when completion is attempted on
# an empty command line
shopt -qs no_empty_cmd_completion

# Allows space to complete and expand !$
bind Space:magic-space

# Perform file completion in a case insensitive fashion
bind "set completion-ignore-case on"

# Display matches for ambiguous patterns at first tab press
bind "set show-all-if-ambiguous on"

## Enable 256-color terminal support
if [ "$TERM" = "xterm" ] ; then
    if [ -z "$COLORTERM" ] ; then
        if [ -z "$XTERM_VERSION" ] ; then
            echo "Warning: Terminal is wrongly calling itself 'xterm'."
        else
            TERM="xterm-256color"
        fi
    else
        case "$COLORTERM" in
            gnome-terminal|mate-terminal)
                TERM="xterm-256color"
                ;;
            *)
                echo "Warning: Unrecognized COLORTERM: $COLORTERM"
                ;;
        esac
    fi
fi

## Other environment setup
[ -d /usr/local/go ] && export GOROOT=/usr/local/go
[ -d ~/work/go ] && export GOPATH=~/work/go

## set orion build/test options
#export GINKGO_FOCUS=data make aat
#export SUITE_FOCUS=local
#export SUITE_FOCUS=dotcom

## Other look and feel

# Colorized prompt
if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[01;34m\] \w \[\033[00m\]\$ '
else
    PS1="${debian_chroot:+($debian_chroot)}\u@\h \w \$ "
fi

# Set window title
if [ $TERM != "emacs" -a $TERM != "eterm-color" -a $TERM != "dumb" ];
then
    PROMPT_COMMAND='echo -ne "\033]0;${USER}@${HOSTNAME%%.*}:${PWD/#$HOME/~}\007"'
fi

# Load directory colors
if [ -x /usr/bin/dircolors ]; then
    eval "$(dircolors -b)"
fi

# Use color in grep output
export GREP_OPTIONS='--color=auto'

# Make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"
export PAGER=less
export MANPAGER=$PAGER

# functions and environment settings to handle python virtual environments
#export PIP_REQUIRE_VIRTUALENV=true

# allow install/update of global packages
gpip() {
    PIP_REQUIRE_VIRTUALENV="" pip "$@"
}

# add basic perforce setup options
export P4CONFIG=.p4env
# perforce.spirentcom.com:1666
#export P4PORT=10.180.22.2:1666
# perforce-rtp.spirentcom.com:1999
export P4PORT=10.28.50.70:1999

[ -x /bin/stty ] && {
    # Turn off stop (^S) control character
    stty stop undef

    # Don't echo control characters
    stty -echoctl
}

## Aliases - OS specific
case "$OSTYPE" in
    linux*)
        alias l='/bin/ls -alF --color=auto'
        alias l.='/bin/ls -dF .* --color=auto'
        alias ll='/bin/ls -lF --color=auto'
        alias ls='ls --color=auto'
        # a few admin aliases to see current MOTD and the packages that are outdated and could be updated
        alias pkg-outdated='/usr/lib/update-notifier/apt-check -p 2>&1 | sort'
        if [ -d /etc/update-motd.d ] && [ -f /bin/run-parts ]; then
            alias pmotd='test -d /etc/update-motd.d && /bin/run-parts /etc/update-motd.d'
        else
            alias pmotd='test -f /etc/motd && cat /etc/motd'
        fi
        alias vncsetup="vncserver -geometry 1870x980 -alwaysshared :`id -u`"
        alias vncstop="vncserver -kill :`id -u`"
        ;;

    darwin*)
        alias-app() {
            if [ $# -gt 0 ]; then
                appPath="$1"
                if [ -f "$appPath" -a -x "$appPath" ]; then
                    if [ $# -gt 1 ]; then
                        aliasName=$2
                    else
                        aliasName=`basename "$appPath"`
                    fi
                    alias $aliasName="`echo $appPath | sed -e 's/ /\\\\ /g'`"
                else
                    echo bad appPath $appPath
                fi
            else
                echo not enough args
            fi
        }
        backup-mac() {
            baseBackupDir=/mnt/backups/lwheat
            if [ -d $baseBackupDir ]; then
                dotList=".spacemacs .emacs.d .bashrc .gem .gitconfig .gitignore_global .gitmodules .hgrc .nmap .profile .pylintrc"
                dirList="Documents Downloads bin tmp work"
                fileList=""
                for i in $dotList $fileList $dirList
                do
                    echo "backing up $i"
                    rsync -az /Users/lwheat/$i $baseBackupDir
                done
            else
                echo "$baseBackupDir not present. try mounting it?"
            fi
        }
        brew-depend() {
            brew list | while read cask; do echo -e -n "\033[1;34m$cask ->\033[0m"; brew deps $cask | awk '{printf(" %s ", $0)}'; echo ""; done
        }
        sync-master() {
            echo "entering "${FUNCNAME}
            echo "num "$#
            echo "args "$@
            declare arg1=$1
            echo "arg1 "$arg1
        }
        #
        # update colors used for ls command. default is "exfxcxdxbxegedabagacad"
        # The color designators are as follows:
        # a     black
        # b     red
        # c     green
        # d     brown
        # e     blue
        # f     magenta
        # g     cyan
        # h     light grey
        # A     bold black, usually shows up as dark grey
        # B     bold red
        # C     bold green
        # D     bold brown, usually shows up as yellow
        # E     bold blue
        # F     bold magenta
        # G     bold cyan
        # H     bold light grey; looks like bright white
        # x     default foreground or background
        #
        export LSCOLORS="Exfxcxdxbxegedabagacad"
        alias l='/bin/ls -alFG'
        alias l.='/bin/ls -dFG .*'
        alias ll='/bin/ls -lFG'
        alias ls='ls -G'
        alias lsusb="ioreg -p IOUSB -w 0"
        #alias mount-bkup='sudo bash -c "mkdir -p /Volumes/backups && sudo mount_afp afp://@rtp-engnas01.ad.spirentcom.com/backups /Volumes/backups"'
        #alias umount-bkup="diskutil umount /Volumes/backups"
        alias mount-bkup='sudo bash -c "mkdir -p /mnt/backups && sudo mount -t nfs rtp-engnas01.ad.spirentcom.com:/c/backups /mnt/backups"'
        alias umount-bkup="sudo umount /mnt/backups"
        alias unquarantine='xattr -d com.apple.quarantine'
        alias-app "/Applications/VMware Fusion.app/Contents/Library/VMware OVF Tool/ovftool"
        alias-app "/Applications/p4merge.app/Contents/MacOS/p4merge"
        alias-app "/Applications/p4v.app/Contents/MacOS/p4v"
        # if docker-machine is installed, add alias to configure/remove environment so we can talk to it
        if [ ! -z "`which docker-machine`" ]; then
            alias docker-setenv='eval "$(docker-machine env)"'
            alias docker-rmenv='unset `printenv | grep ^DOCKER | cut -f1 -d=`'
        fi
        # Spirent-specific stuff
        if [ -d ~/OneDrive\ -\ Spirent\ Communications ]; then
            alias fix-broken-links='for i in `cat broken-links`; do ln -sf `readlink $i | sed "s,/home/lwheat/work/intqemu,/Users/lwheat/work/integration,"` $i; done'
        fi

        ;;
esac

## Aliases - common
alias checkforks='for i in `ls -1F | grep /`; do if [ -d $i/.git ]; then  cd $i; if [ `git rv | grep ^upstream | wc -l | tr -d " "` -gt 0 ]; then echo $i is a fork; echo "git pull upstream master && git push origin master"; else echo $i is not a fork; echo git pull origin master; fi; cd ..;else echo $i not a git repo; fi; done'
alias cf2='for i in `ls -1F | grep /` ; do for j in `find $i -name .git`; do pushd `dirname $j` > /dev/null; pwd; if [ `git rv | grep ^upstream | wc -l | tr -d " "` -gt 0 ]; then echo $i is a fork; echo "git pull upstream master && git push origin master"; else echo $i is not a fork; echo git pull origin master; fi; popd > /dev/null; done; done'
alias cf3='for i in `ls -1F | grep /` ; do for j in `find $i -name .git`; do pushd `dirname $j` > /dev/null; k=`git branch | grep \* | cut -d" " -f2`; if [ `git rv | grep ^upstream | wc -l | tr -d " "` -gt 0 ]; then echo `pwd` is a fork; echo "git pull upstream $k && git push origin $k"; else echo `pwd` is not a fork; echo git pull origin $k; fi; popd > /dev/null; done; done'
alias checkmaster='for i in `ls -1F | grep /` ; do for j in `find $i -name .git`; do pushd `dirname $j` > /dev/null; [ "`git symbolic-ref --short HEAD`" != "master" ] && echo `pwd`" on branch "`git symbolic-ref --short HEAD`; popd > /dev/null; done; done'
#alias emacs='emacs -bg black -fg white'
alias lsd='/bin/ls -F | grep / | sed -e "s,/$,,"'
alias lsdd='/bin/ls -Fd .[A-Z][a-z]* * | grep / | sed -e "s,/$,,"'
alias llsd='/bin/ls -l | grep ^d'
alias sha1='openssl dgst -sha1'
alias sha256='openssl dgst -sha256'
alias ssh-nosave='ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
alias scp-nosave='scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
alias md5='openssl dgst -md5'
alias syncforks='for i in `ls -1F | grep /`; do if [ -d $i/.git ]; then  cd $i; if [ `git rv | grep ^upstream | wc -l | tr -d " "` -gt 0 ]; then echo $i is a fork; git pull upstream master && git push origin master; else echo $i is not a fork; git pull origin master; fi; cd ..;else echo $i not a git repo; fi; done'
alias sf2='for i in `ls -1F | grep /` ; do for j in `find $i -name .git`; do pushd `dirname $j` > /dev/null; pwd; if [ `git rv | grep ^upstream | wc -l | tr -d " "` -gt 0 ]; then echo $i is a fork; git pull upstream master && git push origin master; else echo $i is not a fork; git pull origin master; fi; popd > /dev/null; done; done'
[ -f ~/bin/Table.jar -a -f ~/bin/TABLE.properties ] && alias table-build='java -jar ~/bin/Table.jar'
alias unquarantine='xattr -d com.apple.quarantine'
alias uuidhash='uuidgen | tr [A-Z] [a-z] | sed "s/-//g"'
alias xemacs="xterm -geometry 250x80 emacs -bg black -fg white"
alias z='clear'

## Local environment customization
[ -f ~/.bashrc.local ] && . ~/.bashrc.local

### end ~/.bashrc
