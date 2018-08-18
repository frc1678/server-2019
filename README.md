# 1678 Server 2018 Recode

The server is responsible for all data calculations.  It is also responsible for receiving data from scouts and sending scouts team assignments.  The server is also responsible for creating data exports for strategy use, for tracking missing data and reporting it to lead scouts, and for sending upcoming match notifications.

## Style Guide

We follow the standard [PEP8 Style Guidelines](https://www.python.org/dev/peps/pep-0008/).
To enforce style, we use `pylint`, which can be installed with

```pip install pylint```

To test your code, use `pylint server-2018-recode`. If you changed the name of your repository folder or if you are not located in your repository folder, replace `server-2018-recode` with the path to your repository folder.

### Commit Messages

Write good commit messages!  See [here](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html) and [here](https://chris.beams.io/posts/git-commit/) for helpful articles.

* Commit messages should have an extended description unless the change is very simple (e.g. a couple lines or small fixes).
* Subject lines should be 50 characters or less
* Each line on the extended description should be 72 characters or less

To help enforce these guidelines, commit messages can be edited in sublime.
1. `git config --global core.editor "subl -w"`
2. The next time you run `git commit`, navigate to `Preferences > Settings - Syntax Specific` and add `"rulers": [50, 72]`.

## Contributing

Here's how to get your code into the main repository:

### If you've just joined the team:
1. Make an account on [GitHub](https://github.com).
1. Ask the App Programming Lead to add your account to the frc1678 organization.
### If it's the first time you've contributed to this repo:
1. Fork this repo.
    1. Login to GitHub and navigate to [this repo](https://github.com/frc1678/server-2018-recode).
    1. Click the 'Fork' button in the upper right hand corner.
1. Clone your forked repo.
    * `git clone https://github.com/<your_github_username>/server-2018-recode.git`
1. Add this repo as a remote.
    * `git remote add upstream https://github.com/frc1678/server-2018-recode.git`

### Anytime you want to make a change:
1. Update the master branch of your fork.
    1. `git checkout master`
    1. `git pull upstream master`
1. Create and checkout a new branch.
    * `git checkout -b <branch_name>`, where `<branch_name>` is a descriptive name for your branch. Use dashes instead of underscores in your branch name.
    * __NOTE:__ Only work on one significant change per branch.  If you have changes to make that aren't related or dependent on each other (e.g. working on two isolated features), follow these steps to make a new branch for each change.
1. Commit your work locally.
    * Try to make your commits as atomic (small) as possible.  For example, moving functions around should be different from adding features, and changes in one subsystem should be different than changes to another subsystem.
    * If your change is anything more than a few lines or small fixes, don't skip the extended description.
1. Push to your forked repo.
    * `git push origin <branch_name>`
1. Submit a pull request (PR).
    1. Log into GitHub.
    1. Go to your forked repo.
    1. Select the branch that you just pushed from the 'Branch' dropdown menu.
    1. Click 'Pull request'.
    1. Review the changes that you made.
    1. If you are happy with your changes, click 'Create pull request'.
1. Wait for your PR to be reviewed.
    * A certain number of approvals by experienced students are required for your PR to be merged.
        * Approvals include thorough testing and code review (to ensure code is efficient, easy to read, follows style guidelines, etc.).
    * If any changes are requested, someone will be assigned to your PR.  Most likely, that will be you.  It is the responsibility of the assignee to fix any changes requested.
        * To update your PR, push to the branch that the PR is from.  The PR will automatically update with your changes.
1. Merge your changes into master.
    * If there are conflicts, fix them by merging the branch you are PRing to into your branch.
    * Once there are no conflicts, write a good commit message, and click `Squash and merge`.

## Helpful Tips

### Other remotes

You can add remotes that reference another person's fork.  This allows you to look over someone's code and to test it (useful for reviewing PRs).  It also allows you to contribute to their code by PRing into branches on their repo.
* When contributing to someone else's repo, check out the branch on their repo that you want to contribute to before creating and checking out a new branch.

To add a remote, use `git remote add <name_of_person> https://github.com/<their_username>/server-2018-recode.git`.

### Sublime Text addons + configurations

Here's a list of useful addons + configurations to Sublime Text that can be useful when contributing to the server.

#### Addons

* Package Control - Allows you to install other packages
    * Installation: `CTRL+SHIFT+P`, type 'Install package control'
* [SublimeLinter](https://packagecontrol.io/packages/SublimeLinter) - Runs `pylint` on each save, shows syntax errors, and non-compliance with PEP8 style guidelines.
    * [SublimeLinter-pylint](https://packagecontrol.io/packages/SublimeLinter-pylint) must also be installed
    * To disable the highlight feature, set the highlight color to 'none'.
* [Zen Tabs](https://packagecontrol.io/packages/Zen%20Tabs) - If the configured # of tabs is exceeded, the last used one will be saved + closed automatically.  Also includes indicator if files are saved.
* [Anaconda](https://packagecontrol.io/packages/Anaconda) - Better auto-complete functionality by using files that aren't open.
    * Note: Anaconda comes with a linter, it is recommended to disable it.
* [GitGutter](https://packagecontrol.io/packages/GitGutter) - shows `git diff` by line within your file.

#### Configurations

`Preferences > Settings` opens user settings in Sublime.
* Rulers - creates vertical lines at a certain character count
    * Set to 72 and 79 to show markers for PEP8 (79 is line limit, 72 is multiple-line comment limit)
* Spell Check - set `"spell_check"` to `true`
* Tabs as spaces - PEP8 uses 4 spaces for indentation, not tabs.  To configure sublime to insert 4 spaces when you press tab, use the following settings:
    * `"tab_size": 4`
    * `"translate_tabs_to_spaces": true`
    * `"use_tab_stops": true`

### Dependencies
* python3.7
* python3.7-pip
* All packages listed in `requirements.txt`
    * (Install with `pip install -r requirements.txt`)