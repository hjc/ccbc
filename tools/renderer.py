import argparse
import ConfigParser
import sys
import yaml

from os.path import splitext

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
    elif format_ == 'hjson':
        import hjson
        with open(source, 'r') as f:
            data = hjson.load(f)
    elif format_ == 'cfg':
        # config parser needs the most... massging
        config = ConfigParser.RawConfigParser()
        config.read(source)

        data = config.items('trip')
        data = dict(map(lambda x: (x[0], x[1].replace('\\n', '\n')), data))

        guests = map(lambda x: x[1], config.items('guests'))
        data['guest_list'] = guests
    elif format_ == 'plist':
        import plistlib
        data = plistlib.readPlist(source)
    elif format_ == 'wiki':
        from mediawiki_parser.html import make_parser as make_parser_html
        from mediawiki_parser.preprocessor import make_parser
        preprocessor = make_parser({})

        parser = make_parser_html([], [], [], {}, {})

        with open(source, 'r') as f:
            preprocessed_text = preprocessor.parse(f.read())

        output = parser.parse(preprocessed_text.leaves())

        dest.write(output.value)

        return
    else:
        raise RuntimeError("No usable format given to data parser!")

    loader = jinja2.FileSystemLoader('tools/templates')
    env = jinja2.Environment(loader=loader)

    template = env.get_template(template)

    data['source'] = source

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

    _, ext = splitext(args.source)
    out = parse_data_to_markup(args.source, sys.stdout, format_=ext[1:])

    sys.exit(0)

if __name__ == '__main__':
    main()
