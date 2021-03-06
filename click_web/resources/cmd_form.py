from typing import List, Tuple

import click
from flask import render_template, abort

import click_web
from click_web.exceptions import CommandNotFound
from click_web.resources.input_fields import get_input_field


def get_form_for(command_path: str):
    try:
        ctx_and_commands = _get_commands_by_path(command_path)
    except CommandNotFound as err:
        return abort(404, str(err))

    levels = _generate_form_data(ctx_and_commands)
    return render_template('command_form.html.j2',
                           levels=levels,
                           command=levels[-1]['command'],
                           command_path=command_path)


def _get_commands_by_path(command_path: str) -> Tuple[click.Context, click.Command]:
    """
    Take a (slash separated) string and generate (context, command) for each level.
    :param command_path: "some_group/a_command"
    :return: Return a list from root to leaf commands. each element is (Click.Context, Click.Command)
    """
    command_path_items = command_path.split('/')
    command_name, *command_path_items = command_path_items
    command = click_web.click_root_cmd
    if command.name != command_name:
        raise CommandNotFound('Failed to find root command {}. There is a root commande named:{}'
                              .format(command_name, command.name))
    result = []
    with click.Context(command, info_name=command, parent=None) as ctx:
        result.append((ctx, command))
        # dig down the path parts to find the leaf command
        parent_command = command
        for command_name in command_path_items:
            command = parent_command.get_command(ctx, command_name)
            if command:
                # create sub context for command
                ctx = click.Context(command, info_name=command, parent=ctx)
                parent_command = command
            else:
                raise CommandNotFound('Failed to find command for path "{}". Command "{}" not found. Must be one of {}'
                                      .format(command_path, command_name, parent_command.list_commands(ctx)))
            result.append((ctx, command))
    return result


def _generate_form_data(ctx_and_commands: List[Tuple[click.Context, click.Command]]):
    """
    Construct a list of contexts and commands generate a python data structure for rendering jinja form
    :return: a list of dicts
    """
    levels = []
    for command_index, (ctx, command) in enumerate(ctx_and_commands):
        # force help option off, no need in web.
        command.add_help_option = False

        input_fields = [get_input_field(ctx, param, command_index, param_index)
                        for param_index, param in enumerate(command.get_params(ctx))]
        levels.append({'command': command, 'fields': input_fields})

    return levels
