from unittest2 import TestCase
from ftw.testing.layer import ComponentRegistryLayer
from izug.ticketbox.utils import uniquify_ids
from izug.ticketbox.utils import create_uniqe_id


class NormalizerLayer(ComponentRegistryLayer):

    def setUp(self):
        super(NormalizerLayer, self).setUp()

        import plone.i18n.normalizer
        self.load_zcml_file('configure.zcml', plone.i18n.normalizer)


NORMALIZER_FIXTURE = NormalizerLayer()


class TestUniquifyIds(TestCase):

    layer = NORMALIZER_FIXTURE

    def test_new_ids_set(self):
        input = [{'id': '', 'title': 'Foo'},
                 {'id': '', 'title': 'Bar'}]

        output = [{'id': 'foo', 'title': 'Foo'},
                  {'id': 'bar', 'title': 'Bar'}]

        self.assertEqual(uniquify_ids(input), output)

    def test_partical_ids(self):
        input = [{'id': 'foo', 'title': 'Foo'},
                 {'id': '', 'title': 'Bar'}]

        output = [{'id': 'foo', 'title': 'Foo'},
                  {'id': 'bar', 'title': 'Bar'}]

        self.assertEqual(uniquify_ids(input), output)

    def test_keeps_unexpected_ids(self):
        input = [{'id': 'fooX', 'title': 'Foo'},
                 {'id': '', 'title': 'Bar'}]

        output = [{'id': 'fooX', 'title': 'Foo'},
                  {'id': 'bar', 'title': 'Bar'}]

        self.assertEqual(uniquify_ids(input), output)

    def test_conflicting_ids(self):
        input = [{'id': '', 'title': 'Foo'},
                 {'id': '', 'title': 'Foo'},
                 {'id': '', 'title': 'Foo'}]

        output = [{'id': 'foo', 'title': 'Foo'},
                  {'id': 'foo-1', 'title': 'Foo'},
                  {'id': 'foo-2', 'title': 'Foo'}]

        self.assertEqual(uniquify_ids(input), output)

    def test_modification_keeps_ids(self):
        input = [{'id': '', 'title': 'Foo'},
                 {'id': 'foo', 'title': 'Bar'}]

        output = [{'id': 'foo-1', 'title': 'Foo'},
                  {'id': 'foo', 'title': 'Bar'}]

        self.assertEqual(uniquify_ids(input), output)

    def test_keeps_other_keys(self):
        input = [{'id': 'foo', 'title': 'Foo', 'bar': 'Bar'}]
        output = [{'id': 'foo', 'title': 'Foo', 'bar': 'Bar'}]

        self.assertEqual(uniquify_ids(input), output)

    def test_does_not_copy(self):
        input = [{'id': '', 'title': 'Foo'}]
        self.assertEqual(id(uniquify_ids(input)), id(input))


class TestCreateUniqueId(TestCase):

    layer = NORMALIZER_FIXTURE

    def test_first_id(self):
        self.assertEqual(create_uniqe_id('Foo', []), 'foo')

    def test_existing_id(self):
        self.assertEqual(create_uniqe_id('Foo', ['foo']), 'foo-1')
        self.assertEqual(create_uniqe_id('Foo', ['foo', 'foo-1']), 'foo-2')

    def test_spaces(self):
        self.assertEqual(create_uniqe_id('Foo bar', []), 'foo-bar')
