import os
import re
from replace_unit_test_assertions.replace_java_unit_test_assertions \
    import mask_string_with_comma, find_assert_equals, mask_function_parameter_separator


def test_mask_function_parameter_separator_when_there_are_two_parameters():
    result = mask_function_parameter_separator('"0000000000", value.substring(20, 30)', '<<comma>>')
    assert result == '"0000000000", value.substring(20<<comma>> 30)'


def test_mask_function_parameter_separator_when_there_are_three_parameters():
    result = mask_function_parameter_separator('"0000000000", value.validate(20, 30, 40)', '<<comma>>')
    assert result == '"0000000000", value.validate(20<<comma>> 30<<comma>> 40)'


def test_mask_string_with_comma_when_there_are_multiple_commas():
    result = mask_string_with_comma('"999 - 111 SomeStreet St, City,", class.list(0).method()', '<<comma>>')
    assert result == '"999 - 111 SomeStreet St<<comma>> City<<comma>>", class.list(0).method()'


def test_mask_string_with_comma_when_there_double_value():
    result = mask_string_with_comma('"00,99", class.list(0).method()', '<<comma>>')
    assert result == '"00<<comma>>99", class.list(0).method()'


def test_mask_string_with_comma_when_content_with_special_characters():
    content = r'"<+>-|@:{ };!=~^?$.%#&_\',\\([)]\"*/", lines[10].substring(30, 62)'
    result = mask_string_with_comma(content, '<<tag>>')
    assert result == '"<+>-|@:{ };!=~^?$.%#&_\\\'<<tag>>\\\\([)]\\"*/", lines[10].substring(30, 62)'


def test_find_assert_equals_when_there_is_assert_package():
    content = '''
            }
        Assert.assertEquals(0l, variable);
    }
    '''
    assert_equals = None
    assert_equals_params = None
    for match in find_assert_equals(content):
        assert_equals = match.group("assert_equals")
        assert_equals_params = match.group("assert_equals_params")

    assert assert_equals == 'Assert.assertEquals(0l, variable);'
    assert assert_equals_params == '0l, variable'


def test_find_assert_equals_when_there_is_junit_framework_package():
    content = '''
        junit.framework.Assert.assertEquals(CONSTANT.DISABLED, getStatus());
    }
    '''
    # fileIDModifier.stream().forEach(i -> assertThat("A", is (fileIDModifier.get(0))));
    assert_equals = None
    assert_equals_params = None
    for match in find_assert_equals(content):
        assert_equals = match.group("assert_equals")
        assert_equals_params = match.group("assert_equals_params")

    assert assert_equals == 'junit.framework.Assert.assertEquals(CONSTANT.DISABLED, getStatus());'
    assert assert_equals_params == 'CONSTANT.DISABLED, getStatus()'


def test_find_assert_equals_when_there_is_lambda():
    content = '''
        list.stream().forEach(i -> assertEquals(entities.get(0), "A"));
    }
    '''
    assert_equals = None
    assert_equals_params = None
    for match in find_assert_equals(content):
        assert_equals = match.group("assert_equals")
        assert_equals_params = match.group("assert_equals_params")

    assert assert_equals == 'assertEquals(entities.get(0), "A"));'
    assert assert_equals_params == 'entities.get(0), "A")'
