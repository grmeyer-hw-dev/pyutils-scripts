# Search and replace test files ends with suffix "test.java", "testcase.java"
# replace assertEquals to assertThat
import os
import re

IGNORE_FLOAT_ASSERTION_EQUALS = ['DELTA', 'RuleExecutor.VALID_EXECUTION']
JAVA_IMPORT = '\nimport'
COMMA = ','
EMPTY_STRING = ' '
COMMA_WILDCARD = '<comma>'

IMPORT_JUNIT_4_ASSERT = 'import org.junit.Assert;'
IMPORT_JUNIT_4_ASSERT_EQUALS = 'import static org.junit.Assert.assertEquals;'
IMPORT_JUNIT_4_ASSERT_THAT = 'import static org.junit.Assert.assertThat;'
IMPORT_JUNIT_4_ASSERT_NOT_NULL = 'import static org.junit.Assert.assertNotNull;'

IMPORT_JUNIT_JUPITER_ASSERT_EQUALS = 'import static org.junit.jupiter.api.Assertions.assertEquals;'
IMPORT_ASSERT_THAT = 'import static org.hamcrest.MatcherAssert.assertThat;'

IMPORT_CORE_MATCHERS_EQUAL_TO = 'import static org.hamcrest.CoreMatchers.equalTo;'
IMPORT_CORE_MATCHERS_IS = 'import static org.hamcrest.CoreMatchers.is;'
IMPORT_CORE_MATCHERS_NULL_VALUE = 'import static org.hamcrest.CoreMatchers.nullValue;'
IMPORT_HAMCREST_MATCHERS_IS = 'import static org.hamcrest.core.Is.is;'

IMPORT_MATCHERS_IS = 'import static org.hamcrest.Matchers.is;'
IMPORT_MATCHERS_EQUAL_TO = 'import static org.hamcrest.Matchers.equalTo;'
IMPORT_MATCHERS_NULL_VALUE = 'import static org.hamcrest.Matchers.nullValue;'
IMPORT_MATCHERS_NOT_NULL_VALUE = 'import static org.hamcrest.Matchers.notNullValue;'

METHOD_MATCHERS_IS = 'is'
METHOD_MATCHERS_NULL_VALUE = 'nullValue'
METHOD_MATCHERS_HAS_SIZE = 'hasSize'
METHOD_MATCHERS_ASSERT_THAT = 'assertThat'


class Stats:
    file_updated = 0
    method_name_updated = 0
    file_ignored = []
    file_ignored_matchers_equal_to = []
    assert_matcher_types = {}

    def total_ignored(self):
        return self.total_ignored_manually() + self.total_ignored_by_using_hamcrest_equal_to()

    def total_ignored_manually(self):
        return len(self.file_ignored)

    def total_ignored_by_using_hamcrest_equal_to(self):
        return len(self.file_ignored_matchers_equal_to)


def replace_unit_test_assertions(directory: str, ignored_files=None, skip_apply_changes: bool = False):
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
            if file_name_lowercase.endswith(('test.java', 'testcase.java')):
                # Ignore ITTest
                # if file_name_lowercase.endswith("ittest.java"):
                #     continue

                if file_name_lowercase in lowercase_ignored_files:
                    # skip ignored file
                    stats.file_ignored.append(file_name)
                    continue

                # get the file path
                file_path = os.path.join(root, file_name)

                # evaluate file
                evaluate_file(file_path, stats, skip_apply_changes)

    if skip_apply_changes:
        print('\n####Summary:'
              '\n\t- total file(s) will be affected: {},'
              '\n\t- total matcher(s): {},'
              '\n\t- total file(s) ignored: {}'
              '\n\t\t- ignored manually: {},'
              '\n\t\t- ignored by using `org.hamcrest.Matchers.equalTo`: {},'
              '\n\t- files ignored manually : [{}],'
              '\n\t- files ignored by using `org.hamcrest.Matchers.equalTo`: [{}]'
              .format(stats.file_updated,
                      stats.assert_matcher_types,
                      stats.total_ignored(),
                      stats.total_ignored_manually(),
                      stats.total_ignored_by_using_hamcrest_equal_to(),
                      '\n\t\t- ' + (',\n\t\t- '.join(stats.file_ignored)) + '\n\t',
                      '\n\t\t- ' + (',\n\t\t- '.join(stats.file_ignored_matchers_equal_to)) + '\n\t'))
    else:
        print('\n####Summary,'
              '\n\t- total file(s) affected: `{}`,'
              '\n\t- total matcher(s): `{}`,'
              '\n\t- total file(s) ignored: `{}`'
              '\n\t\t- ignored manually: `{}`,'
              '\n\t\t- ignored by using `org.hamcrest.Matchers.equalTo`: `{}`,'
              '\n\t- files ignored manually : [{}],'
              '\n\t- files ignored by using `org.hamcrest.Matchers.equalTo`: [{}]'
              .format(stats.file_updated,
                      stats.assert_matcher_types,
                      stats.total_ignored(),
                      stats.total_ignored_manually(),
                      stats.total_ignored_by_using_hamcrest_equal_to(),
                      '\n\t\t- ' + (',\n\t\t- '.join(stats.file_ignored)) + '\n\t',
                      '\n\t\t- ' + (',\n\t\t- '.join(stats.file_ignored_matchers_equal_to)) + '\n\t'))


