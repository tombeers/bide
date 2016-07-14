'''
    Various utility functions, mostly for working with files and paths.
'''



import base64
import collections
import hashlib
import itertools
import json
import os
import posixpath
import random
import re
import string
import unicodedata
import urllib.parse
import zipfile
import zlib

try:
    import flask_scrypt
except ImportError:
    pass

try:
    import flask_bcrypt
except ImportError:
    pass



_POSIX_SEPARATOR = posixpath.sep

_DOS_SEPARATOR = '\\'

_SEPARATORS = (_POSIX_SEPARATOR, _DOS_SEPARATOR)

_NT_DRIVE_SUFFIX = ':'


def _url_encode(dictionary):
    query_unparsed = dictionary.get('query')

    # # get this test from crawl's _dictionary method
    if hasattr(query_unparsed, 'items'):
        query_semiparsed = {}

        for key, value in query_unparsed.items():
            if value in (True, False):
                fixed_value = int(value)
            elif value is None:
                fixed_value = ''
            else:
                fixed_value = value

            query_semiparsed.update({key: fixed_value})

        query_parsed = urllib.parse.urlencode(query_semiparsed, doseq=True)

    else:
        query_parsed = strand(query_unparsed)

    return urllib.parse.urlunsplit([
        strand(dictionary.get('protocol')),
        strand(dictionary.get('location')),
        strand(dictionary.get('path')),
        query_parsed,
        strand(dictionary.get('fragment'))
    ])


def _url_decode(url):
    url_split = urllib.parse.urlsplit(url)
    url_query_parsed = urllib.parse.parse_qs(
        url_split.query,
        keep_blank_values=True
    )

    return {
        'protocol': url_split.scheme,
        'location': url_split.netloc,
        'path': url_split.path,
        'query': url_query_parsed,
        'fragment': url_split.fragment
    }


def _code(value, method='percent', encode=True):
    if method == 'percent':
        encoder = urllib.parse.quote
        decoder = urllib.parse.unquote
    elif method == 'base64':
        encoder = base64.urlsafe_b64encode
        decoder = base64.urlsafe_b64decode
    elif method == 'json':
        encoder = json.dumps
        decoder = json.loads
    elif method == 'url':
        encoder = _url_encode
        decoder = _url_decode
    else:
        encoder = decoder = None

    coder = encoder if encode else decoder
    coded_value = coder(value) if coder else value

    return coded_value


def _headless(iterator, count=1):
    iterator = itertools.islice(iterator, count, None)

    for item in iterator:
        yield item


def _tailless(iterator, count=1):
    # from: http:stackoverflow.com/a/16846511
    sliced = itertools.islice(iterator, count)
    previous = collections.deque(sliced, count)

    for item in iterator:
        yield previous.popleft()

        previous.append(item)


def _split(path):
    return Path(path, chain=False).split(maximum=None)


def _get(collection, index=-1, default=None, attribute=None):
    try:
        got = getattr(collection, attribute or '__getitem__')(index)
    except IndexError:
        got = default

    return got


def _drive_reference(path):
    two_length = len(path) == 2

    return two_length and path[0].isalpha() and path[-1] == _NT_DRIVE_SUFFIX


def strand(objekt=''):
    '''
        A small function to return the given object as a string. Returns an
        empty string if the given object equates to zero.

        :param objekt: The object to convert.

        :returns: :class:`str`
    '''

    return str(objekt) if objekt else ''


def array(element=None, collection=None, deque=False):

    '''
        Returns :param:`collection` as an array with the the given
        :param:`element` appended, or the element's content if it is also an
        array.

        :param element: The object to add to :param:`collection`.

        :param collection: The array to which :param:`element` will be added.

        :param deque: Returns :param:`collection` as an instance of
                      :class:`collections.deque`.

        :returns: :class:`list` or :class:`collections.deque`
    '''

    element = element or []
    lister = collections.deque if deque else list

    try:
        collected = lister(collection or ())
    except TypeError:
        collected = lister(array(collection))

    if hasattr(element, 'extend'):
        collected.extend(element)
    else:
        collected.append(element)

    return collected


