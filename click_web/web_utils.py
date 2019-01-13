from collections import OrderedDict

import click
from flask import render_template, abort
import click_web
from click_web.utils import get_input_field


def click_to_tree(node: click.BaseCommand, parents=[]):
    '''
    Convert a click root command to a tree of dicts and lists
    :return: a json like tree
    '''
    res_childs = []
    if isinstance(node, click.core.Group):
        # a group, recurse for every child
        for child in node.commands.values():
            res_childs.append(click_to_tree(child, parents[:] + [node, ]))

    res = OrderedDict()
    res['name'] = node.name
    res['help'] = node.get_short_help_str()
    path_parts = parents + [node]
    res['path'] = '/' + '/'.join(p.name for p in path_parts[1:])
    if res_childs:
        res['childs'] = res_childs
    return res


def render_command_form(ctx, command: click.Command, command_path):
    if command:
        # force help option off, no need in web.
        command.add_help_option = False

        fields = [get_input_field(ctx, p) for p in command.get_params(ctx)]
        return render_template('command_form.html.j2',
                               ctx=ctx,
                               command=command,
                               fields=fields,
                               command_path=command_path)
    else:
        return abort(404, 'command not found. Must be one of {}'.format(click_web.click_root_cmd.list_commands(ctx)))
