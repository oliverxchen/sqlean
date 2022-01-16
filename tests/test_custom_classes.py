from sqlean.custom_classes import CData, CToken, CTree


def test_token_initialisation() -> None:
    token = CToken(type_=CData(name="token"), value="value")
    assert token.type == CData(name="token")
    assert token.value == "value"


def test_tree_initialisation() -> None:
    token = CToken(type_=CData(name="token"), value="value")
    tree = CTree(data=CData(name="tree"), children=[token])
    assert tree.data == CData(name="tree")
    assert isinstance(tree.children[0], CToken)
    assert tree.children[0].type == CData(name="token")
    assert tree.children[0].value == "value"
