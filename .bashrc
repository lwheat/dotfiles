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
if [ -n "$(type -p tput)" ] && tput setaf 1 >&/dev/null; then
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
if [ -n "$(type -p lesspipe)" ]; then
    eval "$(SHELL=/bin/sh lesspipe)"
fi
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

# Turn off stop (^S) control character
stty stop undef

# Don't echo control characters
stty -echoctl

# add private ssh keys to the authentication daemon, if present
add-ssh-keys() {
    if [ -d ~/.ssh ]; then
        if [ -z "`ssh-add -l`" ]; then
            echo "adding keys to ssh-agent"
            ssh-add
            if [ $? -ne 0 ]; then
                echo "problem adding keys to ssh-agent"
            fi
        else
            echo "keys present in ssh-agent already"
        fi
    fi
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
        alias startvnc="vncserver -geometry 1870x980 -alwaysshared :`id -u`"
        alias stopvnc="vncserver -kill :`id -u`"
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
        brew-depend() {
            brew list | while read cask; do echo -e -n "\033[1;34m$cask ->\033[0m"; brew deps $cask | awk '{printf(" %s ", $0)}'; echo ""; done
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
        alias unquarantine='xattr -d com.apple.quarantine'
        alias-app "/Applications/VMware Fusion.app/Contents/Library/VMware OVF Tool/ovftool"
        alias-app "/Applications/p4merge.app/Contents/MacOS/p4merge"
        alias-app "/Applications/p4v.app/Contents/MacOS/p4v"
        alias-app "/Applications/ccollab_client/p4collab"
        #alias-app "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage"
        # if docker-machine is installed, add alias to configure/remove environment so we can talk to it
        if [ ! -z "`which docker-machine`" ]; then
            alias docker-setenv='eval "$(docker-machine env)"'
            alias docker-rmenv='unset `printenv | grep ^DOCKER | cut -f1 -d=`'
        fi
        # Spirent-specific stuff
        if [ -d ~/OneDrive\ -\ Spirent\ Communications ]; then
            alias fix-broken-links='for i in `cat broken-links`; do ln -sf `readlink $i | sed "s,/home/lwheat/work/intqemu,/Users/lwheat/work/integration,"` $i; done'
            alias mount-bkup='sudo bash -c "mkdir -p /mnt/backups && sudo mount -t nfs rtp-engnas01.ad.spirentcom.com:/c/backups /mnt/backups"'
            alias umount-bkup="sudo umount /mnt/backups"
            alias mount-cross='sudo bash -c "mkdir -p /export/crosstools && sudo mount -t nfs rtp-engnas01.ad.spirentcom.com:/c/il-crosstools /export/crosstools"'
            alias umount-cross="sudo umount /export/crosstools"
            alias mount-isos='sudo bash -c "mkdir -p /mnt/isos && sudo mount -t nfs rtp-engnas01.ad.spirentcom.com:/c/isos /mnt/isos"'
            alias umount-isos="sudo umount /mnt/isos"
            alias mount-mcelroy='sudo bash -c "mkdir -p /mnt/mcelroy && sudo mount -t nfs mcelroy.ad.spirentcom.com:/export/archive/pv /mnt/mcelroy"'
            alias umount-mcelroy="sudo umount /mnt/mcelroy"
            alias mount-martin='sudo bash -c "mkdir -p /mnt/martin && sudo mount -t nfs martin.ad.spirentcom.com:/export/archive/pv /mnt/martin"'
            alias umount-martin="sudo umount /mnt/martin"
            alias ssh-stc='ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o KexAlgorithms=diffie-hellman-group1-sha1,diffie-hellman-group14-sha1'
            alias scp-stc='scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o KexAlgorithms=diffie-hellman-group1-sha1,diffie-hellman-group14-sha1'
            alias ssh-chassis='ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o KexAlgorithms=diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 -o HostKeyAlgorithms=+ssh-dss'
            backup-mac() {
                baseBackupDir=/mnt/backups/individual-machines
                fullBackupPath=$baseBackupDir/lwheat-mac
                if [ -d $baseBackupDir ]; then
                    mkdir -p $fullBackupPath || (echo Unable to create $fullBackupPath; exit 1)
                    dotList=".spacemacs .emacs.d .spacemacs.local .bashrc .gem .gitconfig .gitignore_global .gitmodules .hgignore_global .hgrc .kube .minikube .nmap .npm .p4environ .profile .pylintrc .screenrc .telnetrc .tmux.conf .vim .viminfo"
                    dirList="Documents Downloads bin tmp work"
                    oneDriveDir="OneDrive - Spirent Communications"
                    fileList=""
                    for i in $dotList $fileList $dirList "$oneDriveDir"
                    do
                        [ -e "$i" ] && echo `date "+ %b %d %H:%M:%S"`" - backing up $i" || continue
                        rsync -az /Users/lwheat/"$i" $fullBackupPath
                    done
                    echo `date "+ %b %d %H:%M:%S"`" - done"
                else
                    echo "$baseBackupDir not present. try mounting it?"
                fi
            }
        fi

        ;;
    cygwin*)
        p4() {
            export PWD=`cygpath -wa .`
            /cygdrive/c/Program\ Files/Perforce/p4.exe $@
        }
        [ -f /cygdrive/c/Program\ Files/Notepad++/notepad++.exe ] && alias np++='/cygdrive/c/Program\ Files/Notepad++/notepad++.exe'
        #[ -f /drives/c/Program\ Files/Notepad++/notepad++.exe ] && alias np++='/drives/c/Program\ Files/Notepad++/notepad++.exe'
        alias mount-bkup="mkdir -p /backups && mount //rtp-engnas01.ad.spirentcom.com/backups /backups"
        alias umount-bkup="umount /backups"
        backup-devvm() {
            if [ -L /cygdrive ] && [ -d /drives ]; then
                rootDirectoryPath=/drives/c
            elif [ -d /cygdrive ]; then
                rootDirectoryPath=/cygdrive/c
            else
                echo "No root directory detected"
                return 1
            fi
            rootDirectoryPath=/drives/c
            baseBackupDir=/backups/individual-machines
            fullBackupPath=$baseBackupDir/lwheat-devvm
            if [ -d $baseBackupDir ]; then
                currentUmask=`umask`
                umask g=rwx,o=rwx
                mkdir -p $fullBackupPath || (echo Unable to create $fullBackupPath; return 1)
                pushd $rootDirectoryPath >/dev/null
                #dotList=".spacemacs .emacs.d .spacemacs.local .bashrc .gem .gitconfig .gitignore_global .gitmodules .hgignore_global .hgrc .kube .minikube .nmap .npm .p4environ .profile .pylintrc .screenrc .telnetrc .tmux.conf .vim .viminfo"
                dotList=".profile .viminfo"
                #dirList="Documents Downloads bin tmp work"
                dirList="bin tmp dev"
                #oneDriveDir="Users/spirent/OneDrive - Spirent Communications"
                oneDriveDir=""
                fileList=""
                #done
                for i in $dotList $fileList $dirList "$oneDriveDir"
                do
                    [ -e "$i" ] && echo `date "+ %b %d %H:%M:%S"`" - backing up $i" || continue
                    #rsync -az /Users/lwheat/"$i" $fullBackupPath
                    rsync -az --exclude 'Debug/' --exclude 'Debug_x64/' --exclude 'Release/' --exclude='Release_x64/' "$i" $fullBackupPath
                done
                echo `date "+ %b %d %H:%M:%S"`" - done"
                popd >/dev/null
                umask $currentUmask
            else
                echo "$baseBackupDir not present. try mounting it?"
            fi
        }
        ;;
esac

## git helpers - common
#
# sync an individual repo directory. it's a clone of a forked repo or
# a clone of the repo itself
#
sync-repo-dir() {
    dryRunArg=""
    if [ $# -gt 0 ]; then
        if [ "$1" == "-n" ]; then
            dryRunArg=$1
            shift
        fi
    fi
    if [ $# -gt 0 ]; then
        branchName="master"
        dirName=$1
        if [ $# -gt 1 ]; then
            branchName=$2
        fi
        pushd $dirName > /dev/null
        currentBranch=`git branch | grep \* | cut -d" " -f2-`
        if [ ! -z "$currentBranch" ]; then
            if [ "$currentBranch" = "$branchName" ]; then
                if [ `git remote -v | grep ^upstream | wc -l | tr -d " "` -gt 0 ]; then
                    echo "==== "$dirName"("$branchName") is a fork ===="
                    [ -z "$dryRunArg" ] && git pull upstream $currentBranch && git push origin $currentBranch
                else
                    echo "==== "$dirName"("$branchName") is not a fork ===="
                    [ -z "$dryRunArg" ] && git pull origin $currentBranch
                fi
            else
                echo "$dirName, $currentBranch is current branch, not $branchName"
            fi
        else
            echo "$dirName, cannot find current branch"
        fi
        popd > /dev/null
    fi
}

#
# find all the cloned git repos in the list of directories and sync each one
#
walk-git-tree() {
    dryRunArg=""
    if [ $# -gt 0 ]; then
        if [ "$1" == "-n" ]; then
            dryRunArg=$1
            shift
        fi
    fi
    if [ $# -gt 0 ]; then
        dirList=$1
        startDir=`pwd`
        for i in $dirList ; do
            for j in `find $i -name .git` ; do
                sync-repo-dir $dryRunArg "`dirname $j`"
            done
        done
    fi
}

#
# sync all cloned repos under the passed in direcotry list or under all directories
# in the current working directory.
#
sync-forks() {
    dryRunArg=""
    if [ $# -gt 0 ]; then
        if [ "$1" == "-n" ]; then
            dryRunArg=$1
            shift
        fi
    fi
    dirList=$@
    if [ $# -eq 0 ]; then
        dirList=`ls -1F | grep "/$" | sed -e 's,/$,,'`
    fi
    walk-git-tree $dryRunArg "$dirList"
}

#
# start STCv VMs on QManager
#
start-stc-vm() {
    if [ -f ~/bin/start_stc_vm.py ]; then
        stcVmVersion=""
        if [ $# -gt 0 ]; then
            stcVmVersion=$1
            python ~/bin/start_stc_vm.py lwheat "#${stcVmVersion}" $((60*24*14))
        else
            echo "STCv version number missing"
        fi
    else
        echo "start script ~/bin/start_stc_vm.py not found"
    fi
}

#
# start a generic VM on QManager
#
start-generic-vm() {
    if [ -f ~/bin/start_generic_vm.py ]; then
        vmPath=""
        if [ $# -gt 0 ]; then
            vmPath=$1
            python ~/bin/start_generic_vm.py lwheat "${vmPath}"
        else
            echo "VM path missing"
        fi
    else
        echo "start script ~/bin/start_generic_vm.py not found"
    fi
}

#
# Check to see if the specified VM(s) have obtained an IP address
#
wait-for-vms() {
    if [ -f ~/bin/get_vm_ip.py ]; then
        vmIds=""
        if [ $# -gt 0 ]; then
            vmIds=$@
            while [ true ]; do
                for i in ${vmIds}; do
                    python ~/bin/get_vm_ip.py $i
                done
                sleep 5
            done
        else
            echo "VM ID(s) missing"
        fi
    else
        echo "start script ~/bin/get_vm_ip.py not found"
    fi
}

## Aliases - common
#alias emacs='emacs -bg black -fg white'
alias lsd='/bin/ls -F | grep / | sed -e "s,/$,,"'
alias lsdd='/bin/ls -Fd .[A-Z][a-z]* * | grep / | sed -e "s,/$,,"'
alias lsnpm='npm list -g --depth=0'
alias llsd='/bin/ls -l | grep ^d'
alias p4head='p4 changes -m1 @`p4 client -o | grep ^Client: | cut -f2 -d"	" | tr -d "\r\n"`'
alias sha1='openssl dgst -sha1'
alias sha256='openssl dgst -sha256'
alias ssh-nosave='ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
alias scp-nosave='scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
alias md5='openssl dgst -md5'
[ -f ~/bin/Table.jar -a -f ~/bin/TABLE.properties ] && alias table-build='java -jar ~/bin/Table.jar'
alias unquarantine='xattr -d com.apple.quarantine'
alias uuidhash='uuidgen | tr [A-Z] [a-z] | sed "s/-//g"'
alias xemacs="xterm -geometry 250x80 emacs -bg black -fg white"
alias z='clear'

## Local environment customization
[ -f ~/.bashrc.local ] && . ~/.bashrc.local

## add bash completetion customizations
[ -f /usr/local/etc/bash_completion ] && . /usr/local/etc/bash_completion

### end ~/.bashrc