def get(*args, **kwargs):
    '''
        A function that returns the item at the given :param:`index` from the
        given :class:`list`. If there is no item at that index,
        :param:`default` is returned instead.

        :param collection: The array to pop from.
        :type collection: :class:`list`

        :param index: The index of the item to remove and return.
        :type index: :class:`int`

        :param default: The :class:`object` to return if :param:`index` cannot
                        be found.
        :type default: Any `object`

        :returns: The item at :param:`index` in :param:`collection` or `None`.
    '''

    return _get(*args, **kwargs)


def pop(*args, **kwargs):
    '''
        A function that removes and returns the item at the given
        :param:`index` from the given :class:`list`. If there is no item at
        that index, :param:`default` is returned instead.

        :param collection: The array to pop from.
        :type collection: :class:`list`

        :param index: The index of the item to remove and return.
        :type index: :class:`int`

        :param default: The :class:`object` to return if :param:`index` cannot
                        be found.
        :type default: Any `object`

        :returns: The item at :param:`index` in :param:`collection` or `None`.
    '''

    return _get(attribute='pop', *args, **kwargs)


def salt(length=64, lowercase=True, uppercase=True, digits=True):
    '''
        Returns a randomly generated string.

        :param length: The length of the generated string to return.
        :type length: :class:`int`

        :param lowercase: Include lowercase UTF-8 letters.
        :type lowercase: :class:`bool`

        :param uppercase: Include uppercase UTF-8 letters.
        :type uppercase: :class:`bool`

        :param digits: Include decimal digits letters.
        :type digits: :class:`bool`

        :returns: :class:`str`
    '''

    randomiser = random.SystemRandom()
    characters = ''

    if lowercase:
        characters = ''.join((characters, string.ascii_lowercase))

    if uppercase:
        characters = ''.join((characters, string.ascii_uppercase))

    if digits:
        characters = ''.join((characters, string.digits))

    return ''.join(randomiser.choice(characters) for _ in range(length))


def encode(*args, **kwargs):
    '''
        Encodes the given :param:`value` using the specified :param:`method`.

        :param value: The value to be encoded.
        :type value: :class:`str` if :param:`method` is 'percent',
                     :class:`bytes` if it is 'base64', or any jsonifiable
                     object(s) if it is 'json'.

        :param method: 'percent', 'base64' or 'json'.
        :type method: :class:`str`

        :returns: :class:`str` if :param:`method` is 'percent' or 'json', or
                  :class:`bytes` if it is 'base64'.
    '''

    return _code(encode=True, *args, **kwargs)


def decode(*args, **kwargs):
    '''
        Decodes the given :param:`value` using the specified :param:`method`.

        :param value: The value to be decoded.
        :type value: :class:`str` if :param:`method` is 'percent' or 'json',
                     or :class:`bytes` if it is 'base64'.

        :param method: 'percent', 'base64' or 'json'.
        :type method: :class:`str`

        :returns: :class:`str` if :param:`method` is 'percent', :class:`bytes`
                  if it is 'base64', or the equivalent Python object(s) if it
                  is 'json'.
    '''

    return _code(encode=False, *args, **kwargs)


def checksum(stream, algorithm='crc32', verify=None, salt=None):
    '''
        Calculates the checksum of the given :param:`stream`.

        :param stream: The object to hash.
        :type stream: :class:`bytes` or an iterable containing :class:`bytes`
                      objects. If a string is given, or the iterable contains
                      strings, it or they will be encoded to :class:`bytes`
                      using 'UTF-8' encoding.

        :param algorithm: Specifies what algorithm should be used to calculate
                          the checksum. Can be 'crc32' or any algorithm
                          supported by :mod:`hashlib`.
        :type algorithm: :class:`str`

        :returns: :class:`int` if :param:`algorithm` is 'crc32', otherwise
                  :class:`str`
    '''

    CRC32 = 'crc32'
    SCRYPT = 'scrypt'
    BCRYPT = 'bcrypt'

    is_bytes = hasattr(stream, 'decode')

    if algorithm == SCRYPT:
        result = flask_scrypt.gemerate_password_hash(stream, salt)

    elif algorithm == BCRYPT:
        result = flask_bcrypt.gemerate_password_hash(stream)

    elif algorithm == CRC32:
        if is_bytes:
            result = zlib.crc32(stream)
        else:
            result = 0

            for brook in stream:
                result = zlib.crc32(brook, result)

        result = result & 0xffffffff

    else:
        hasher = hashlib.new(algorithm)

        if is_bytes:
            hasher.update(stream)
        else:
            for brook in stream:
                hasher.update(brook)

        result = hasher.hexdigest()

    if verify:
        if algorithm == SCRYPT:
            returning = flask_scrypt.check_password_hash(stream, verify, salt)
        elif algorithm == BCRYPT:
            returning = flask_bcrypt.check_password_hash(verify, stream)
        else:
            returning = result == verify

    else:
        returning = result

    return returning


