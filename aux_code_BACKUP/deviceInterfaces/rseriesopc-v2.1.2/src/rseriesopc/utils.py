# -*- coding: utf-8 -*-
import logging

log = logging.getLogger("rseriesclient.utils")


def get_interest_child(node, target):
    """
    Return the node's child that matchs with target string

    Parameters
    ----------
    node : opcua.Node()
        Node that will be filtered
    target : string
        string to match filtering the node

    Returns
    -------
    opcua.Node()
        Node which browse name match with the string

    """
    if node is None:
        return None
    getted = None
    for child in node.get_children():
        if target in child.get_browse_name().to_string():
            getted = child
            return getted
    if getted is None:
        log.info("The machine has not the component " + target)
        infoAllChildren(node)
    return getted


def toLetter(num):
    """
    Convert an integer to equivalent capitalized alphabet letter.

    Parameters
    ----------
    num : integer
        It is the number to convert.

    Returns
    -------
    char
        It is the capitalized alphabet letter

    """
    res = ""
    while num >= 0:
        if num < 26:
            return chr(num + 65) + res
        char = int(num) % 26
        num = num - char
        num = int(num / 26) - 1
        char = chr(char + 65)
        res = char + res


def infoAllChildren(node):
    """
    It prints all the browse name of the children of a given node

    Parameters
    ----------
    node : opcua.Node
        It is the parent node whose children will be printed.

    Returns
    -------
    None.

    """
    log.info("The children of " + node.get_browse_name() + " are:")
    for child in node.get_children():
        log.info(child.get_browse_name().to_string())
