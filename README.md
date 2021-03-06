A binding for Sublime Text to the Crystal auto completion tool
by TechMagister (https://github.com/TechMagister/cracker).

![screenshot1](https://raw.githubusercontent.com/TechMagister/CrystalAutoComplete/master/screenshots/screenshot1.png)

Features
========

    * Auto complete (invoked automatically on Crystal files).

Status
======

Pull requests for fixes and new features are very welcome.

I have only tested this on Linux. It may work on Mac.

Requirements
============

1) Install the Crystal syntax highlighting package from Package Control:
   [crystal-lang/sublime-crystal](https://github.com/crystal-lang/sublime-crystal)

2) Clone and build the auto completion tool cracker:
    https://github.com/TechMagister/cracker

3) Configure the plugin to be able to find the cracker executable.
   Open menu

    Preferences -> Package settings -> CrystalAutoComplete -> Settings - User

    and edit the settings file using below as a template:


    // Copy this and place into your Packages/User directory.
    {
        // The full path to the cracker binary. If cracker is already
        // in your system path, then this default will be fine.
        "cracker": "cracker",
    }

