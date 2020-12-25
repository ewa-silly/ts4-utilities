#!/usr/bin/env python3

""" File and directory renamer for The Sims 4 CC / mods.
"""

__DOCS_URL__ = "https://github.com/ewa-silly/ts4-utilities#usage"

import os
import sys
import re
import argparse
import pathlib
import textwrap

def do_parse(args, dbg_lvl=0):

    _help_=("""This is the Sims 4 mod and CC renaming tool.  

    To use it, you must provide additional information via
    command-line arguments. On-line help is available at %(url)s.

    If you are familiar with unix-style command-line tools, the supported usage is as follows:
    """ % {"url": __DOCS_URL__}).splitlines()
    
    wrapper = textwrap.TextWrapper(replace_whitespace=False)
    _help_ = [wrapper.wrap(textwrap.dedent(p)) for p in _help_]

    
    
    parser = argparse.ArgumentParser()

    parser.add_argument('dir', action='store', metavar='target_directory', type=pathlib.Path,
                        help='Recursively process all files in all directories under target_directory'
    )

    parser.add_argument('--whitespace', action='store', nargs=1,
                        choices=['delete', 'to_dash', 'underscore', 'error'],
                        help=
                        """Match on whitespace characters in file/directory names""")

    parser.add_argument('--dashes', action='store', nargs=1,
                        choices=['delete', 'to_dash', 'underscore', 'error'],
                        help='Compress redonkulous sequences of _-_ type things')
    parser.add_argument('--specials', action='store', nargs=1,
                        choices=['delete', 'to_dash', 'underscore', 'error'],
                        help="""Match 'special' characters: ~ & [ ] / \\""")

    
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

    if ((args_opts.whitespace is not None and args_opts.whitespace != False) and
        (args_opts.specials is not None and args_opts.specials != False)):
        sys.stderr.write("--specials, --whitespace, and --dashes are mutually exclusive.\nRun them in separate passes if needed.")
    
    if (dbg_lvl >= 1):
        print(repr(args_opts))

    
    return args_opts
    

def main(args):

    DEBUG=2

    args_opts = do_parse(args, DEBUG)

    root = args_opts.dir
    root_r = root.resolve(strict=True)
    here = pathlib.Path.cwd()
    here_r = here.resolve(strict=True)

    if (DEBUG >=2):

        print(repr(list(root_r.parents)))
        print(here_r in root_r.parents)


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
    
    #print(repr(root))

    change_ct = 0
    #Iterate, depth-first
    for (dir, subs, files, fd) in os.fwalk(root_r, topdown=False):
        print("(%d) %s:" % (fd, dir))

        #sanity
        dir_path = pathlib.Path(dir)
        if not dir_path.exists():
            raise UserWarning("I think I'm in '%s', but also it does not exist!??" % (dir_path))
        if not dir_path.is_dir():
            raise UserWarning("Path is not a directory?: '%s'" % (dir_path))

        
        print("Files:")
        for f in files:
            full_p = dir_path / pathlib.Path(f)

            #sanity
            if not full_p.exists():
                raise UserWarning("File '%s' does not exist!??" % (full_p))
            if not full_p.is_file():
                raise UserWarning("Path is not a file?: '%s'" % (full_p))
            if full_p.is_symlink():
                raise UserWarning("Path is a symlink? Not cool, man: '%s'" % (full_p))


            print("\t(%d) %s" % (fd,f))

            if (action == 'error' and mster.search(f)):
                raise ValueError("Filename '%s' matches regex: %s, and you requested treating that as an error" % (f, repr(mster.search(f))))
            
            (newstr, ct) = mster.subn(my_repl,f)
            if (ct > 0):
                print("\t -->  %s" % (newstr))
                new_p = dir_path / pathlib.Path(newstr)
                #print("\t === %s" % new_p)
                if args_opts.really:
                    full_p.rename(new_p)
                    # sys.stderr.write(" xx %s ==> %s\n" % (repr(new_p), repr(actual_new)))
                    # if actual_new.resolve() != new_p.resolve():
                    #     print("Hmmm: %s %s" % (new_p, actualy_new))
                    #     raise Exception("Eep!")
                else:
                    print("\t To do it for real, pass --really flag")
        
                change_ct = change_ct + 1
                if (args_opts.only is not None and (change_ct >= args_opts.only)):
                    print("This was change number %d, and you requested a limit" % (change_ct))
                    sys.exit(1)
 
                    
                

                
                
        print("\nSubdirectories:")
        for d in subs:

            full_p = dir_path / pathlib.Path(d)

            #sanity
            if not full_p.exists():
                raise UserWarning("Dir '%s' does not exist!??" % (full_p))
            if not full_p.is_dir():
                raise UserWarning("Path is not a dir?: '%s'" % (full_p))
            if full_p.is_symlink():
                raise UserWarning("Path is a symlink? Not cool, man: '%s'" % (full_p))

            print("\t(%d) %s" % (fd, d))

            (newstr, ct) = mster.subn(my_repl,d)
            if (ct > 0):
                print("\t -->  %s" % (newstr))
                new_p = dir_path / pathlib.Path(newstr)
                #print("\t === %s" % new_p)
                if args_opts.really:
                    full_p.rename(new_p)
                    # sys.stderr.write(" xx %s ==> %s\n" % (repr(new_p), repr(actual_new)))
                    # if actual_new.resolve() != new_p.resolve():
                    #     print("Hmmm: %s %s" % (new_p, actualy_new))
                    #     raise Exception("Eep!")
                else:
                    print("\t To do it for real, pass --really flag")
        
                change_ct = change_ct + 1
                if (args_opts.only is not None and (change_ct >= args_opts.only)):
                    print("This was change number %d, and you requested a limit" % (change_ct))
                    sys.exit(1)

        
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

    
