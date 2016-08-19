# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

## OS-specific environment setup
case "$OSTYPE" in
    linux*)
        export PATH=/usr/local/bin:$PATH
        [ -d /opt/emacs/bin/emacs ] && export EDITOR=/opt/emacs/bin/emacs || export EDITOR=/usr/local/bin/emacs
        ;;

    darwin*)
        export PATH=/usr/local/bin:$PATH
        [ -d /usr/local/bin/emacs ] && export EDITOR=/usr/local/bin/emacs || export EDITOR=/opt/emacs/bin/emacs
        ;;
esac

export VISUAL=$EDITOR

## Prepend miscellaneous directories to PATH
[ -d ~/bin ]                        && PATH=~/bin:$PATH
[ -d ~/.cabal/bin ]                 && PATH=~/.cabal/bin:$PATH
[ -d ~/work/go/bin ]                && PATH=~/work/go/bin:$PATH
[ -d ~/Library/Haskell/bin ]        && PATH=~/Library/Haskell/bin:$PATH
[ -d /usr/local/git ]               && PATH=/usr/local/git/bin:$PATH
[ -d /usr/local/go ]                && PATH=/usr/local/go/bin:$PATH

## Finally, append . to the PATH
export PATH=$PATH:.

## Make sure the homebrew site-packages directory is in the PYTHONPATH
[ -d /usr/local/lib/python2.7/site-packages ]   && PYTHONPATH=/usr/local/lib/python2.7/site-packages:$PYTHONPATH
export PYTHONPATH

## Local environment customization
[ -f ~/.profile.local ] && . ~/.profile.local

## If running bash, source ~/.bashrc
[ -n "$BASH_VERSION" -a -z "$POSIXLY_CORRECT" -a -f ~/.bashrc ] && . ~/.bashrc

## Add experimental go vendor path flag
export GO15VENDOREXPERIMENT=1

### end ~/.profile
