import argparse
import sys
import yaml

import jinja2


def parse_data_to_markup(source, dest, format_='yaml',
                         template='standard_entry.md.jinja'):
    """Given the path to a source data file and a destination, turn the source
    file into a Python dictionary and then pass it to a Jinja template, writing
    to the destination.

    Args:
        source (file): File-like object to read and parse data from.
        dest (file): File-like object to write the rendered template to.

    Kwargs:
        format (string): What format the source file is in. Default assumption
            is `yaml`.
        template (string): Name of the template we should read and then render.
    """
    data = None

    if format_ == 'yaml':
        with open(source, 'r') as f:
            data = yaml.load(f)
    else:
        raise RuntimeError("No usable format given to data parser!")

    loader = jinja2.FileSystemLoader('tools/templates')
    env = jinja2.Environment(loader=loader)

    template = env.get_template(template)

    data['source'] = source
    print source

    dest.write(template.render(**data))


def main():
    """Create the argument parser and parse from the environment, then run the
    main execution to transform data to markup.
    """
    parser = argparse.ArgumentParser(description=('Turn a generic data file '
                                                  'into markdown via Jinja '
                                                  'template'))
    parser.add_argument('-s', '--source', dest='source')
    args = parser.parse_args()

    if args.source is None:
        print('No source file given!')
        sys.exit(0)

    out = parse_data_to_markup(args.source, sys.stdout)

    sys.exit(0)

if __name__ == '__main__':
    main()
