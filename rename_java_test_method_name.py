import os
import re

class Stats:
    file_updated = 0
    method_name_updated = 0

def rename_test_method_recursive(directory):
    target_file_name_suffix = "test.java"
    stats = Stats()
    # List all files from the target directory
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            # evaluated files that ends with Test.java
            if file_name.lower().endswith(target_file_name_suffix):
                # get the file path
                file_path = os.path.join(root, file_name)

                # evaluate file
                evaluate_method_test_name(file_path, stats)

    print('Summary, file affected: {}, method renamed: {}'.format(stats.file_updated, stats.method_name_updated))

def evaluate_method_test_name(file_path, stats):
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    # Read the file contents
    with open(file_path, 'r') as file:
        content = file.read()

    # Find methos annotated with @Test
    pattern = re.compile("(@Test\n.*void\s+)(\w+\()")

    new_content = content
    should_display_file_name = True
    is_file_affected = False
    for match in re.finditer(pattern, content):

        method_name = match.group(2)

        new_method_name = method_name
        if not method_name.lower().startswith("test"):
            if not method_name.lower().startswith("should"):
                new_method_name = add_prefix_test(new_method_name)

        if  method_name.find("_"):
            new_method_name = replace_underline(new_method_name)

        if new_method_name != method_name:
            stats.method_name_updated = stats.method_name_updated + 1
            if not is_file_affected:
                is_file_affected = True
                print('file_name: {}'.format(file_path))

            print('original_method_name: {}, new_method_name: {}'.format(method_name, new_method_name))
            # replace method to the new one from file's content
            new_content = new_content.replace('void {}'.format(method_name), 'void {}'.format(new_method_name))

    if (is_file_affected):
        stats.file_updated = stats.file_updated + 1
        with open(file_path, 'w') as file:
            file.write(new_content)

def capitalize(value):
    # capitalize only the fisrt letter
    if value == "":
        return value

    if len(value) == 1:
        return value[0].upper()

    return value[0].upper() + value[1:]


def add_prefix_test(name):
    # append prefix test to the method name
    captalize = name[0].upper() + name[1:]
    return 'test{}'.format(captalize)

def replace_underline(original_name):
    # Splits value by _ and replace by prefix With
    values = original_name.split("_")

    is_fist_part = True
    for value in values:
        if value == "":
            continue
        if not is_fist_part :
            captalized_value = capitalize(value)
            join_value = "With"
            if value.lower().startswith("with"):
                join_value = ""

            new_name = '{}{}{}'.format(new_name, join_value, captalized_value, )
        else:
            is_fist_part = False
            new_name = value

    return new_name

# Usage example
directory = '../target_folder'

rename_test_method_recursive(directory)