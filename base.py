import argparse

class Base:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.args = None

    def parse_arguments(self):
        self.add_arguments()
        self.args = self.parser.parse_known_args()[0]

    def add_arguments(self):
        pass

    def prepare(self):
        pass

    def run(self):
        pass

    def on_exception(self, e):
        raise

    def on_end(self):
        pass

    def execute(self):
        self.parse_arguments()
        try:
            self.prepare()
            self.run()
        except Exception as e:
            print ("Exception on created")
            self.on_exception(e)
        finally:
            self.on_end()