def compress(root, name=None, store=False, _update=False, files=None,
             include=True, inside=False):

    '''
        Archives and optionally compresses the given directory as a zip.

        :param root: The directory or file to be zipped.
        :type root: :class:`str`

        :param name: The optional name of the zip file.
        :type name: :class:`str`

        :param store: Whether to just archive or archive and compress the zip
                      file. `True` will just archive it.
        :type store: :class:`bool`

        :param _update: Whether to update an existing zip file or write it new.
                        Currently in alpha state of development.
        :type _update: :class:`bool`

        :param files: The file or files to include/exclude; used with
                      :param:`include`.
        :type files: :class:`str` or :class:`list`

        :param include: Determines whether :param:`files` is a whitelist or
                        blacklist. `True` for whitelist.
        :type include: :class:`bool`

        :param inside: Whether to store the resulting zip file inside or
                       alongside the given directory. Only applies if
                       :param:`root` is a directory.
        :type inside: :class:`bool`

        :returns: :class:`str` containing the output's file name.
    '''

    mode = 'a' if _update else 'w'
    compression = zipfile.ZIP_STORED if store else zipfile.ZIP_DEFLATED
    root_instance = Path(root, chain=False)
    includes = None
    excludes = None

    if inside and not os.path.isdir(root):
        inside = False

    if name:
        output_name = name
    else:
        if inside:
            output_name = '.zip'
        else:
            root_name = root_instance.name()

            if root_name:
                output_name = root_name
            else:
                output_name = Path(salt(4), chain=False).extension('.zip')

    if not inside:
        output_name = Path(os.pardir, chain=False).join(output_name)

    if files:
        if include:
            includes = array(files)
        else:
            excludes = [_split(file) for file in array(files)]

    with directory(root, make=True):
        with zipfile.ZipFile(output_name, mode, compression) as zip_file:
            if includes:
                for include in includes:
                    zip_file.write(include)

            else:
                walked = 0

                for path, _, files in os.walk(os.curdir):
                    for file in files:
                        walked += 1

                        if inside and walked == 1 and file == output_name:
                            continue

                        path_instance = Path(path, chain=True)
                        path_fixed = path_instance.normalise().strip()
                        file_path = path_fixed.join(file).path

                        if excludes:
                            file_path_split = _split(file_path)
                            allowed = file_path_split not in excludes
                        else:
                            allowed = True

                        if allowed:
                            zip_file.write(file_path)

    return output_name


def feed(file, strip=False, skip=False, split=False, headless=False,
         tailless=False):

    '''
        A generator that can process the given :param:`file` iterator in
        various ways, such as stripping lines, ignoring blank lines, skipping
        `x` number of the last lines, etc.

        :param file: Expected to be the equivalent of what
                     :func:`file.readlines`' or :func:`file.xreadlines`'
                     returns.
        :type file: An iterator containing strings, such as those from
                    :class:`file`.

        :param strip: Strip lines of whitespace if `True`, or of whatever else
                      is passed if some non-zero value is given.
        :type strip: :class:`bool` or whatever is taken by :func:`str.strip`

        :param skip: Skips blanks lines.
        :type skip: :class:`bool`

        :param split: Split lines on the whitespace parts if `True`, or on
                      whatever is passed if another non-zero value is given.
        :type split: :class:`bool` or whatever is taken by :func:`str.split`

        :param headless: Skip the first line if `True`, or the amount specified
                         if an :class:`int` is given.
        :type headless: :class:`bool` or :class:`int`

        :param tailless: Skip the last line if `True`, or the amount specified
                         if an :class:`int` is given.
        :type tailless: :class:`bool` or :class:`int`

        :param _maximum: Skips any lines longer than the given length.
        :type _maximum: :class:`int`

        :returns: A generator.
    '''

    file = file or []

    if headless:
        file = _headless(file, count=int(headless))

    if tailless:
        file = _tailless(file, count=int(tailless))

    for line in file:
        if strip:
            strip_argument = None if strip is True else strip
            line = line.strip(strip_argument)

        if line or not skip:
            if split:
                split_argument = None if split is True else split
                line = line.split(split_argument)

            yield line


