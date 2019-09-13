 SCSS compiler for lektor
=============================
[![PyPI version](https://badge.fury.io/py/lektor-scss.svg)](https://badge.fury.io/py/lektor-scss)
 [![Downloads](https://pepy.tech/badge/lektor-scss)](https://pepy.tech/project/lektor-scss) 

SCSS compiler for [Lektor](https://getlektor.com) that compiles css from sass.

 How does it acutually work?
----------------------------
 + It uses [libsass](https://github.com/sass/libsass-python) 
 + It looks for ``.scss`` and ``.sass`` files *(ignores part files that begin with a underscore e.g. '_testfile.scss'), compiling them as part of the build process.*
 + It only rebuilds the css when it's needed (file changed, a file it imports changed or the config changed).
 + When starting the the development server it watchs the files for changes in the background and rebuilds them when needed.

 Installation
-------------
You can install the plugin with Lektor's installer::
```bash
lektor plugins add lektor-scss
```

Or by hand, adding the plugin to the packages section in your lektorproject file::
```ini
[packages]
lektor-scss = 1.3.3
```
 Usage
------
To enable scsscompile, pass the ``scss`` flag when starting the development
server or when running a build:
```bash
# build and compile css from scss
lektor build -f scss

# edit site with new generated css
lektor server -f scss
```

 Configuration
-------------
The Plugin has the following settings you can adjust to your needs:

|parameter      |default value      |description                                                                                       |
|---------------|-------------------|--------------------------------------------------------------------------------------------------|
|source_dir     |assets/scss/       | the directory in which the plugin searchs for sass files (subdirectories are included)           |
|output_dir     |assets/css/        | the directory the compiled css files get place at                                                |
|output_style   |compressed         | coding style of the compiled result. choose one of: 'nested', 'expanded', 'compact', 'compressed'|
|source_comments|False              | whether to add comments about source lines                                                       |
|precision      |5                  | precision for numbers                                                                            |

An example file with the default config can be found at ``configs/scsscompile.ini``

 Developement
-------------
To test and/or develope this plugin in your running lektor installation, simply put it in the ``packages/`` Folder and have a look at the [Lektor Doku](https://www.getlektor.com/docs/plugins/dev/)

<!-- How to add to pypi: https://packaging.python.org/tutorials/packaging-projects/ -->
