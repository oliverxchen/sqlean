import pytest

from sqlean.node import ArgumentItem, ArgumentList, SelectItem
from sqlean.exceptions import NodeListError


def test_NodeList_used():
    # test if a class derived from NodeList can be initialised
    arg_items = [ArgumentItem("arg1", 1, 0), ArgumentItem("arg2", 1, 7)]
    arg_list = ArgumentList(arg_items, 0, 0)
    assert arg_list.type == "ArgumentItem"
    assert len(arg_list.items) == 2

    # test a proper append
    arg_list.append(ArgumentItem("arg3", 1, 13))
    assert len(arg_list.items) == 3

    # test a wrong append
    with pytest.raises(NodeListError) as excinfo:
        arg_list.append(SelectItem("select1", "", 2, 1))
    expected_msg = (
        "Cannot append item with type SelectItem to NodeList with type ArgumentItem"
    )
    assert str(excinfo.value) == expected_msg


def test_NodeList_wrong_init():
    # test the exception if a class derived from NodeList is initialised wrong
    items = [ArgumentItem("arg1", 1, 0), SelectItem("arg2", "", 1, 7)]
    with pytest.raises(NodeListError) as excinfo:
        _ = ArgumentList(items, 0, 0)
    # The message will look like this (but order not guaranteed):
    # There was more than one type in NodeList: {'ArgumentItem', 'SelectItem'}
    assert str(excinfo.value).startswith("There was more than one type in NodeList:")
    assert "ArgumentItem" in str(excinfo.value)
    assert "SelectItem" in str(excinfo.value)
