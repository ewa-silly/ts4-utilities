#!/usr/bin/env python3

""" File and directory renamer for The Sims 4 CC / mods.
"""

__DOCS_URL__ = "https://github.com/ewa-silly/ts4-utilities#usage"

__DEBUG_DIR_WALK__ = False


import os
import sys
import re
import argparse
import pathlib
import shutil
import textwrap
import logging

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

def do_parse(args, dbg_lvl=0):

    _help_=("""This is the Sims 4 mod and CC renaming tool.  

    To use it, you must provide additional information via command-line arguments. On-line help is available at %(url)s.

    If you are familiar with unix-style command-line tools, the supported usage is as follows:
    """ % {"url": __DOCS_URL__}).splitlines()
    
    wrapper = textwrap.TextWrapper(replace_whitespace=False, width=shutil.get_terminal_size()[0])
    _help_ = [wrapper.wrap(textwrap.dedent(p)) for p in _help_]

    
    
    parser = argparse.ArgumentParser(epilog="This script only takes one kind of renaming action at a time.  That is, one and only one of --whitespace, --dashes, and --specials may be specified at once.  To perform multiple actions, run this program once with each.")

    parser.add_argument('dir', action='store', metavar='target_directory', type=pathlib.Path,
                        help='Recursively process all files in all directories under target_directory'
    )

    one_action = parser.add_mutually_exclusive_group(required=True)
    
    one_action.add_argument('--whitespace', action='store', nargs=1,
                        choices=['delete', 'to_dash', 'underscore', 'error'],
                        help=
                        """Match on whitespace characters in file/directory names""")

    one_action.add_argument('--dashes', action='store', nargs=1,
                        choices=['delete', 'to_dash', 'underscore', 'error'],
                        help='Compress redonkulous sequences of _-_ type things')
    one_action.add_argument('--specials', action='store', nargs=1,
                        choices=['delete', 'to_dash', 'underscore', 'error'],
                        help="""Match 'special' characters such as ~ & [ ] ( ) { } / \\""")

    
    parser.add_argument('-t', '--tilde_space', action='store_true',
                         help="Treat tilde as whitespace instead of a general special.")

    parser.add_argument('--really', action='store_true', default=False,
                        help="Actually make the changes")

    parser.add_argument('-e', '--elsewhere', action='store_true', default=False,
                        help="Allow target_directory outside current directory")

    parser.add_argument('-o', '--only', action='store', type=int,
                        metavar='N', help="Only make N changes before stopping")


    ##Actions are reused by "whitespace" and "specials"
    ap = argparse.ArgumentParser("Actions for Matches", add_help=False)
    
    ## Special-case check for the "no arguments supplied" situation
    if len(args)==1:
        print('\n'.join(['\n'.join(l) for l in _help_]))
        #print(repr(wrapper.wrap(_help_)))
        parser.print_help()
        sys.exit(1)
        
    args_opts = parser.parse_args(args[1:])

    logger.debug("Options/arguments (as parsed): " + repr(args_opts))

    
    return (parser, args_opts)
    

