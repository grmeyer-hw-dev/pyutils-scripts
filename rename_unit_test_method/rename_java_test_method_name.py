# Search and replace test files ends with suffix "test.java", "testcase.java"
# names methods annotated with @Test and @ParameterizedTest
import os
import re


class Stats:
    file_updated = 0
    method_name_updated = 0
    file_ignored = 0


def rename_test_method_recursive(directory: str, ignored_files=None, skip_apply_changes: bool = False):
    # Set True on skip_apply_changes to skip apply changes to the file, it'll only display the changes
    if ignored_files is None:
        ignored_files = {}
    stats = Stats()
    lowercase_ignored_files = list(map(lambda x: x.lower(), ignored_files))
    # List all files from the target directory
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            # evaluated files that ends with Test.java
            file_name_lowercase = file_name.lower()
            if file_name_lowercase.endswith(("test.java", "testcase.java")):
                if file_name_lowercase in lowercase_ignored_files:
                    # skip ignored file
                    # print('skip file: {}'.format(file_name))
                    stats.file_ignored = stats.file_ignored + 1
                    continue
                # get the file path
                file_path = os.path.join(root, file_name)

                # evaluate file
                evaluate_method_test_name(file_path, stats, skip_apply_changes)

    if skip_apply_changes:
        print('\nSummary:'
              '\n\ttotal file(s) will be affected: {},'
              '\n\ttotal method(s) will be renamed: {},'
              '\n\ttotal file(s) ignored: {}'
              .format(stats.file_updated, stats.method_name_updated, stats.file_ignored))
    else:
        print('\nSummary,'
              '\n\ttotal file(s) affected: {},'
              '\n\ttotal method(s) renamed: {},'
              '\n\ttotal file(s) ignored: {}'
              .format(stats.file_updated, stats.method_name_updated, stats.file_ignored))


def evaluate_method_test_name(file_path, stats, skip_apply_changes=False):
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    # Read the file contents
    with open(file_path, 'r') as file:
        content = file.read()

    # Find method name that is annotated with @Test or @ParameterizedTest
    target_method_prefix = r"@Test\n.*void" \
                           r"|@Test\n\s+@Override\n.*void" \
                           r"|@ParameterizedTest\n.*void" \
                           r"|@ParameterizedTest\n.*\n\s+void" \
                           r"|@ParameterizedTest\n.*\n\s+public\s+void" \
                           r"|@ParameterizedTest\n\s+\@ValueSource\(strings = \{(\n.*){2,4}\s+\}\)\n\s+void" \
                           r"|@ParameterizedTest\n\s+\@CsvSource\((\n\s+value|value|)[\w\s=\{\",\.]+\}\)\n\s+void"
    target_method_name = r"?P<method_name>\w+\("
    regular_expression = r"({})\s+({})".format(target_method_prefix, target_method_name)

    pattern = re.compile(regular_expression)

    new_content = content
    is_file_affected = False
    for match in re.finditer(pattern, content):

        method_name = match.group("method_name")
        if method_name == "" or method_name is None:
            print('!!!! review regex, file_name: {}'.format(file_path))
            continue

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
                stats.file_updated = stats.file_updated + 1
                print('file_name: {}'.format(file_path))

            print('  original_method_name: {}, new_method_name: {}'.format(method_name, new_method_name))
            # replace method to the new one from file's content
            if not skip_apply_changes:
                new_content = new_content.replace('void {}'.format(method_name), 'void {}'.format(new_method_name))

    if not skip_apply_changes and is_file_affected:
        with open(file_path, 'w') as file:
            file.write(new_content)


def capitalize(value):
    # capitalize only the first letter
    if value == "":
        return value

    if len(value) == 1:
        return value[0].upper()

    return value[0].upper() + value[1:]


def reformat(name, prefix):
    value = name[len(prefix):]
    return append_prefix(value, prefix)


def append_prefix(name, prefix):
    # append prefix test to the method name
    capitalized_name = capitalize(name)
    return '{}{}'.format(prefix, capitalized_name)


def replace_underline(original_name):
    # Splits value by _ and replace by prefix With
    values = original_name.split("_")
    new_name = ""
    join_value = ""
    is_fist_part = True
    for value in values:
        if value == "":
            continue
        if not is_fist_part:
            formatted_name = capitalize(value)
            new_name = '{}{}{}'.format(new_name, join_value, formatted_name)
        else:
            is_fist_part = False
            new_name = value

    return new_name


# only print the changes
# rename_test_method_recursive(directory='target_directory_path', skip_apply_changes=True)

# Define the ignored file name. like:   ignored_files =  ["ClassANameTest.java", "ClassBNameTest.java"]
skip_files = [
]
# Apply the change to the files
rename_test_method_recursive(directory='target_directory_path', ignored_files=skip_files, skip_apply_changes=True)

# only print the changes
# rename_test_method_recursive(directory='target_directory_path', skip_apply_changes=True)
