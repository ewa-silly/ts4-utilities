# ts4-utilities
Utility program(s) related to playing and extending The Sims 4.  Right
now, there's just one:

## "Bulk Rename" mod files: `mod_name_fix.py` 

This is a command-line utility which renames all the files in or under
a specified directory according to user-selectable rules.

It's a [Python](https://docs.python.org/3/tutorial/index.html) script,
written for MacOS / OS X.  You don't need to know any Python to use
it, and you don't need to be a command-line wizard, but you should be
familiar with the basic concepts of paths (directories) as written on
the command line, and with command-line arguments / options.  I'll
link to helpful resources a little later in this document.

So, what does it do?

## Usage

The `mod_name_fix.py` script is run from the command-line terminal
like this:

``` shellsession
	$ mod_name_fix.py (some options about what to do) (directory to do renaming in)
```

### Basic Example

Here's an example of what that looks like in practice:

``` shellsession 
	Erics-MacBook-Pro:sims4_backup andersoe $ pwd
	/Users/andersoe/sims4_backup

	Erics-MacBook-Pro:sims4_backup andersoe $ ls
	CC        Tray      foobar    mods_home saves

	Erics-MacBook-Pro:sims4_backup andersoe $ ~/projects/ts4-utilities/mod_name_fix.py --dashes delete foobar/
```

Let me break that down a bit:

![Image](docs/tutorial-cmd-line.svg "Image of the preceding command
line, with boxes highlighting different parts.")

There are four parts to this command:

  1. (Grey box) This is the "command prompt" shown to you by the
      operating system.  In my configuration, this is showing me what
      computer I'm on (`Erics-MacBook-Pro`), what directory I'm in
      (`sims4_backup`), and what user I'm logged in as (`andersoe`).
      Everything after the prompt is typed in by the user, which in
      this case is me.
  2. (Blue box) This is the command to run.  `mod_name_fix.py` is the
     name of the script, and `~/projects/ts4-utilities/` is the
     directory where it's saved. (`~` means "my home directory" in the
     command line shell).  The directory structure I'm working with is
     shown in [this picture](docs/tutorial-cmd-line) in case that's
     helpful.
  3. (Green box) These are _command-line options_, which in this case
     tell the script to (a) process dashes in file names, and (b)
     specifically to delete them.  That is to say that it would rename
     `A-B` to `AB`.
  4. (Red box) This is the directory in which to do the renaming.
     This _argument_ could be a _relative_ or _absolute_ path; in this
     case it's a _relative_ path refering to the `foobar` subdirectory
     within the current directory.
	 
The command as written won't do anything because of a safety check in
the program, discussed in the following section:

### Command-Line Options

Note:  Documentation like this has a tendency to get out-of-date
relative to the actual functionality of the program, so please be
aware that you can always get a list the correct, current, options
from the program itself by running `mod_name_fix.py -h` (`-h` is for
_help_.)

This script supports 3 categories of characters (or character
sequences) to change, and provides four options for what to do with
each one:

#### Main Options

Option           | Meaning
---------------- | -------
`--whitespace`   | Change "white space" characters (space, tab, return, etc.)
`--dashes`       | Change - and _ characters.  Specifically, process sequences of dashes _of any length_ into a _single_ replacement character.
`--specials`     | Change "special" characters (~, &, [, ], /, and \).


For each "character set" option, there are 4 options of what to do
with it:

Option       | Meaning
-------------|--------
`delete`     | Just remove any occurence of the characters in characters in question. _e.g._ `--whitespace delete` would transform `This And That.mod` into `ThisAndThat.mod`.
`to_dash`    | Convert the characters in question to a dash.
`underscore` | Convert the characters in question to an underscore.
`error`      | Treat any occurence of of the characters as an error and exit the program.  This is useful as a check, to verify that you don't have any files with an offending name left.

For example `mod_name_fix.py --dashes underscore` what rename `This_-__-And__That.mod` to `This_And_That.mod`.

There's one additional "what to do" option:

Option                  | Meaning
------------------------|--------
`-t` or `--tilde_space` | Treat tilde characters (`~`) as white space.  This is useful if you have a lot of file names like `This~And~That` or `This ~ And That`, which I've run into a bit.


That's it.  That's all the "main" options.  They can be combined, so `mod_name_fix.py --dashes delete --whitespace delete -t` would delete all dash characters and whitespace characters, with `~` included.

#### Safety Options

This script exists to bulk-rename mod files, but it isn't picky.
Since it will recursively rename *every* file with a matching name in
*every* subdirectory of *any* target directory specified, there are a
couple of safety option to reduce the odds of doing something
regretable. These are:

Option                  | Meaning
------------------------|--------
`--really`              | Actually make the requested changes.  Without the `--really` option, the program will list the files that _would be_ renamed, but not actually rename anything.
`-e` or `--elsewhere`   | Allow a target directory that is *not* a subdirectory of your current working directory.  This check exists so that it's harder to make a typo and blow away files in some random directory.
`-o N` or `--only N`    | Instead of going through and renaming *every* matching file, rename only _N_ files and then stop.  This is, again, a chance to make sure it's doing what you want.

### Complete Example

This will go through the `mods_home` directory (which is a
subdirectory of the current working directory), find every file with
dashes in the name, and rename each one to remove the dashes.

``` shellsession
~/projects/ts4-utilities/mod_name_fix.py --dashes delete --really mods_home
```

# Resources

## MacOS / OS X Command Line

These appear to be good tutorials for using the command-line (terminal) interface on a Mac:
* [A Beginner's Guide to Using the Mac Terminal](https://www.makeuseof.com/tag/beginners-guide-mac-terminal/) at MakeUseOf.
* [Getting to Know the Command Line](https://www.davidbaumgold.com/tutorials/command-line/) on David Baumgold's blog.
* [Command Line Primer](https://developer.apple.com/library/archive/documentation/OpenSource/Conceptual/ShellScripting/CommandLInePrimer/CommandLine.html) from Apple Developer.


