import unittest
import os
import zipfile
import collections

from ._context import _current_directory_path, _make_temporary_subdirectory
from ._context import _remove_temporary_directory, _temporary_directory_path
from ._context import _temporary_subdirectory_path

from bide.utilities import strand, salt, feed, directory, compress, encode
from bide.utilities import decode, checksum, array



class TestUtilities(unittest.TestCase):
    @classmethod
    def setUpClass(_):
        super().tearDownClass()

        _remove_temporary_directory()
        directory_path = _make_temporary_subdirectory()

        files = {
            'file_1': 'abc',
            'file_2': '1\n\nb\n \n3\n',
            'file_3': ''
        }

        for name, content in files.items():
            file_path = os.path.join(directory_path, name)

            with open(file_path, 'w') as file:
                file.write(content)

    @classmethod
    def tearDownClass(_):
        super().tearDownClass()

        _remove_temporary_directory()

    def _test_array_results(self, standard, deque, result):
        self.assertTrue(standard == result)
        self.assertTrue(deque == collections.deque(result))
        self.assertTrue(list(deque) == result)

        self.assertTrue(isinstance(standard, list))
        self.assertTrue(isinstance(deque, collections.deque))

    def _test_salt(self, length):
        salted = salt(length)

        self.assertTrue(isinstance(salted, str))
        self.assertTrue(len(salted) == length)

    def _test_compress(self, input_directory, output_directory, output_name,
                       file_infos, store=False, files=None, **kwargs):

        compress(
            input_directory,
            name=output_name,
            store=store,
            files=files,
            **kwargs
        )

        output_path = os.path.join(output_directory, output_name)

        if isinstance(files, str):
            pre_file_count = 1
        elif files:
            pre_file_count = len(files)
        else:
            pre_file_count = len(file_infos)

        self.assertTrue(os.path.exists(output_path))

        with zipfile.ZipFile(output_path) as zipped_directory:
            file_count = 0

            for file_info in zipped_directory.infolist():
                file_count += 1
                compression = 0 if store else 8
                pre_file_info = file_infos[file_info.filename]

                self.assertTrue(compression == file_info.compress_type)
                self.assertTrue(pre_file_info['size'] == file_info.file_size)
                self.assertTrue(pre_file_info['checksum'] == file_info.CRC)

            self.assertTrue(file_count == pre_file_count)

    def _test_directory_is(self, path):
        self.assertTrue(_current_directory_path() == path)

    def test_strand(self):
        stranded = strand(None)

        self.assertTrue(stranded == '')

    def test_array(self):
        element_1 = 1
        element_2 = 2
        list_1 = [1]
        list_2 = [2]
        result_list = list_2 + list_1

        standard_array_1 = array(element_1, deque=False)
        deque_array_1 = array(element_1, deque=True)

        standard_array_2 = array(list_1, deque=False)
        deque_array_2 = array(list_1, deque=True)

        standard_array_3 = array(element_1, element_2, deque=False)
        deque_array_3 = array(element_1, element_2, deque=True)

        standard_array_4 = array(list_1, element_2, deque=False)
        deque_array_4 = array(list_1, element_2, deque=True)

        standard_array_5 = array(element_1, list_2, deque=False)
        deque_array_5 = array(element_1, list_2, deque=True)

        standard_array_6 = array(list_1, list_2, deque=False)
        deque_array_6 = array(list_1, list_2, deque=True)

        self._test_array_results(standard_array_1, deque_array_1, list_1)
        self._test_array_results(standard_array_2, deque_array_2, list_1)
        self._test_array_results(standard_array_3, deque_array_3, result_list)
        self._test_array_results(standard_array_4, deque_array_4, result_list)
        self._test_array_results(standard_array_5, deque_array_5, result_list)
        self._test_array_results(standard_array_6, deque_array_6, result_list)

    def test_salt(self):
        self._test_salt(32)
        self._test_salt(64)

    def test_coder(self):
        unencoded_json = {'a': 2}
        preencoded_json = '{"a": 2}'
        preencoded_json_bytes = bytes(preencoded_json, 'utf-8')
        preencoded_percent = '%7B%22a%22%3A%202%7D'
        preencoded_base64 = b'eyJhIjogMn0='

        encoded_percent = encode(preencoded_json, method='percent')
        encoded_base64 = encode(preencoded_json_bytes, method='base64')
        encoded_json = encode(unencoded_json, method='json')

        self.assertTrue(encoded_percent == preencoded_percent)
        self.assertTrue(encoded_base64 == preencoded_base64)
        self.assertTrue(encoded_json == preencoded_json)

        decoded_percent = decode(encoded_percent, method='percent')
        decoded_base64 = decode(encoded_base64, method='base64')
        decoded_json = decode(encoded_json, method='json')

        self.assertTrue(decoded_percent == preencoded_json)
        self.assertTrue(decoded_base64 == preencoded_json_bytes)
        self.assertTrue(decoded_json == unencoded_json)

    def test_checksum(self):
        string_1 = b'123'
        list_1 = [b'1', b'2', b'3']

        pre_1_checksum_crc32 = 2286445522
        pre_1_checksum_sha512_1 = '3c9909afec25354d551dae21590bb26e38d53f2173b'
        pre_1_checksum_sha512_2 = '8d3dc3eee4c047e7ab1c1eb8b85103e3be7ba613b31'
        pre_1_checksum_sha512_3 = 'bb5c9c36214dc9f14a42fd7a2fdb84856bca5c44c2'
        pre_1_checksum_sha512 = ''.join((
            pre_1_checksum_sha512_1,
            pre_1_checksum_sha512_2,
            pre_1_checksum_sha512_3
        ))

        string_1_checksum_crc32 = checksum(string_1, algorithm='crc32')
        string_1_checksum_sha512 = checksum(string_1, algorithm='sha512')
        list_1_checksum_crc32 = checksum(list_1, algorithm='crc32')
        list_1_checksum_sha512 = checksum(list_1, algorithm='sha512')

        self.assertTrue(string_1_checksum_crc32 == pre_1_checksum_crc32)
        self.assertTrue(string_1_checksum_sha512 == pre_1_checksum_sha512)
        self.assertTrue(list_1_checksum_crc32 == pre_1_checksum_crc32)
        self.assertTrue(list_1_checksum_sha512 == pre_1_checksum_sha512)

    def test_compress(self):
        temporary_path = _temporary_directory_path()
        directory_path = _temporary_subdirectory_path()
        files = {
            'file_1': {
                'size': 3,
                'checksum': 891568578
            },
            'file_2': {
                'size': 14,
                'checksum': 955811600
            },
            'file_3': {
                'size': 0,
                'checksum': 0
            }
        }

        self._test_compress(
            directory_path,
            temporary_path,
            'compressed_1.zip',
            files,
            store=True,
            _update=False,
            inside=False
        )

        self._test_compress(
            directory_path,
            temporary_path,
            'compressed_2.zip',
            files,
            store=False,
            _update=False,
            inside=False
        )

        self._test_compress(
            directory_path,
            temporary_path,
            'compressed_3.zip',
            files,
            store=True,
            _update=False,
            inside=False,
            files='file_1',
            include=True
        )

        self._test_compress(
            directory_path,
            directory_path,
            'compressed_4.zip',
            files,
            store=True,
            _update=False,
            inside=True,
            files=['file_1', 'file_3'],
            include=True
        )

    def test_feed(self):
        directory_path = _temporary_subdirectory_path()
        file_path = os.path.join(directory_path, 'file_2')

        with open(file_path, 'r') as file:
            lines = file.readlines()

        feeder_1 = feed(
            lines,
            strip=True,
            skip=True,
            split=False,
            headless=False,
            tailless=False
        )

        feeder_2 = feed(
            lines,
            strip=False,
            skip=True,
            split=False,
            headless=2,
            tailless=1
        )

        self.assertTrue(len(list(feeder_1)) == 3)
        self.assertTrue(len(list(feeder_2)) == 2)

    def test_directory(self):
        temporary_path = _temporary_directory_path()
        directory_path_1 = os.path.join(temporary_path, 'abc')
        directory_path_2 = os.path.join(directory_path_1, '123')
        original_directory_path_3 = os.path.realpath(os.sep)

        if len(original_directory_path_3) > 1:
            directory_path_3 = original_directory_path_3.strip(os.sep)
        else:
            directory_path_3 = original_directory_path_3

        start_path = _current_directory_path()

        os.mkdir(directory_path_1)

        with directory(directory_path_1):
            self._test_directory_is(directory_path_1)

            with directory(directory_path_2, make=True):
                self._test_directory_is(directory_path_2)

                with directory(directory_path_3, make=True):
                    self._test_directory_is(original_directory_path_3)

                self._test_directory_is(directory_path_2)

            self._test_directory_is(directory_path_1)

        self._test_directory_is(start_path)