def main(args):

    DEBUG=2

    (parser, args_opts) = do_parse(args, DEBUG)

    root = args_opts.dir
    root_r = root.resolve(strict=True)
    here = pathlib.Path.cwd()
    here_r = here.resolve(strict=True)


    logger.debug("Parent directories of target (root) directory:\n\t" + '\n\t'.join([str(p) for p in root_r.parents]))
    logger.debug("Current directory is one of those parents: " + str(here_r in root_r.parents))


    if not (here_r in root_r.parents or # Root is a subdirectory of cwd
            here_r == root_r or         # Root is cwd
            args_opts.elsewhere):       # --elsewhere is selected

        sys.stderr.write("""\nABORT\n\nSelected target_directory "%s" ("%s") is not a subdirectory of your current directory %s\nand the 'elsewhere' option is not set.\n\n""" % (root, root_r, here))
        sys.exit(-1)
    

    # Actual matching regex
    mster = None
    action = None

    if args_opts.whitespace:
        action = args_opts.whitespace[0]
    elif args_opts.specials:
        action = args_opts.specials[0]
    elif args_opts.dashes:
        action = args_opts.dashes[0]

    if action is None:
        parser.error("At least one renaming option (e.g. --whitespace, --dashes, ...)  must be specified")
    
    if  (args_opts.whitespace and not args_opts.tilde_space):
        mster = re.compile("\s+")
    elif (args_opts.whitespace and args_opts.tilde_space):
        mster = re.compile("[\s~]+")
    elif (args_opts.specials and not args_opts.tilde_space):
        mster = re.compile("[^\w_\- .]+")
    elif (args_opts.specials and args_opts.tilde_space):
        mster = re.compile("[^\w~_\- .]+")
    elif (args_opts.dashes):
        mster = re.compile("[_\-~][_\-~]+")


    # String replacements
    action_repls = {
        'delete' : '',
        'to_dash' : '-',
        'underscore' : '_',
        'error' : Exception("Yo, this is the error case")
    }
    
    my_repl = action_repls[action]
    logger.debug("Selected action: {}".format(action))
    logger.debug("Pattern to match: {}".format(mster))
    logger.debug("Replacement string: {}".format(repr(my_repl)))

    
    #print(repr(root))

    change_ct = 0
    
    #Iterate, depth-first.  Depth-first IS IMPORTANT so we don't
    #rename a directory and then try to recurse into (the old name's)
    #subdirectories

    if not args_opts.really:
        print("\nExecuting dry run (without --really option).  The following changes (if any) would be made if run with --really:\n")
    
    for (dir, subs, files, fd) in os.fwalk(root_r, topdown=False):
        logger.debug("Walking directory %s:" % (dir))

        #sanity
        dir_path = pathlib.Path(dir)
        if not dir_path.exists():
            raise UserWarning("I think I'm in '%s', but also it does not exist!??" % (dir_path))
        if not dir_path.is_dir():
            raise UserWarning("Path is not a directory?: '%s'" % (dir_path))

        if __DEBUG_DIR_WALK__:
            logger.debug("Files in this directory:\n " + '\n'.join(['\t%s' % f for f in files]))
    
        for f in files:
            full_p = dir_path / pathlib.Path(f)

            #sanity
            if not full_p.exists():
                raise UserWarning("File '%s' does not exist!??" % (full_p))
            if not full_p.is_file():
                raise UserWarning("Path is not a file?: '%s'" % (full_p))
            if full_p.is_symlink():
                raise UserWarning("Path is a symlink? Not cool, man: '%s'" % (full_p))


            if (action == 'error' and mster.search(f)):
                raise ValueError("Filename '%s' matches regex: %s, and you requested treating that as an error" % (f, repr(mster.search(f))))
            
            (newstr, ct) = mster.subn(my_repl,f) # ct is # of substitutions made 
            if (ct > 0):
                new_p = dir_path / pathlib.Path(newstr)
                #print("\t === %s" % new_p)
                if args_opts.really:
                    logger.info("Renaming file '%s' -->  '%s'" % (f, newstr))
                    logger.debug("Renaming file (full) '%s' --> '%s'" % (full_p, new_p))
                    full_p.rename(new_p)
                else:
                    logger.info("WOULD rename file '%s' -->  '%s'" % (f, newstr))
        
                change_ct = change_ct + 1
                if (args_opts.only is not None and (change_ct >= args_opts.only)):
                    print("This was change number %d, and you requested a limit" % (change_ct))
                    sys.exit(1)
 
                    
                

                
        if __DEBUG_DIR_WALK__:                
            logger.debug("Subdirectories in this directory:\n " + '\n'.join(['\t%s' % d for d in subs]))
        
        for d in subs:

            full_p = dir_path / pathlib.Path(d)

            #sanity
            if not full_p.exists():
                raise UserWarning("Dir '%s' does not exist!??" % (full_p))
            if not full_p.is_dir():
                raise UserWarning("Path is not a dir?: '%s'" % (full_p))
            if full_p.is_symlink():
                raise UserWarning("Path is a symlink? Not cool, man: '%s'" % (full_p))

            #print("\t(%d) %s" % (fd, d))

            (newstr, ct) = mster.subn(my_repl,d)

            logger.debug("Directory path '%s' matches pattern '%s': %d" % (d, mster, ct))
            if (ct > 0):
                new_p = dir_path / pathlib.Path(newstr)
                if args_opts.really:
                    logger.info("Renaming dir '%s' -->  '%s'" % (d, newstr))
                    logger.debug("Renaming dir (full) '%s' --> '%s'" % (full_p, new_p))

                    full_p.rename(new_p)
                else:
                    logger.info("WOULD rename dir '%s' -->  '%s'" % (d, newstr))
        
                change_ct = change_ct + 1
                if (args_opts.only is not None and (change_ct >= args_opts.only)):
                    print("This was change number %d, and you requested a limit" % (change_ct))
                    sys.exit(1)

        
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

    
