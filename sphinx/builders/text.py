"""
    sphinx.builders.text
    ~~~~~~~~~~~~~~~~~~~~

    Plain-text Sphinx builder.

    :copyright: Copyright 2007-2018 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from os import path

from docutils.io import StringOutput

from sphinx.builders import Builder
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.osutil import ensuredir, os_path
from sphinx.writers.text import TextWriter, TextTranslator

if False:
    # For type annotation
    from typing import Any, Dict, Iterator, Set, Tuple  # NOQA
    from docutils import nodes  # NOQA
    from sphinx.application import Sphinx  # NOQA

logger = logging.getLogger(__name__)


class TextBuilder(Builder):
    name = 'text'
    format = 'text'
    epilog = __('The text files are in %(outdir)s.')

    out_suffix = '.txt'
    allow_parallel = True
    default_translator_class = TextTranslator

    current_docname = None  # type: str

    def init(self):
        # type: () -> None
        # section numbers for headings in the currently visited document
        self.secnumbers = {}  # type: Dict[str, Tuple[int, ...]]

    def get_outdated_docs(self):
        # type: () -> Iterator[str]
        for docname in self.env.found_docs:
            if docname not in self.env.all_docs:
                yield docname
                continue
            targetname = path.join(self.outdir, docname + self.out_suffix)
            try:
                targetmtime = path.getmtime(targetname)
            except Exception:
                targetmtime = 0
            try:
                srcmtime = path.getmtime(self.env.doc2path(docname))
                if srcmtime > targetmtime:
                    yield docname
            except EnvironmentError:
                # source doesn't exist anymore
                pass

    def get_target_uri(self, docname, typ=None):
        # type: (str, str) -> str
        return ''

    def prepare_writing(self, docnames):
        # type: (Set[str]) -> None
        self.writer = TextWriter(self)

    def write_doc(self, docname, doctree):
        # type: (str, nodes.Node) -> None
        self.current_docname = docname
        self.secnumbers = self.env.toc_secnumbers.get(docname, {})
        destination = StringOutput(encoding='utf-8')
        self.writer.write(doctree, destination)
        outfilename = path.join(self.outdir, os_path(docname) + self.out_suffix)
        ensuredir(path.dirname(outfilename))
        try:
            with open(outfilename, 'w', encoding='utf-8') as f:
                f.write(self.writer.output)
        except (IOError, OSError) as err:
            logger.warning(__("error writing file %s: %s"), outfilename, err)

    def finish(self):
        # type: () -> None
        pass


def setup(app):
    # type: (Sphinx) -> Dict[str, Any]
    app.add_builder(TextBuilder)

    app.add_config_value('text_sectionchars', '*=-~"+`', 'env')
    app.add_config_value('text_newlines', 'unix', 'env')
    app.add_config_value('text_add_secnumbers', True, 'env')
    app.add_config_value('text_secnumber_suffix', '. ', 'env')

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