class _chain(object):
    def __init__(self, instance):
        self.instance = instance
        self.chaining = None

    def __enter__(self):
        self.chaining = self.instance.chain
        self.instance.chain = True

    def __exit__(self, _, __, ___):
        self.instance.chain = self.chaining


class directory(object):

    '''
        Adapted from: http:stackoverflow.com/a/13197763

        Context manager for changing the current working directory.
    '''

    def __init__(self, destination, make=False):
        '''
            :param destination: The path of the directory to change to. Pass
                                whatever :func:`os.chdir` can take.
            :type destination: str

            :param make: If :param:`destination` doesn't exist, it and any
                         required parents will be created using
                         :func:`os.makedirs`.
            :type make: bool
        '''

        self.destination = os.path.expanduser(destination)
        self.make = make
        self.start = None

    def __enter__(self):
        self.start = os.getcwd()

        if os.name == 'nt' and _drive_reference(self.destination):
            destination = '{}{}'.format(self.destination, os.sep)
        else:
            destination = self.destination

        try:
            os.chdir(destination)
        except FileNotFoundError:
            if self.make:
                os.makedirs(destination)
                os.chdir(destination)
            else:
                raise

    def __exit__(self, _, __, ___):
        if self.start:
            os.chdir(self.start)


class StorageNotAllowed(Exception):
    '''
        Raised when a :class:`werkzeug.FileStorage` instance is passed to
        :func:`File.create` which has an extension that is not allowed.
    '''

    pass


class All(object):

    '''
        From Flask-Uploads.

        This can be used to allow all extensions when passing
        :class:`werkzeug.FileStorage` instances to :func:`File.create`.
    '''

    def __contains__(self, _):
        return True


