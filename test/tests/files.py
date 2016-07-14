import unittest
import os
import posixpath

from bide.files import File
from ._context import _temporary_directory_path, _make_temporary_directory
from ._context import _remove_temporary_directory, _current_directory_path


class TestFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        _remove_temporary_directory()
        _make_temporary_directory()

        # # move to __init__
        current_directory = '{}{}'.format(os.curdir, posixpath.sep)
        parent_directory = '{}{}'.format(os.pardir, posixpath.sep)

        instance_2_name = 'text.md'
        instance_3_name = 'avatar'
        instance_7_name = 'abc'
        instance_9_name = '123'

        instance_3_base = '../{}'.format(instance_3_name)

        instance_8_path = ('{}'*22).format(
            current_directory,
            parent_directory,
            parent_directory,
            current_directory,
            parent_directory,
            parent_directory,
            parent_directory,
            current_directory,
            parent_directory,
            current_directory,
            current_directory,
            parent_directory,
            parent_directory,
            current_directory,
            parent_directory,
            current_directory,
            current_directory,
            current_directory,
            parent_directory,
            parent_directory,
            current_directory,
            parent_directory
        )

        cls.instance_2_name = instance_2_name
        cls.instance_7_name = instance_7_name
        cls.instance_9_name = instance_9_name

        cls.instance_2_path = instance_2_name
        cls.instance_3_path = '{}_1.png'.format(instance_3_name)
        cls.instance_4_path = '{}_2.png'.format(instance_3_name)
        cls.instance_5_path = posixpath.sep
        cls.instance_6_path = current_directory
        cls.instance_8_path = instance_8_path
        cls.instance_9_path = '{}{}'.format(instance_8_path, instance_9_name)
        cls.instance_7_path = '{}{}'.format(parent_directory, instance_7_name)

        temporary_path = _temporary_directory_path()
        avatar_1_path = os.path.join(temporary_path, cls.instance_3_path)
        avatar_2_path = os.path.join(temporary_path, cls.instance_4_path)

        with open(avatar_1_path, 'w') as file:
            file.write('monkeys')

        cls.instance_1 = File()
        cls.instance_2 = File(cls.instance_2_path, temporary_path)
        cls.instance_3 = File(instance_3_base, temporary_path, match=True)
        cls.instance_4 = File(cls.instance_4_path, temporary_path)
        cls.instance_5 = File(cls.instance_5_path, temporary_path)
        cls.instance_6 = File(cls.instance_6_path)
        cls.instance_7 = File(cls.instance_7_path)
        cls.instance_8 = File(cls.instance_8_path)
        cls.instance_9 = File(cls.instance_9_path)

        with open(avatar_2_path, 'w') as file:
            file.write('capuchins')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        _remove_temporary_directory()

    def test_init(self):
        current_path = _current_directory_path()
        temporary_path = _temporary_directory_path()

        root_path = os.path.realpath(os.sep)
        joined_path = os.path.join(root_path, posixpath.sep)
        default_root = os.path.normpath(joined_path).rstrip(os.sep)

        text_path = posixpath.join(posixpath.sep, self.instance_2_name)
        text_full_path = os.path.join(temporary_path, self.instance_2_name)
        avatar_1_path = posixpath.join(posixpath.sep, self.instance_3_path)
        avatar_1_full_path = os.path.join(temporary_path, self.instance_3_path)
        avatar_2_path = posixpath.join(posixpath.sep, self.instance_4_path)
        avatar_2_full_path = os.path.join(temporary_path, self.instance_4_path)
        instance_7_path = '{}{}'.format(posixpath.sep, self.instance_7_name)
        instance_7_full_path = os.path.join(current_path, self.instance_7_name)
        instance_9_path = '{}{}'.format(posixpath.sep, self.instance_9_name)
        instance_9_full_path = os.path.join(current_path, self.instance_9_name)

        self.assertTrue(self.instance_1.root == os.path.realpath(os.sep))
        self.assertTrue(self.instance_1.path == posixpath.sep)
        self.assertTrue(self.instance_1.parent_path == posixpath.sep)
        self.assertTrue(self.instance_1.name == '')
        self.assertTrue(self.instance_1.full_path == default_root)
        self.assertTrue(self.instance_1.full_parent_path == default_root)

        self.assertTrue(self.instance_2.root == temporary_path)
        self.assertTrue(self.instance_2.path == text_path)
        self.assertTrue(self.instance_2.parent_path == posixpath.sep)
        self.assertTrue(self.instance_2.name == self.instance_2_name)
        self.assertTrue(self.instance_2.full_path == text_full_path)
        self.assertTrue(self.instance_2.full_parent_path == temporary_path)

        self.assertTrue(self.instance_3.root == temporary_path)
        self.assertTrue(self.instance_3.path == avatar_1_path)
        self.assertTrue(self.instance_3.parent_path == posixpath.sep)
        self.assertTrue(self.instance_3.name == self.instance_3_path)
        self.assertTrue(self.instance_3.full_path == avatar_1_full_path)
        self.assertTrue(self.instance_3.full_parent_path == temporary_path)

        self.assertTrue(self.instance_4.root == temporary_path)
        self.assertTrue(self.instance_4.path == avatar_2_path)
        self.assertTrue(self.instance_4.parent_path == posixpath.sep)
        self.assertTrue(self.instance_4.name == self.instance_4_path)
        self.assertTrue(self.instance_4.full_path == avatar_2_full_path)
        self.assertTrue(self.instance_4.full_parent_path == temporary_path)

        self.assertTrue(self.instance_5.root == temporary_path)
        self.assertTrue(self.instance_5.path == posixpath.sep)
        self.assertTrue(self.instance_5.parent_path == posixpath.sep)
        self.assertTrue(self.instance_5.name == '')
        self.assertTrue(self.instance_5.full_path == temporary_path)
        self.assertTrue(self.instance_5.full_parent_path == temporary_path)

        self.assertTrue(self.instance_6.root == current_path)
        self.assertTrue(self.instance_6.path == posixpath.sep)
        self.assertTrue(self.instance_6.parent_path == posixpath.sep)
        self.assertTrue(self.instance_6.name == '')
        self.assertTrue(self.instance_6.full_path == current_path)
        self.assertTrue(self.instance_6.full_parent_path == current_path)

        self.assertTrue(self.instance_7.root == current_path)
        self.assertTrue(self.instance_7.path == instance_7_path)
        self.assertTrue(self.instance_7.parent_path == posixpath.sep)
        self.assertTrue(self.instance_7.name == self.instance_7_name)
        self.assertTrue(self.instance_7.full_path == instance_7_full_path)
        self.assertTrue(self.instance_7.full_parent_path == current_path)

        self.assertTrue(self.instance_8.root == current_path)
        self.assertTrue(self.instance_8.path == posixpath.sep)
        self.assertTrue(self.instance_8.parent_path == posixpath.sep)
        self.assertTrue(self.instance_8.name == '')
        self.assertTrue(self.instance_8.full_path == current_path)
        self.assertTrue(self.instance_8.full_parent_path == current_path)

        self.assertTrue(self.instance_9.root == current_path)
        self.assertTrue(self.instance_9.path == instance_9_path)
        self.assertTrue(self.instance_9.parent_path == posixpath.sep)
        self.assertTrue(self.instance_9.name == self.instance_9_name)
        self.assertTrue(self.instance_9.full_path == instance_9_full_path)
        self.assertTrue(self.instance_9.full_parent_path == current_path)

    def test_bool(self):
        self.assertTrue(bool(self.instance_1))
        self.assertTrue(not bool(self.instance_2))
        self.assertTrue(bool(self.instance_3))
        self.assertTrue(bool(self.instance_4))
        self.assertTrue(bool(self.instance_5))
