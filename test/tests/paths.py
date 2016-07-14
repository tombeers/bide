import unittest

from bide.utilities import Path



class TestPath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.path_1 = ''
        cls.path_2 = ''
        cls.path_3 = 'abc'
        cls.path_5 = 'abc\\123'
        cls.path_6 = '123/abc.md'
        cls.path_7 = '123\\..\\abc.md'
        cls.path_8 = '/abc\\123/'
        cls.path_9 = '\\123/abc\\'
        cls.path_10 = '.MD'
        cls.path_11 = 'abc/.py'
        cls.path_12 = '/'
        cls.path_13 = '\\'
        cls.path_14 = 'C:\\text.md'
        cls.path_15 = 'C:'
        cls.path_16 = './../.././../'
        cls.path_17 = '{}abc'.format(cls.path_16)

        cls.instance_1 = Path(posix=True, chain=True)
        cls.instance_2 = Path(posix=False, chain=False)
        cls.instance_3 = Path(cls.path_3)
        cls.instance_4 = Path(cls.instance_1)
        cls.instance_5 = Path(cls.path_5, posix=True, chain=False)
        cls.instance_6 = Path(cls.path_6, posix=False, chain=True)
        cls.instance_7 = Path(cls.path_7, posix=True, chain=True)
        cls.instance_8 = Path(cls.path_8, posix=False, chain=False)
        cls.instance_9 = Path(cls.path_9, posix=True, chain=False)
        cls.instance_10 = Path(cls.path_10, chain=True)
        cls.instance_11 = Path(cls.path_11, chain=False, posix=False)
        cls.instance_12 = Path(cls.path_12, chain=False, posix=True)
        cls.instance_13 = Path(cls.path_13, chain=False, posix=False)
        cls.instance_14 = Path(cls.path_14, chain=True, posix=False)
        cls.instance_15 = Path(cls.path_15, chain=False, posix=False)
        cls.instance_16 = Path(cls.path_16, chain=False, posix=False)
        cls.instance_17 = Path(cls.path_17, chain=False, posix=True)

    def test_init(self):
        self.assertTrue(self.instance_1.path == self.path_1)
        self.assertTrue(self.instance_2.path == self.path_2)
        self.assertTrue(self.instance_3.path == self.path_3)
        self.assertTrue(self.instance_4 == self.instance_1)
        self.assertTrue(self.instance_5.path == self.path_5)
        self.assertTrue(self.instance_6.path == self.path_6)
        self.assertTrue(self.instance_7.path == self.path_7)
        self.assertTrue(self.instance_8.path == self.path_8)
        self.assertTrue(self.instance_9.path == self.path_9)
        self.assertTrue(self.instance_10.path == self.path_10)
        self.assertTrue(self.instance_11.path == self.path_11)
        self.assertTrue(self.instance_12.path == self.path_12)
        self.assertTrue(self.instance_13.path == self.path_13)
        self.assertTrue(self.instance_14.path == self.path_14)
        self.assertTrue(self.instance_15.path == self.path_15)
        self.assertTrue(self.instance_16.path == self.path_16)
        self.assertTrue(self.instance_17.path == self.path_17)

        self.assertTrue(self.instance_1.posix is True)
        self.assertTrue(self.instance_2.posix is False)
        self.assertTrue(self.instance_4.posix is self.instance_1.posix)

        self.assertTrue(self.instance_1.chain is True)
        self.assertTrue(self.instance_2.chain is False)
        self.assertTrue(self.instance_3.chain is False)
        self.assertTrue(self.instance_4.chain is self.instance_1.chain)

    def test_bool(self):
        self.assertTrue(not bool(self.instance_2))
        self.assertTrue(bool(self.instance_3))

    def test_len(self):
        self.assertTrue(len(self.instance_2) == 0)
        self.assertTrue(len(self.instance_3) == 3)
        self.assertTrue(len(self.instance_5) == 7)
        self.assertTrue(len(self.instance_12) == 1)

    def test_eq(self):
        self.assertTrue(self.instance_1 == self.instance_2)
        self.assertTrue(self.instance_1 == self.instance_2)

    def test_ne(self):
        self.assertTrue(self.instance_1 != self.instance_3)
        self.assertTrue(self.instance_3 != self.instance_6)
        self.assertTrue(self.instance_5 != self.instance_8)
        self.assertTrue(self.instance_7 != self.instance_9)

    def test_join(self):
        joined_1 = self.instance_1.join('x').path
        joined_2 = self.instance_2.join('y')
        joined_3 = self.instance_3.join('x/y')
        joined_4 = self.instance_4.join('\\x\\y\\').path
        joined_5 = self.instance_5.join('/x/', '/y/')
        joined_6 = self.instance_12.join('x')
        joined_7 = self.instance_13.join('x', '/y/')
        joined_8 = self.instance_15.join('text.md')
        joined_9 = self.instance_16.join('123')

        self.assertTrue(joined_1 == 'x')
        self.assertTrue(joined_2 == 'y')
        self.assertTrue(joined_3 == 'abc\\x/y')
        self.assertTrue(joined_4 == '\\x\\y\\')
        self.assertTrue(joined_5 == 'abc\\123/x/y/')
        self.assertTrue(joined_6 == '/x')
        self.assertTrue(joined_7 == '\\x\\y/')
        self.assertTrue(joined_8 == 'C:\\text.md')
        self.assertTrue(joined_9 == '{}{}'.format(self.path_16, '123'))

    def test_normalise(self):
        normalised_1 = self.instance_5.normalise()
        normalised_2 = self.instance_6.normalise().path
        normalised_3 = self.instance_7.normalise(absolute=True).path
        normalised_4 = self.instance_7.normalise(collapse=False).path
        normalised_5 = self.instance_7.normalise(resolve=False).path
        normalised_6 = self.instance_8.normalise(collapse=False)
        normalised_7 = self.instance_11.normalise(absolute=True)
        normalised_8 = self.instance_12.normalise()
        normalised_9 = self.instance_12.normalise(collapse=False)
        normalised_10 = self.instance_13.normalise(absolute=True)
        normalised_11 = self.instance_14.normalise()
        normalised_12 = self.instance_17.normalise(absolute=True)

        self.assertTrue(normalised_1 == 'abc/123')
        self.assertTrue(normalised_2 == '123\\abc.md')
        self.assertTrue(normalised_3 == '/abc.md')
        self.assertTrue(normalised_4 == '123/../abc.md')
        self.assertTrue(normalised_5 == '123/abc.md')
        self.assertTrue(normalised_6 == '\\abc\\123\\')
        self.assertTrue(normalised_7 == '\\abc\\.py')
        self.assertTrue(normalised_8 == '/')
        self.assertTrue(normalised_9 == '/')
        self.assertTrue(normalised_10 == '\\')
        self.assertTrue(normalised_11 == 'C:\\text.md')
        self.assertTrue(normalised_12 == '/abc')

    def test_strip(self):
        stripped_1 = self.instance_8.strip()
        stripped_2 = self.instance_8.strip(side='left')
        stripped_3 = self.instance_8.strip(side='right')
        stripped_4 = self.instance_9.strip()
        stripped_5 = self.instance_9.strip(side='left')
        stripped_6 = self.instance_9.strip(side='right')
        stripped_7 = self.instance_12.strip(side='left')
        stripped_8 = self.instance_13.strip(side='right')

        self.assertTrue(stripped_1 == 'abc\\123')
        self.assertTrue(stripped_2 == 'abc\\123/')
        self.assertTrue(stripped_3 == '/abc\\123')
        self.assertTrue(stripped_4 == '123/abc')
        self.assertTrue(stripped_5 == '123/abc\\')
        self.assertTrue(stripped_6 == '\\123/abc')
        self.assertTrue(stripped_7 == '')
        self.assertTrue(stripped_8 == '')

    def test_split(self):
        split_1 = self.instance_1.split()
        split_2 = self.instance_2.split(maximum=None)
        split_3 = self.instance_3.split()
        split_4 = self.instance_3.split(maximum=None)
        split_5 = self.instance_5.split()
        split_6 = self.instance_5.split(maximum=None)
        split_7 = self.instance_7.split()
        split_8 = self.instance_7.split(maximum=None)
        split_9 = self.instance_10.split()
        split_10 = self.instance_10.split(maximum=-1)
        split_11 = self.instance_11.split()
        split_12 = self.instance_11.split(maximum=-1)
        split_13 = self.instance_12.split()
        split_14 = self.instance_13.split(maximum=-1)
        split_15 = self.instance_14.split()
        split_16 = self.instance_14.split(maximum=-1)

        self.assertTrue(split_1 == ['', ''])
        self.assertTrue(split_2 == [''])
        self.assertTrue(split_3 == ['', 'abc'])
        self.assertTrue(split_4 == ['abc'])
        self.assertTrue(split_5 == ['abc', '123'])
        self.assertTrue(split_6 == ['abc', '123'])
        self.assertTrue(split_7 == ['123/..', 'abc.md'])
        self.assertTrue(split_8 == ['123', '..', 'abc.md'])
        self.assertTrue(split_9 == ['', '.MD'])
        self.assertTrue(split_10 == ['.MD'])
        self.assertTrue(split_11 == ['abc', '.py'])
        self.assertTrue(split_12 == ['abc', '.py'])
        self.assertTrue(split_13 == ['', ''])
        self.assertTrue(split_14 == [''])
        self.assertTrue(split_15 == ['C:', 'text.md'])
        self.assertTrue(split_16 == ['C:', 'text.md'])

    def test_simplify(self):
        # from: http:www.cl.cam.ac.uk/~mgk25/ucs/examples/quickbrown.txt

        special_path_1 = '/café/'
        special_path_2 = '/Âne ex\\aéquo au/whist'
        special_path_3 = 'Árvíztűrő/tükörfúrógép'
        special_path_4 = '/Heizölrückstoßabdämpfung/'
        special_path_5 = 'Γαζέες καὶ μυρτιὲς δὲν θὰ βρῶ πιὰ στὸ χρυσαφὶ ξέφωτο'
        special_path_6 = ''.join([
            '/D\'fhuascail Íosa,/Úrmhac na\\hÓighe Beannaithe, pór',
            'Éava\\agus/Ádhaimh\\'
        ])

        special_path_7 = ''.join([
            '/Quizdeltagerne spiste/jordbær med\\fløde, mens ',
            'cirkusklovnen/Wolther spillede på/xylofon.'
        ])

        special_path_8 = ''.join([
            '/El pingüino Wenceslao\\hizo kilómetros/bajo exhaustiva/lluvia y',
            'frío,/añoraba a\\su querido cachorro.\\'
        ])

        prenormalised_path_1 = '/cafe/'
        prenormalised_path_2 = '/Ane ex\\aequo au/whist'
        prenormalised_path_3 = 'Arvizturo/tukorfurogep'
        prenormalised_path_4 = '/Heizolruckstoabdampfung/'
        prenormalised_path_5 = '         '
        prenormalised_path_6 = ''.join([
            '/D\'fhuascail Iosa,/Urmhac na\\hOighe Beannaithe, ',
            'porEava\\agus/Adhaimh\\'
        ])

        prenormalised_path_7 = ''.join([
            '/Quizdeltagerne spiste/jordbr med\\flde, mens ',
            'cirkusklovnen/Wolther spillede pa/xylofon.'
        ])

        prenormalised_path_8 = ''.join([
            '/El pinguino Wenceslao\\hizo kilometros/bajo exhaustiva/lluvia ',
            'yfrio,/anoraba a\\su querido cachorro.\\'
        ])

        special_path_instance_1 = Path(special_path_1, posix=True, chain=False)
        special_path_instance_2 = Path(special_path_2, posix=True, chain=False)
        special_path_instance_3 = Path(special_path_3, posix=True, chain=False)
        special_path_instance_4 = Path(special_path_4, posix=True, chain=False)
        special_path_instance_5 = Path(special_path_5, posix=True, chain=False)
        special_path_instance_6 = Path(special_path_6, posix=True, chain=False)
        special_path_instance_7 = Path(special_path_7, posix=True, chain=False)
        special_path_instance_8 = Path(special_path_8, posix=True, chain=False)

        simplified_path_1 = special_path_instance_1.simplify()
        simplified_path_2 = special_path_instance_2.simplify()
        simplified_path_3 = special_path_instance_3.simplify()
        simplified_path_4 = special_path_instance_4.simplify()
        simplified_path_5 = special_path_instance_5.simplify()
        simplified_path_6 = special_path_instance_6.simplify()
        simplified_path_7 = special_path_instance_7.simplify()
        simplified_path_8 = special_path_instance_8.simplify()

        self.assertTrue(simplified_path_1 == prenormalised_path_1)
        self.assertTrue(simplified_path_2 == prenormalised_path_2)
        self.assertTrue(simplified_path_3 == prenormalised_path_3)
        self.assertTrue(simplified_path_4 == prenormalised_path_4)
        self.assertTrue(simplified_path_5 == prenormalised_path_5)
        self.assertTrue(simplified_path_6 == prenormalised_path_6)
        self.assertTrue(simplified_path_7 == prenormalised_path_7)
        self.assertTrue(simplified_path_8 == prenormalised_path_8)

    def test_parent(self):
        self.assertTrue(self.instance_1.parent().path == '')
        self.assertTrue(self.instance_2.parent() == '')
        self.assertTrue(self.instance_3.parent() == '')
        self.assertTrue(self.instance_4.parent().path == '')
        self.assertTrue(self.instance_5.parent() == 'abc')
        self.assertTrue(self.instance_6.parent().path == '123')
        self.assertTrue(self.instance_7.parent().path == '123/..')
        self.assertTrue(self.instance_8.parent() == '\\abc')
        self.assertTrue(self.instance_9.parent() == '/123')
        self.assertTrue(self.instance_10.parent() == '')
        self.assertTrue(self.instance_11.parent() == 'abc')
        self.assertTrue(self.instance_12.parent() == '')
        self.assertTrue(self.instance_13.parent() == '')
        self.assertTrue(self.instance_14.parent() == 'C:')
        self.assertTrue(self.instance_14.parent().parent() == '')
        self.assertTrue(self.instance_16.parent() == '.\\..\\..\\.')
        self.assertTrue(self.instance_17.parent() == self.path_16.rstrip('/'))

    def test_name(self):
        self.assertTrue(self.instance_1.name() == '')
        self.assertTrue(self.instance_2.name() == '')
        self.assertTrue(self.instance_3.name() == 'abc')
        self.assertTrue(self.instance_4.name() == '')
        self.assertTrue(self.instance_5.name() == '123')
        self.assertTrue(self.instance_6.name() == 'abc.md')
        self.assertTrue(self.instance_7.name() == 'abc.md')
        self.assertTrue(self.instance_8.name() == '123')
        self.assertTrue(self.instance_9.name() == 'abc')
        self.assertTrue(self.instance_10.name() == '.MD')
        self.assertTrue(self.instance_11.name() == '.py')
        self.assertTrue(self.instance_7.name(split=True) == ('abc', '.md'))
        self.assertTrue(self.instance_9.name(split=True) == ('abc', ''))
        self.assertTrue(self.instance_10.name(split=True) == ('', '.MD'))
        self.assertTrue(self.instance_12.name() == '')
        self.assertTrue(self.instance_13.name() == '')
        self.assertTrue(self.instance_14.name() == 'text.md')
        self.assertTrue(self.instance_15.name() == 'C:')
        self.assertTrue(self.instance_17.name() == 'abc')

    def test_base(self):
        self.assertTrue(self.instance_1.base() == '')
        self.assertTrue(self.instance_3.base() == 'abc')
        self.assertTrue(self.instance_5.base() == '123')
        self.assertTrue(self.instance_6.base() == 'abc')
        self.assertTrue(self.instance_7.base() == 'abc')
        self.assertTrue(self.instance_8.base() == '123')
        self.assertTrue(self.instance_9.base() == 'abc')
        self.assertTrue(self.instance_9.base() == 'abc')
        self.assertTrue(self.instance_10.base() == '')
        self.assertTrue(self.instance_11.base() == '')
        self.assertTrue(self.instance_1.base(full=True) == '')
        self.assertTrue(self.instance_3.base(full=True) == 'abc')
        self.assertTrue(self.instance_5.base(full=True) == 'abc/123')
        self.assertTrue(self.instance_6.base(full=True) == '123\\abc')
        self.assertTrue(self.instance_7.base(full=True) == '123/../abc')
        self.assertTrue(self.instance_8.base(full=True) == '\\abc\\123')
        self.assertTrue(self.instance_9.base(full=True) == '/123/abc')
        self.assertTrue(self.instance_10.base(full=True) == '')
        self.assertTrue(self.instance_11.base(full=True) == 'abc')
        self.assertTrue(self.instance_12.base() == '')
        self.assertTrue(self.instance_13.base(full=True) == '')
        self.assertTrue(self.instance_14.base() == 'text')
        self.assertTrue(self.instance_14.base(full=True) == 'C:\\text')
        self.assertTrue(self.instance_15.base() == 'C:')
        self.assertTrue(self.instance_15.base(full=True) == 'C:')
        self.assertTrue(self.instance_17.base() == 'abc')
        self.assertTrue(self.instance_17.base(full=True) == self.path_17)

    def test_extension(self):
        instance_1 = self.instance_10.extension('.html')

        self.assertTrue(instance_1.extension() == '.html')
        self.assertTrue(self.instance_1.extension() == '')
        self.assertTrue(self.instance_2.extension() == '')
        self.assertTrue(self.instance_3.extension() == '')
        self.assertTrue(self.instance_4.extension() == '')
        self.assertTrue(self.instance_5.extension() == '')
        self.assertTrue(self.instance_6.extension() == '.md')
        self.assertTrue(self.instance_7.extension() == '.md')
        self.assertTrue(self.instance_8.extension() == '')
        self.assertTrue(self.instance_9.extension() == '')
        self.assertTrue(self.instance_10.extension() == '.MD')
        self.assertTrue(self.instance_11.extension() == '.py')
        self.assertTrue(self.instance_12.extension() == '')
        self.assertTrue(self.instance_13.extension() == '')
        self.assertTrue(self.instance_14.extension() == '.md')
        self.assertTrue(self.instance_15.extension() == '')
