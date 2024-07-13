import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from base import Base

class PodExposer(Base):
    """
    This class inherits from Base class.
    Its purpose is to access the Pod's name via an environment variable and return it.
    """

    def __init__(self):
        super().__init__()
        #self.add_arguments()       # For bonus task

    def add_arguments(self):    #Bonues task
        self.parser.add_argument('-p', '--podname')

    def prepare(self):
        pass

    def run(self):
        #Check if argument wasd given, use it if yes
        if hasattr(self.args, "podname") and self.args.podname:
            pod_name = self.args.podname
            os.environ['POD_NAME'] = pod_name
        else:
            pod_name = os.environ.get("POD_NAME")
        if pod_name is not None:
            print(pod_name)
        else:
            raise Exception("Failed to get the runner pod's name.")

    def on_exception(self, e):
        print ("No POD name!!!")
        raise Exception from e

    def on_end(self):
        pass

if __name__ == '__main__':
    run = PodExposer()
    sys.exit(run.execute())