def evaluate_file(file_path, stats, skip_apply_changes=False):
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    # Read the file contents
    with open(file_path, 'r') as file:
        content = file.read()

    # Process the file contents
    is_file_affected, new_content = process_content(content, file_path, skip_apply_changes, stats)

    # Update the file contents
    if not skip_apply_changes and is_file_affected:
        with open(file_path, 'w') as file:
            file.write(new_content)


def process_content(content, file_path, skip_apply_changes, stats):
    new_content = content
    is_file_affected = False
    # if IMPORT_JUNIT_JUPITER_ASSERT_EQUALS in content:
    #     # Skip equals from import static org.junit.Assert.assertEquals\
    #     file_path, filename = os.path.split(file_path)
    #     stats.file_ignored_matchers_equal_to.append(filename)
    #     return is_file_affected, new_content

    add_imports = {IMPORT_ASSERT_THAT}
    remove_imports = {IMPORT_JUNIT_4_ASSERT_THAT}

    # Find assert equals target
    for match in find_assert_equals(content):
        assert_equals = match.group("assert_equals")
        assert_equals_params = match.group("assert_equals_params")

        if should_skip_assert_equals(assert_equals_params):
            continue

        if not is_file_affected:
            is_file_affected = True
            stats.file_updated = stats.file_updated + 1
            print('----------------------------\nfile_name: {}'.format(file_path))

        assert_equals_params_wildcard = replace_comma_to_wildcard(assert_equals_params)
        assert_that_template = build_assert_that(add_imports, remove_imports, assert_equals_params_wildcard, stats)
        assert_that = replace_wildcard_to_comma(assert_that_template)

        print("assertEquals: {}".format(assert_equals))
        print("assertThat: {}\n".format(assert_that))

        if not skip_apply_changes:
            new_content = new_content.replace(assert_equals, assert_that)

    if is_file_affected:
        # The find regex (replace_unit_test_assertions.replace_java_unit_test_assertions.find_assert_equals)
        # is not capturing the prefix `Assert.assertEquals` in few scenarios.
        new_content = new_content.replace(' Assert.assertThat(', ' assertThat(')
        # Replace imports
        new_content = append_java_imports(new_content, add_imports)
        new_content = remove_assert_imports(new_content, remove_imports)

    return is_file_affected, new_content


def should_skip_assert_equals(assert_equals_params):
    # skip assertEquals(float, float, float)
    for ignore_item in IGNORE_FLOAT_ASSERTION_EQUALS:
        if ignore_item in assert_equals_params:
            return True
    return False


def find_assert_equals(content):
    assertion_equals_regular_expression = r'(?P<assert_equals>(' \
                                          r'junit\.framework\.Assert\.assertEquals' \
                                          r'|Assertions\.assertEquals' \
                                          r'|Assert\.assertEquals' \
                                          r'|assertEquals' \
                                          r')\((?P<assert_equals_params>.*?)\);)\n'
    pattern = re.compile(assertion_equals_regular_expression)
    return re.finditer(pattern, content)


def append_java_imports(new_content, assert_imports):
    # Remove duplicate imports
    filtered_imports = remove_duplicate_imports(assert_imports, new_content)

    # Preparer imports statements
    if filtered_imports:
        new_imports = '\n'.join(filtered_imports)

        # Append assert imports
        new_content = append_java_assert_imports(new_content, new_imports)

    return new_content


def append_java_assert_imports(new_content, new_imports):
    # Find the last import statement
    last_import_index = new_content.rfind(JAVA_IMPORT)
    # Find the position to insert the new imports
    next_line_content = new_content.find('\n', last_import_index)
    new_content = new_content[:next_line_content] + '\n' + new_imports + new_content[next_line_content:]
    return new_content


def remove_assert_imports(new_content, remove_imports):
    for remove_import in remove_imports:
        import_value = "{}\n" \
            .format(remove_import) \
            .rstrip('\n')
        if import_value in new_content:
            new_content = new_content.replace(import_value, "")

    return new_content