class Path(object):
    def __init__(self, path=None, posix=None, chain=None):
        '''
            Path interaction.

            :param path: The starting path to work with.
            :type path: :class:`Path` instance if :param:`chain` is set to
                        `True`, otherwise :class:`str`. The default is an empty
                        string.

            :param posix: The path will be worked with as though it is for a
                          posix system if :param:`posix` is set to `True`,
                          otherwise it will be for DOS. I.e. `/` separators if
                          :param:`posix` is `True`, `\\` otherwise. The default
                          is the system's default.
            :type posix: :class:`bool`

            :param chain: Will have most operations return instances of
                          :class:`Path` if :param:`chain` is True, otherwise
                          THe :class:`str` path will be returned. This is for
                          performing operations such as:
                          `path.join(y).normalise().extension('md')`. The
                          default is `False`.
            :type chain: :class:`bool`

            :returns: An instance of :class:`Path` is :param:`chain` is set to
                      `True`, otherwise the path as a :class:`str`.
        '''

        self._init_attribute(path, 'posix', posix, self._posix_os)
        self.separator = posixpath.sep if self.posix else os.sep
        self._init_attribute(path, 'chain', chain, False)
        self._init_attribute(path, 'path', None, path or '')

    def __nonzero__(self):
        return bool(self.path)

    def __len__(self):
        return len(self.path)

    def __eq__(self, other):
        return self._compare_equality(other)

    def __ne__(self, other):
        return not self._compare_equality(other)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.path)

    @property
    def _posix_os(self):
        return os.name == 'posix'

    def _init_attribute(self, path, attribute, given, default):
        if given is not None:
            value = given
        else:
            value = getattr(path, attribute, default)

        setattr(self, attribute, value)

    @property
    def _kwargs(self):
        return {'posix': self.posix, 'chain': self.chain}

    def _compare_equality(self, other):
        return self.path == getattr(other, 'path', other)

    def _returnable(self, path):
        if self.chain:
            if hasattr(path, 'path'):
                returning = path
            else:
                returning = self.__class__(path, **self._kwargs)

        else:
            # # getattr shouldn't be needed; only ever pass it a path
            returning = getattr(path, 'path', path)

        return returning

    def _plant(self, path):
        if path.startswith(self.separator):
            planted_path = path
        else:
            planted_path = self.__class__(
                self.separator,
                posix=self.posix,
                chain=False
            ).join(path)

        return planted_path

    def _split_extension(self, full=True):
        ancestry, name = self.split(maximum=1)

        if name.startswith(os.path.extsep) and name.count(os.path.extsep) == 1:
            name_base = ''
            extension = name
        else:
            name_base, extension = os.path.splitext(name)

        if full:
            if ancestry and name_base:
                base = self.separator.join([ancestry, name_base])
            elif ancestry:
                base = ancestry
            else:
                base = name_base

        else:
            base = name_base

        return (base, extension)

    def join(self, paths, *args):
        '''
            Join the given path with :param:`self.path`, separating with the
            path separator determined by :param:`self.posix`.

            :param paths: The paths to be used in the join.
            :type paths: :class:`str`s or :class:`Path`, either an iterable of
                         these or an individual.

            :param args: Used in the same way as :param:`paths`.
            :type args: The same as :param:`paths`, except they can't be lists
                        or equivalent.

            :returns: Chainable, see :param:`self.chain`.
        '''

        all_paths = array(paths or [], deque=True)
        all_paths.extend(args)
        if self.path:
            all_paths.insert(0, self.path)

        strung_paths = []
        for path in all_paths:
            if path:
                strung_paths.append(strand(getattr(path, 'path', path)))

        stripped_paths = []
        for index, path in enumerate(strung_paths):
            if index > 0 and path.startswith(_SEPARATORS):
                stripped_path = self.__class__(
                    path,
                    posix=self.posix,
                    chain=False
                ).strip(side='left')

            else:
                stripped_path = path

            stripped_paths.append(stripped_path)

        joined_path = ''
        for index, path in enumerate(stripped_paths):
            if index == 0 or joined_path.endswith(_SEPARATORS):
                separator = ''
            else:
                separator = self.separator

            joined_path = separator.join((joined_path, path))

        return self._returnable(joined_path)

    def normalise(self, collapse=True, resolve=True, absolute=False):
        '''
            Normalises :param:`self.path`, uniforming the path separators. and
            removing current and parent directory identifiers.

            :param collapse: Removes current and parent directory identifer,
                             i.e. '.' and '..' respectively.
            :type collapse: :class:`bool`

            :param resolve: If :param:`collapse` is also True, 'abc/../123'
                            becomes '123'.
            :type resolve: :class:`bool`

            :param absolute: Ensures the resulting path is rooted by inserting
                             the path separator at the beginning, determined by
                             :param:`self.posix`.
            :type absolute: :class:`bool`

            :returns: Chainable, see :param:`self.chain`.
        '''

        if collapse and (len(self.path) > 1 or self.path not in _SEPARATORS):
            segments = self.split(maximum=None)
            filtered_segments = []

            for segment in segments:
                if segment in (os.curdir, os.pardir):
                    if resolve and segment == os.pardir:
                        pop(filtered_segments, -1)

                else:
                    filtered_segments.append(segment)

            # # dry
            first_segment = pop(segments, 0, '')
            first_filtered_segment = pop(filtered_segments, 0, '')
            last_segment = pop(segments, -1, '')
            last_filtered_segment = pop(filtered_segments, -1, '')

            if first_segment.startswith(_SEPARATORS):
                first_filtered_segment = ''.join((
                    self.separator,
                    first_filtered_segment
                ))

            if last_segment.endswith(_SEPARATORS):
                last_filtered_segment = ''.join((
                    last_filtered_segment,
                    self.separator
                ))
            # # enddry

            normal_path = self.__class__(
                first_filtered_segment,
                posix=self.posix,
                chain=False
            ).join(
                filtered_segments,
                last_filtered_segment
            )

        else:
            both_separators = _DOS_SEPARATOR*2 + _POSIX_SEPARATOR
            both_separators_regex = r'[{}]+'.format(both_separators)

            if self.separator == _POSIX_SEPARATOR:
                separator = self.separator
            else:
                separator = self.separator * 2

            normal_path = re.sub(both_separators_regex, separator, self.path)

        path = self._plant(normal_path) if absolute else normal_path

        return self._returnable(path)

    # # lstrip & rstrip sugar
    def strip(self, side='both'):
        '''
            Removes both of the path separators from the sides of
            :param:`self.path`.

            :param side: Which side of :param:`self.path` to trim.
            :type side: :class:`str`; 'both', 'left' or 'right'

            :returns: Chainable, see :param:`self.chain`.
        '''

        side_extract = side[0:1].lower()
        strip_formatter = side_extract if side_extract in ('l', 'r') else ''
        stripper = getattr(self.path, '{}strip'.format(strip_formatter))
        separator = _POSIX_SEPARATOR + _DOS_SEPARATOR
        stripped = stripper(separator)

        return self._returnable(stripped)

    # # lsplit & rsplit sugar
    def split(self, maximum=1):
        '''
            Splits :param:`self.path` with both path separators. If
            :param:`self.path` starts or ends with a path separator, this one
            is ignored.

            :param full: Splits on every path separator if `True`, otherwise
                         just the first, starting from the right.
            :type full: :class:`bool`

            :returns: :class:`list` if :param:`full` is `True`, otherwise
                      :class:`tuple`.
        '''

        side = 'both' if maximum is None else 'right'
        maximum = -1 if maximum is None else maximum

        with _chain(self):
            normalised = self.strip(side=side).normalise(collapse=False)

        split = normalised.path.rsplit(self.separator, maximum)

        if maximum == 1 and len(split) == 1:
            split.insert(0, '')

        return split

    def simplify(self, errors='ignore'):
        '''
            Normalises :param:`self.path` to contain only 'standard' (i.e.
            unaccented) characters. E.g. 'café' becomes 'cafe'.

            :param errors: Passed to :func:`str.encode`, see its help for more
                           details.

            :returns: Chainable, see :param:`self.chain`.
        '''

        normaliser = unicodedata.normalize('NFKD', self.path)
        simplified_path_binary = normaliser.encode('ascii', errors)
        simplified_path = simplified_path_binary.decode('utf-8')

        return self._returnable(simplified_path)

    def parent(self):
        '''
            Returns :param:`self.path` without the last segment. E.g.
            `/abc/123` would return as `/abc`.
        '''

        base_path = self.split(maximum=1)[0]

        return self._returnable(base_path)

    def name(self, split=False):
        '''
            Returns the last segment of :param:`self.path`. E.g. `/123/abc.md`
            would return as `abc.md`.

            :param split: Returns the name split at its extension. E.g.
                          `/123/abc.md` would return as `('abc', '.md')`.
            :type split: `bool`

            :returns: :class:`tuple` if :param:`split` is `True`, otherwise
                      :class:`str`.
        '''

        if split:
            name = self._split_extension(full=False)
        else:
            name = self.split(maximum=1)[1]

        return name

    def base(self, full=False):
        '''
            Returns `self.path`'s name, minus the extension. E.g. `/123/abc.md`
            would be returned as `abc`.

            :param full: Preserves the path preceding the basename. E.g.
                         `/123/abc.md` would be returned as `/123/abc`.
            :type full: :class:`bool`

            :returns: Chainable if :param:`full` is `True`, see
                      :param:`self.chain` for details. Otherwise, :class:`str`.
        '''

        if full:
            with _chain(self):
                base = self.strip(side='right')._split_extension(full=True)[0]

            returning = self._returnable(base)

        else:
            returning = self.name(split=True)[0]

        return returning

    def extension(self, identifier=None):
        '''
            Either returns or sets `self.path`'s extension.

            :param identifier: If given, it will set `self.path`'s extension to
                               the given extension and return the resulting
                               path.
            :type identifier: :class:`str`

            :returns: Chainable if :param:`identifier` is not given, see
                      :param:`self.chain` for details. Otherwise, :class:`str`.
        '''

        if identifier:
            # # use getattr(x, y, x) instead of _chain, here and elsewhere
            # # where it is used when self.method's return is not certain
            with _chain(self):
                base_path = self.base(full=True).path

            bare_identifier = identifier.strip(os.path.extsep)
            full_identifier = '{}{}'.format(os.path.extsep, bare_identifier)
            extended_path = '{}{}'.format(base_path, full_identifier)
            returning = self._returnable(extended_path)

        else:
            extension = self.name(split=True)[1]
            returning = extension

        return returning
