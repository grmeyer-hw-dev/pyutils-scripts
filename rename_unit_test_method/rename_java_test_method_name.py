import os
import re


class Stats:
    file_updated = 0
    method_name_updated = 0


def rename_test_method_recursive(directory: str, skip_apply_changes: bool = False):
    # Set True on skip_apply_changes to skip apply changes to the file, it'll only display the changes
    stats = Stats()
    # List all files from the target directory
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            # evaluated files that ends with Test.java
            file_name_lowercase = file_name.lower()
            if file_name_lowercase.endswith("test.java") or file_name_lowercase.endswith("testcase.java"):
                # get the file path
                file_path = os.path.join(root, file_name)

                # evaluate file
                evaluate_method_test_name(file_path, stats, skip_apply_changes)

    print('Summary, file affected: {}, method renamed: {}'.format(stats.file_updated, stats.method_name_updated))


def evaluate_method_test_name(file_path, stats, skip_apply_changes=False):
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    # Read the file contents
    with open(file_path, 'r') as file:
        content = file.read()

    # Find method annotated with @Test
    # (@Test\n.*void|@Test\n.*@Override\n.*void|@ParameterizedTest\n.*\n\s+void)\s(?!(test|should))(\w+)
    # (@Test\n.*void|@ParameterizedTest\n.*void|@ParameterizedTest\n.*\n\s+void)\s(?!(test|should))(\w+)
    # @Test\n.*void|@ParameterizedTest\n.*void|@ParameterizedTest\n.*\n\s+void|@ParameterizedTest\n.*\n\s+public\s+void
    # "(@Test\n.*void\s+)(\w+\()"
    pattern = re.compile(
        "(@Test\n.*void|@ParameterizedTest\n.*void|@ParameterizedTest\n.*\n\s+void|@ParameterizedTest\n.*\n\s+public\s+void)\s+(\w+\()")

    new_content = content
    should_display_file_name = True
    is_file_affected = False
    for match in re.finditer(pattern, content):

        method_name = match.group(2)

        new_method_name = method_name
        if not method_name.lower().startswith("test"):
            if not method_name.lower().startswith("should"):
                new_method_name = append_prefix(new_method_name, "test")
        else:
            new_method_name = reformat(method_name, "test")

        if method_name.find("_"):
            new_method_name = replace_underline(new_method_name)

        if new_method_name != method_name:
            stats.method_name_updated = stats.method_name_updated + 1
            if not is_file_affected:
                is_file_affected = True
                print('file_name: {}'.format(file_path))

            print('original_method_name: {}, new_method_name: {}'.format(method_name, new_method_name))
            # replace method to the new one from file's content
            if not skip_apply_changes:
                new_content = new_content.replace('void {}'.format(method_name), 'void {}'.format(new_method_name))

    if not skip_apply_changes and is_file_affected:
        stats.file_updated = stats.file_updated + 1
        with open(file_path, 'w') as file:
            file.write(new_content)


def capitalize(value):
    # capitalize only the first letter
    if value == "":
        return value

    if len(value) == 1:
        return value[0].upper()

    return value[0].upper() + value[1:]


def reformat(name, prefix_name):
    value = name.replace("test", "")
    return append_prefix(value, prefix_name)


def append_prefix(name, prefix_name):
    # append prefix test to the method name
    capitalized_name = capitalize(name)
    return '{}{}'.format(prefix_name, capitalized_name)


def replace_underline(original_name):
    # Splits value by _ and replace by prefix With
    values = original_name.split("_")
    new_name = ""
    is_fist_part = True
    for value in values:
        if value == "":
            continue
        if not is_fist_part:
            captalized_value = capitalize(value)
            join_value = "With"
            if value.lower().startswith("with"):
                join_value = ""

            new_name = '{}{}{}'.format(new_name, join_value, captalized_value, )
        else:
            is_fist_part = False
            new_name = value

    return new_name


# only print the changes
# rename_test_method_recursive(directory='target_directory_path', skip_apply_changes=True)

# Apply the change to the files
rename_test_method_recursive(directory='target_directory_path')
