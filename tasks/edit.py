import os
import re


def contents_of(directory, relative_path):
    class EditedFile(object):
        def __init__(self, file_path):
            self.file_path = file_path
            self.contents = None

        def __enter__(self):
            with open(self.file_path, 'r') as input_file:
                self.contents = input_file.read()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            with open(self.file_path, 'w') as output_file:
                output_file.write(self.contents)

        def edit(self, pattern, replacement, flags=0):
            for match in re.finditer(pattern, self.contents, flags=flags):
                self.contents = self.contents.replace(match.group(0), replacement)

    return EditedFile(os.path.join(directory, relative_path))