def remove_duplicate_imports(assert_imports, new_content):
    filtered_imports = []
    # Remove duplicate imports
    for import_statement in assert_imports:
        if import_statement not in new_content:
            filtered_imports.append(import_statement)
    return filtered_imports


def build_assert_that(add_imports, remove_imports, update_params, stats):
    params = update_params.split(",")
    params_length = len(params)

    if params_length < 2:
        return None

    message = None
    if params_length == 2:
        object_expected = params[0]
        object_actual = params[1]
        object_expected_actual = remove_prefix(object_expected, EMPTY_STRING)
        update_object_actual = remove_prefix(object_actual, EMPTY_STRING)
        if ")" in update_object_actual and "(" not in update_object_actual:
            # Handle assertion inside lambda
            update_object_actual = update_object_actual.replace(")", "")
            object_expected_actual = object_expected_actual + ")"
    elif params_length == 3:
        message = params[0]
        object_expected = params[1]
        object_actual = params[2]
        update_object_actual = remove_prefix(object_actual, EMPTY_STRING)
        object_expected_actual = remove_prefix(object_expected, EMPTY_STRING)

        message = remove_prefix(message, EMPTY_STRING)

    assert_that = format_assert_that(add_imports, remove_imports, update_object_actual, object_expected_actual,
                                     stats, message)

    return assert_that


def replace_comma_to_wildcard(assert_equals_params):
    update_params = mask_string_with_comma(assert_equals_params, COMMA_WILDCARD)
    update_params = mask_function_parameter_separator(update_params, COMMA_WILDCARD)
    return update_params


def replace_wildcard_to_comma(text):
    return text.replace(COMMA_WILDCARD, COMMA)


def mask_string_with_comma(text, wildcard):
    # Replace comma (,) from text string by wildcard e.g. "00,44", results: "00<<comma>>44"
    string_content = r'[\w\s\d\<\+\>\-\|\@\:\{\}\;\!\=\~\^\?\$\.\%\#\&\_\'\\\(\[\)\]\*,]+'
    regular_expression = r'^"({})(,{}){}\"'.format(string_content, string_content, "{1,3}")
    updated_text = text
    pattern = re.compile(regular_expression)
    for match in re.finditer(pattern, text):
        original_value = match.group(0)
        updated_value = original_value.replace(",", wildcard)
        updated_text = updated_text.replace(original_value, updated_value)

    return updated_text.replace(",\"", "{}\"".format(wildcard))


def mask_function_parameter_separator(text, tag):
    # Replace comma (,) from function's arguments by wildcard e.g. "calc(10, 44)", results: "calc(10<<comma>> 44)"
    regular_expression = r'(?P<function_params>\(.*?\)|,\s\w+\))'
    updated_text = text
    pattern = re.compile(regular_expression)
    for match in re.finditer(pattern, text):
        params = match.group("function_params")
        if params != "" and params is not None:
            updated = params.replace(",", tag)
            updated_text = updated_text.replace(params, updated)

    return updated_text


def format_assert_that(add_imports, remove_imports, object_actual, object_expected, stats, message=None):
    update_object_actual = object_actual
    update_object_expected = object_expected
    if object_expected == "null":
        # Append Matcher.nullValue to assert target value
        add_imports.add(IMPORT_MATCHERS_NULL_VALUE)
        remove_imports.add(IMPORT_CORE_MATCHERS_NULL_VALUE)
        assert_matcher = METHOD_MATCHERS_NULL_VALUE
        update_object_expected = ""
    else:
        # Append Matcher.is to assert target value
        assert_matcher = METHOD_MATCHERS_IS
        add_imports.add(IMPORT_MATCHERS_IS)
        remove_imports.add(IMPORT_CORE_MATCHERS_IS)
        remove_imports.add(IMPORT_HAMCREST_MATCHERS_IS)

    # Track stats
    if assert_matcher not in stats.assert_matcher_types:
        stats.assert_matcher_types[assert_matcher] = 0

    stats.assert_matcher_types[assert_matcher] += 1

    if message is not None:
        return "{}({}, {}, {}({}));" \
            .format(METHOD_MATCHERS_ASSERT_THAT, message, update_object_actual, assert_matcher, update_object_expected)
    # build assert statement
    return "{}({}, {}({}));" \
        .format(METHOD_MATCHERS_ASSERT_THAT, update_object_actual, assert_matcher, update_object_expected)


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


skip_files = {
}
# Apply the change to the files
replace_unit_test_assertions(directory='<path>',
                             ignored_files=skip_files,
                             skip_apply_changes=False)

