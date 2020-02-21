# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# delete directory from path if present
delete_path()
{
    local p d
    p=":$1:"
    d=":$PATH:"
    d=${d//$p/:}
    d=${d/#:/}
    PATH=${d/%:/}
}

# if directory exists, add directory to end. delete if present already
append_path()
{
    #[[ -d "$2" && ":$PATH:" != *":$2:"* ]] && eval "$1=\$$1:2"
    [ -d "$2" ] && delete_path $2 && eval "$1=\$$1:2"
}

# if directory exists, add directory to beginning. delete if present already
prepend_path()
{
    #[[ -d "$2" && ":$PATH:" != *":$2:"* ]] && eval "$1=$2:\$$1"
    [ -d "$2" ] && delete_path $2 && eval "$1=$2:\$$1"
}

## OS-specific environment setup
case "$OSTYPE" in
    linux*)
        prepend_path PATH /usr/local/bin
        #export PATH=/usr/local/bin:$PATH
        [ -f /opt/emacs/bin/emacs ] && export EDITOR=/opt/emacs/bin/emacs || export EDITOR=/usr/local/bin/emacs
        ;;

    darwin*)
        prepend_path PATH /usr/local/bin
        #export PATH=/usr/local/bin:$PATH
        [ -f /usr/local/bin/emacs ] && export EDITOR=/usr/local/bin/emacs || export EDITOR=/opt/emacs/bin/emacs
        ;;
esac

[ ! -z "$EDITOR" ] && export VISUAL=$EDITOR

## Prepend miscellaneous directories to PATH
#[ -d ~/bin ]                 && PATH=~/bin:$PATH
#[ -d ~/.cabal/bin ]          && PATH=~/.cabal/bin:$PATH
#[ -d ~/work/go/bin ]         && PATH=~/work/go/bin:$PATH
#[ -d ~/Library/Haskell/bin ] && PATH=~/Library/Haskell/bin:$PATH
#[ -d /usr/local/git ]        && PATH=/usr/local/git/bin:$PATH
#[ -d /usr/local/go ]         && PATH=/usr/local/go/bin:$PATH
#[ -d "`dirname $EDITOR`" ]   && PATH=`dirname $EDITOR`:$PATH
prepend_path PATH ~/bin
prepend_path PATH ~/.cabal/bin
prepend_path PATH ~/work/go/bin
prepend_path PATH ~/Library/Haskell/bin
prepend_path PATH /usr/local/git
prepend_path PATH /usr/local/go
prepend_path PATH "`dirname $EDITOR`"
prepend_path PATH "/usr/local/opt/swagger-codegen@2/bin"
prepend_path PATH "/usr/local/opt/postgresql@10/bin"
## Other environment setup
[ -d /usr/local/go ] && export GOROOT=/usr/local/go
[ -d ~/work/go ] && export GOPATH=~/work/go
[ -d ~/work/go/bin ] && export GOBIN=~/work/go/bin

## Make sure the homebrew site-packages directory is in the PYTHONPATH
[ -d /usr/local/lib/python2.7/site-packages ]   && PYTHONPATH=/usr/local/lib/python2.7/site-packages:$PYTHONPATH
export PYTHONPATH

## Local environment customization
[ -f ~/.profile.local ] && . ~/.profile.local

## If running bash, source ~/.bashrc
[ -n "$BASH_VERSION" -a -z "$POSIXLY_CORRECT" -a -f ~/.bashrc ] && . ~/.bashrc

## Finally, append . to the PATH
export PATH=$PATH:.

## Add experimental go vendor path flag
export GO15VENDOREXPERIMENT=1

### end ~/.profile
if [ -e /Users/lwheat/.nix-profile/etc/profile.d/nix.sh ]; then . /Users/lwheat/.nix-profile/etc/profile.d/nix.sh; fi # added by Nix installer
