;; .emacs

;;; uncomment this line to disable loading of "default.el" at startup
;; (setq inhibit-default-init t)
;;;

;; I keep everything under ~/.emacs.d
(defvar emacs-root (cond ((eq system-type 'cygwin) "/home/lwheat/")
                         ((eq system-type 'gnu/linux) "/home/lwheat/")
                         ((eq system-type 'linux) "/home/lwheat/")
                         ((eq system-type 'darwin) "/Users/lwheat/")
                         (t "c:/home/lwheat/"))
  "My home directory -- the root of my personal emacs load-path")

;;; add some paths to the list of places emacs looks for elisp packages
;;;
(setq load-path (cons "~/lisp" load-path))

;; Add all the elisp directories under ~/.emacs.d to my load path
(defun add-path (p)
    (add-to-list 'load-path (concat emacs-root p))
)

(add-path ".emacs.d/lisp")                  ;; all my personal elisp code
(add-path ".emacs.d/site-lisp")             ;; elisp stuff from the net
(add-path ".emacs.d/site-lisp/color-theme") ;; http://www.emacswiki.org/cgi-bin/wiki?ColorTheme
(add-path ".emacs.d/site-lisp/erlang")      ;; file:/usr/lib64/erlang/lib/tools-2.5.2/emacs
(add-path ".emacs.d/site-lisp/git-emacs")   ;; git://github.com/tsgates/git-emacs.git
(add-path ".emacs.d/site-lisp/nxml-mode")   ;; http://www.thaiopensource.com/nxml-mode
(add-path ".emacs.d/site-lisp/ruby-mode")   ;; http://svn.ruby-lang.org/repos/ruby/trunk/misc/ruby-mode
(add-path ".emacs.d/site-lisp/speedbar")    ;; http://cedet.sourceforge.net/speedbar.shtml

;; turn on font-lock mode
;(when (fboundp 'global-font-lock-mode)
;  (global-font-lock-mode t))
(require 'font-lock) ; enable syntax highlighting
(require 'xgtags)    ; enable xgtags
(require 'gtags)     ; enable gtags

;; enable visual feedback on selections
;(setq transient-mark-mode t)

;; default to better frame titles
(setq frame-title-format
      (concat  "%b - emacs@" system-name))

;;;
;;; modifications to adapt the macbookpro's keyboard to emacs
;;;
(setq mac-command-modifier 'meta)

;;;
;;; lee's modifications to the standard .emacs
;;; pre-load the several libraries so they don't need to be loaded on the
;;; first invocation of the initial sequences
(load-library "view")
(load-library "frame")
(load-library "cc-mode")
;(load-library "p4-config")
;(load-library "ruby-config")
;(load-library "scons-config")
;(load-library "screen-config")
;(load-library "shell-config")
;(load-library "skeleton-config")
;(load-library "xml-config")
(load-library "xcscope")
(load-library "xpycscope")
;(load-library "gtags")

;;; Change some of the navigation keys to more familiar settings
(global-set-key [home]      'beginning-of-line)
(global-set-key [end]       'end-of-line)
(global-set-key [C-home]    'beginning-of-buffer)
(global-set-key [C-end]     'end-of-buffer)
(global-set-key [C-up]      'View-scroll-line-forward)
(global-set-key [C-down]    'View-scroll-line-backward)
(global-set-key [delete]    'delete-char)
(global-set-key [kp-delete] 'delete-char)
(global-set-key "\C-xp"     'previous-multiframe-window)
(global-set-key "\C-x\C-q"  'toggle-read-only)
(global-set-key [M-home]    'my-move-to-top-of-window)
(global-set-key [M-end]     'my-move-to-bottom-of-window)
(global-set-key [M-prior]   'my-scroll-window-right)
(global-set-key [M-next]    'my-scroll-window-left)
(global-set-key [f9]        'my-delete-line)
(global-set-key [f10]       'isearch-repeat-forward)
(global-set-key [f11]       'call-last-kbd-macro)
(global-set-key [f12]       'my-untabify-file)

;;; some of my olde meta-key combinations
(global-set-key "\ew" 'copy-region-as-kill)
(global-set-key "\eg" 'goto-line)

;; tagging key bindings
;(global-set-key "\C-cwg" 'tags-search)
;(global-set-key "\C-cwr" 'tags-query-replace)
;(global-set-key "\C-cwa" 'tags-apropos)
;(global-set-key "\C-cwf" 'xgtags-find-file)
;(global-set-key "\C-cwl" 'list-tags)

;;; set the font to something other than the clunky default
(set-frame-font "-Adobe-Courier-Medium-R-Normal--12-120-75-75-M-70-ISO8859-1")
;;;(set-frame-font "-Misc-Fixed-Medium-R-SemiCondensed--13-120-75-75-C-60-ISO8859-1")

;;; general display characteristics for all frames and settings
;(setq default-frame-alist '((foreground-color . "white")
;                            (background-color . "black")
;                            (cursor-color .     "white")))
;(setq initial-frame-alist '((foreground-color . "white")
;                            (background-color . "black")
;                            (cursor-color .     "white")))

;;; super-size the initial and default window frames
(setq default-frame-alist '((width  . 201)
                            (height . 64)
                           )
)
(setq initial-frame-alist '((width  . 201)
                            (height . 64)
                           )
)

;;; make some of the initial editing settings more realistic
(put 'downcase-region 'disabled nil)
(put 'upcase-region 'disabled nil)
(setq scroll-step 1)
(setq-default tab-width 4
              standard-indent 4
              indent-tabs-mode nil)
(setq-default case-fold-search nil)
(setq-default nuke-trailing-whitespace-p t)

(custom-set-variables
;   '(tab-stop-list (quote (4 8 12 16 20 24 28 32 36 40 44 48 52 56 60)))
;   '(tab-width 4)
    '(line-number-mode t)
    '(column-number-mode t)
    '(global-font-lock-mode t nil (font-lock))
;   '(inverse-video t)
)
(custom-set-faces ; only one 'custom-set-faces' entry must exist in custom.el
 '(default ((t (:foreground "white" :background "black" :size "12" :family "courier"))) t)
 '(cperl-array-face ((t (:foreground "orangered" :bold t))))
 '(cperl-hash-face ((t (:foreground "Red" :bold t))))
 '(cperl-nonoverridable-face ((t (:foreground "orange" :bold t))))
 '(custom-button-face ((t (:bold t :foreground "#3fdfcf"))))
 '(custom-group-tag-face ((t (:underline t :foreground "blue"))))
 '(custom-saved-face ((t (:underline t :foreground "orange"))))
 '(custom-state-face ((t (:foreground "green3"))))
 '(custom-variable-button-face ((t (:bold t :underline t :foreground "white"))))
 '(dired-face-permissions ((t (:foreground "green"))))
 '(font-latex-bold-face ((((class color) (background light)) (:bold t))))
 '(font-latex-italic-face ((((class color) (background light)) (:italic t))))
 '(font-latex-math-face ((((class color) (background light)) (:foreground "green3"))))
 '(font-latex-sedate-face ((((class color) (background light)) (:foreground "gold"))))
 '(font-lock-comment-face ((t (:foreground "orange3"))))
 '(font-lock-doc-string-face ((t (:foreground "Wheat3"))))
 '(font-lock-function-name-face ((t (:foreground "blue" :bold t))))
 '(font-lock-keyword-face ((t (:foreground "gold"))))
 '(font-lock-preprocessor-face ((t (:foreground "red" :bold t))))
 '(font-lock-reference-face ((t (:foreground "orangered"))))
 '(font-lock-string-face ((t (:foreground "green3"))))
 '(font-lock-type-face ((t (:foreground "#886fff" :bold t))))
 '(font-lock-variable-name-face ((t (:foreground "yellow" :bold t))))
 '(font-lock-warning-face ((t (:foreground "Violetred"  :bold t))))
 '(highlight ((t (:foreground "red3" :background "white"))) t)
 '(isearch ((t (:foreground "red" :background "white"))) t)
 '(list-mode-item-selected ((t (:foreground "green"))) t)
 '(message-cited-text ((t (:bold t :italic nil))))
 '(secondary-selection ((t (:foreground "white" :background "red"))) t)
 '(text-cursor ((t (:foreground "black" :background "green"))) t)
 '(zmacs-region ((t (:background "RoyalBlue"))) t)
 )
(custom-set-faces)

;;; ignore case when auto-completing
(setq completion-ignore-case t)

;(cond (window-system
;          (setq font-lock-face-attributes
;;                        face                     fg        bg  bf  it  ul 
;              '((font-lock-comment-face       "FireBrick"   nil nil  t  nil)
;                (font-lock-string-face        "BlueViolet"  nil nil  t  nil)
;                (font-lock-keyword-face       "MediumBlue"  nil  t  nil nil)
;                (font-lock-type-face          "ForestGreen" nil  t  nil nil)
;                (font-lock-function-name-face "DarkCyan"    nil  t   t  nil)
;                (font-lock-variable-name-face "Goldenrod"   nil  t  nil nil)
;                (font-lock-warning-face       "Salmon"      nil  t  nil nil)
;                (font-lock-constant-face      "Magenta"     nil nil  t  nil))
;              font-lock-maximum-decoration t
;              font-lock-support-mode 'lazy-lock-mode
;              font-lock-verbose nil
;              lazy-lock-stealth-verbose nil
;              )
;; Turn on Font Lock mode (changed in Emacs 19.31, this works for all)
;          (if (fboundp 'global-font-lock-mode)
;              (global-font-lock-mode t)
;              (add-hook 'find-file-hooks 'turn-on-font-lock))
;))

;; Set C indentation style
(defun my-coding-indent ()
    (interactive)
;    (c-set-style "java")
    (setq c-basic-offset 4)
    (setq tab-width 4)
;    (xgtags-mode 1)
;    (setq indent-tabs-mode 'nil)
;;   (c-toggle-auto-state 1)
)
(add-hook 'c-mode-hook 'my-coding-indent)
(add-hook 'c-mode-common-hook 'my-coding-indent)

(defun my-frame ()
    (interactive)
    (set-foreground-color "white")
    (set-background-color "black")
    (set-cursor-color "white")
    (set-frame-font "-Misc-Fixed-Medium-R-SemiCondensed--13-120-75-75-C-60-ISO8859-1")
)

(defun my-transpose-lines ()
    (interactive)
    (transpose-lines '0)
    (previous-line '2)
)

(defun my-untabify-file (file)
    (interactive "fLoad file: ")
    (c-mode)
    (find-file (expand-file-name file))
    (untabify (point-min) (point-max))
    (basic-save-buffer)
)

(defun my-delete-line()
    (interactive)
    (beginning-of-line)
    (kill-line)
    (kill-line)
)
 
(defun my-move-to-top-of-window ()
    (interactive)
    (move-to-window-line 0)
)

(defun my-move-to-bottom-of-window ()
    (interactive)
    (move-to-window-line -1)
)

(defun my-scroll-window-left()
    (interactive)
    (scroll-left 1)
)

(defun my-scroll-window-right()
    (interactive)
    (scroll-right 1)
)
