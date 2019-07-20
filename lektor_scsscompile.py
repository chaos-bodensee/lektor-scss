# -*- coding: utf-8 -*-
import os
#import errno

import sass
import re
from lektor.pluginsystem import Plugin
from termcolor import colored
import threading
import time

COMPILE_FLAG = "scsscompile"

class SCSScompilePlugin(Plugin):
    name = u'Lektor SCSScompile'
    description = u'SASS compiler for Lektor, thats based on libsass.'

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        config = self.get_config()
        self.source_dir = config.get('source_dir', 'asset_sources/scss/')
        self.output_dir = config.get('output_dir', 'assets/css/')
        self.output_style = config.get('output_style', 'compressed')
        self.source_comments = config.get('source_comments', 'False')
        self.precision = config.get('precision', '5')
        self.name_prefix = config.get('name_prefix', '')
        self.watcher = None
        self.run_watcher = False

    def is_enabled(self, build_flags) -> bool:
        return bool(build_flags.get(COMPILE_FLAG))

    def find_dependencies(self, target) -> list:
        dependencies = [target]
        with open(target, 'r') as f:
            data = f.read()
            imports = re.findall(r'@import\s+((?:[\'|\"]\S+[\'|\"]\s*(?:,\s*(?:\/\/\s*|)|;))+)', data)
            for files in imports:
                files = re.sub('[\'\"\n\r;]', '', files)
                
                # find correct filename and add to watchlist (recursive so dependencies of dependencies get added aswell)
                for file in files.split(","):
                    file = file.strip()
                    if file.endswith('.css'):
                        continue
                    
                    basepath = os.path.dirname(target)
                    filepath = os.path.dirname(file)
                    basename = os.path.basename(file)
                    filenames = [basename, '_' + basename, basename + '.scss', '_' + basename + '.scss']

                    for filename in filenames:
                        path = os.path.join(basepath, filepath, filename)
                        if os.path.isfile(path):
                            dependencies += self.find_dependencies(path)
        return dependencies

    def compile_file(self, target, output, dependencies):
        """
        Compiles the target scss file.
        """
        filename = os.path.splitext(os.path.basename(target))[0]
        if not filename.endswith(self.name_prefix):
            filename += self.name_prefix
        filename += '.css'
        output_file = os.path.join(output, filename)

        # check if dependency changed and rebuild if it did
        rebuild = False
        for dependency in dependencies:
            if ( not os.path.isfile(output_file) or os.path.getmtime(dependency) > os.path.getmtime(output_file)):
                rebuild = True
                break
        if not rebuild:
            return

        result = sass.compile(
                filename=target,
                output_style=self.output_style,
                precision=int(self.precision),
                source_comments=(self.source_comments.lower()=='true')
            )
        with open(output_file, 'w') as fw:
            fw.write(result)
        
        print(colored('css', 'green'), self.source_dir + os.path.basename(target), '\u27a1', self.output_dir + filename)
        

    def find_files(self, destination):
        """
        Finds all scss files in the given destination. (ignore files starting with _)
        """
        for root, dirs, files in os.walk(destination):
            for f in files:
                if (f.endswith('.scss') or f.endswith('.sass')) and not f.startswith('_'):
                    yield os.path.join(root, f)            

    def thread(self, output, watch_files):
        while True:
            if not self.run_watcher:
                self.watcher = None
                break
            for filename, dependencies in watch_files:
                self.compile_file(filename, output, dependencies)
            time.sleep(1)

    def on_server_spawn(self, **extra):
        self.run_watcher  = True

    def on_server_stop(self, **extra):
        if self.watcher is not None:
            self.run_watcher = False
            print('stopped')
        
  
    def on_before_build_all(self, builder, **extra):
        try: # lektor 3+
            is_enabled = self.is_enabled(builder.extra_flags)
        except AttributeError: # lektor 2+
            is_enabled = self.is_enabled(builder.build_flags)

        # only run when server runs
        if not is_enabled or self.watcher:
            return

        root_scss = os.path.join(self.env.root_path, self.source_dir )
        output = os.path.join(self.env.root_path, self.output_dir )
        config_file = os.path.join(self.env.root_path, 'configs/scsscompile.ini')

        # output path has to exist
        os.makedirs(output, exist_ok=True)

        dependencies = []
        if ( os.path.isfile(config_file)):
            dependencies.append(config_file)

        if self.run_watcher:
            watch_files = []
            for filename in self.find_files(root_scss):
                dependencies += self.find_dependencies(filename)
                watch_files.append([filename, dependencies])
            self.watcher = threading.Thread(target=self.thread, args=(output, watch_files))
            self.watcher.start()
        else:
            for filename in self.find_files(root_scss):
                # get dependencies by searching imports in target files
                dependencies += self.find_dependencies(filename)
                self.compile_file(filename, output, dependencies)
