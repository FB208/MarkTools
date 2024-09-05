import pkg_resources
import subprocess
import sys
packages = [dist.project_name for dist in pkg_resources.working_set]
subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y'] + packages)