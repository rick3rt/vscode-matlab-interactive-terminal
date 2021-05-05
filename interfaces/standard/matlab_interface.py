# Developed by Aurelien Pommel and other contributors

# Trying to have a basic Python 2 compatibility
from __future__ import print_function

try:
    input = raw_input
except NameError:
    pass

import os

global import_fail
try:  # Check if the Matlab Engine is installed
    import matlab.engine
    from matlab.engine import RejectedExecutionError as MatlabTerminated
except ImportError:
    print("Matlab Engine for Python cannot be detected. Please install it for the extension to work")
    import_fail = True
else:
    import_fail = False


class MatlabInterface:
    global import_fail

    def __init__(self, attach_existing=True):
        # OS checks related work
        if os.name == 'nt':
            self.cls_str = 'cls'
        else:
            self.cls_str = 'clear'
        self.clear()
        if not import_fail:
            if attach_existing:
                print("Attaching to running Matlab...")
                msessions = matlab.engine.find_matlab()
                if msessions:
                    print("Session found!")
                    self.eng = matlab.engine.connect_matlab(msessions[0])
                else:
                    print("No session found, starting Matlab...")
                    self.eng = matlab.engine.start_matlab()
            else:
                print("Starting Matlab...")
                self.eng = matlab.engine.start_matlab()
        else:
            print("Could not start Matlab")

    def clear(self):
        os.system(self.cls_str)

    def run_script(self, script_path):
        if not import_fail:
            try:
                print("Running: \"{}\"".format(script_path))
                self.eng.run(script_path, nargout=0)
            except MatlabTerminated:
                print("Matlab terminated. Restarting the engine...")
                self.eng = matlab.engine.start_matlab()
                print("Matlab restarted")
            except:  # The other exceptions are handled by Matlab
                pass

    def run_selection(self, temp_path):
        if not import_fail:
            f = open(temp_path, 'r')
            print("Running:")
            try:  # Print the content of the selection before running it, encoding issues can happen
                for line in f:
                    print(line, end='')
            except UnicodeDecodeError:
                print("current selection")
            print('\n')
            f.close()
            try:
                self.eng.run(temp_path, nargout=0)
            except MatlabTerminated:
                print("Matlab terminated. Restarting the engine...")
                self.eng = matlab.engine.start_matlab()
                print("Matlab restarted")
            except:  # The other exceptions are handled by Matlab
                pass
            finally:
                try:
                    os.remove(temp_path)
                    os.rmdir(os.path.dirname(temp_path))
                except OSError:
                    pass

    def interactive_loop(self):
        loop = True  # Looping allows for an interactive terminal
        while loop and not import_fail:
            print('>> ', end='')
            command = input()
            if command == "exit" or command == "exit()":  # Keywords to leave the engine
                loop = False
            elif command == "clc":  # matlab terminal clearing must be reimplemented
                self.clear()
            else:
                try:
                    self.eng.eval(command, nargout=0)  # Feed the instructions to Matlab eval
                except MatlabTerminated:
                    print("Matlab terminated. Restarting the engine...")
                    self.eng = matlab.engine.start_matlab()
                    print("Matlab restarted")
                except:  # The other exceptions are handled by Matlab
                    pass
        if not import_fail:
            self.eng.quit()
