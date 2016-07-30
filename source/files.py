import filecmp
import fnmatch
import functools
import os
import posixpath
import ntpath
import re
import shutil

from . import utilities



class File:

    '''
        File interactions.

        The size, in bytes, of an instance can be returned with
        `len(file_instance)`.

        Instances can be used where a :class:`bool` is required, such as:
        `if file: ...` or `bool(file)`. It will evaluate to `True` if the
        referenced file or directory exists.

        Two instances can be compared using the `==`, `!=`, `>`, `<`, `>=`
        and `<=` operators, such as: `file_1 == file_2` or `file_1 > file_2`.
        The `>`, `<`, `>=` and `<=` operators use the file's or directory's
        size (in bytes) to make the comparison. In the case of a file/directory
        mismatch, directories are always considered greater than files.

        When comparing equality with the `==` and `!=` operators,
        :mod:`filecmp` is used with its `shallow` argument set to `True`, and
        the comparison will be recursive (i.e. subdirectories will also be
        compared). To do something else, such as a non-recursive, deep
        inequality comparison, for example, use `instance_1.compare(instance_2,
        recurse=False, shallow=False, inverse=True)`. See :func:`File.compare`
        for more details.
    '''

    # # break into smaller functions
    def __init__(self, path='/', root=None, match=False):
        '''
            :param path: Should always be given as a POSIX path (such as those
                         used on GNU/Linux, BSD, Mac OS X, etc). That is, paths
                         that are separated with '/', and where the first
                         directory in the tree is referred to as '/'. On a
                         DOS/WIndows system, `C:\\files\\some.txt` would here
                         be referred to as `/files/some.txt`, unless
                         :param:`root` has been changed.

                         Relative paths can be given, see below at
                         :param:`relative` for details.
            :type path: :class:`str` or :class:`File` instances.

            :param root: This is the real path that sits beneath the given
                         :param:`path`. This will default to '/' on POSIX
                         systems (e.g. GNU/Linux, BSD, Mac OS X, etc) and
                         something like 'C:\' on a DOS/Windows system. The
                         default is determined by `os.path.realpath(os.sep)`.

                         This means any path given to this instance, or any
                         instances or paths returned by it will always be below
                         this point. For example, if this is set to
                         `/home/bob`, a :param:`path` set to `/files/` will
                         actually reference `/home/bob/files/` and any children
                         of that instance will refer to themselves as something
                         like `/files/some.txt` but actually point to
                         `/home/bob/files/some.txt`.

                         If a :class:`File` instance is given to :param:`path`,
                         this will be ignored and taken from that instance.
            :type root: :class:`str`.

            :param match: This causes the instance to search for an existing
                          file that begins with the given path. For example, if
                          this parameter is enabled, `/avatar` is passed as
                          :param:`path` and only `/avatar.png` exists, the
                          instance will set its path to `/avatar.png` instead.
                          If multiple possibilities exist, the first found
                          alphabetically is chosen. If no match is found,
                          :param:`path` will not be changed.
            :type match: :class:`bool`
        '''

        if hasattr(root, 'path'):
            self.root = root.path
            self._root_instance = root
        else:
            if root:
                self.root = root
            else:
                relative = (
                    path.startswith(os.curdir) or
                    not path.startswith((posixpath.sep, ntpath.sep))
                )

                if relative:
                    root_reference = os.curdir
                    path = path.lstrip(os.curdir)
                else:
                    root_reference = os.sep

                self.root = os.path.realpath(root_reference)

            self._root_instance = utilities.Path(self.root, chain=True)

        real_path = getattr(path, 'path', path)
        path_instance = utilities.Path(
            real_path,
            posix=True,
            chain=True
        ).strip().normalise(absolute=True)

        path_directory, path_name = path_instance.split(maximum=1)
        fixed_directory = path_directory or posixpath.sep
        self._parent_path_instance = utilities.Path(
            fixed_directory,
            posix=True,
            chain=True
        )

        # # # use glob
        if match:
            full_directory_instance = self._root_instance.join(fixed_directory)
            full_directory = full_directory_instance.path

            if os.path.isdir(full_directory):
                files = os.listdir(full_directory)

                for file in files:
                    if file.startswith(path_name):
                        path_name = file
                        path_instance = self._parent_path_instance.join(
                            path_name
                        )

                        break

        self.name = path_name
        self._path_instance = path_instance
        self.path = self._path_instance.path
        self.parent_path = self._parent_path_instance.path
        full_path_instance = self._root_instance.join(self.path).normalise()
        self._full_path_instance = full_path_instance
        self.full_path = self._full_path_instance.path
        full_parent_path_instance = self._root_instance.join(self.parent_path)
        self._full_parent_path_instance = full_parent_path_instance.normalise()
        self.full_parent_path = self._full_parent_path_instance.path

    def __bool__(self):
        return self._existence

    def __len__(self):
        length = self._size(recurse=True, limit=None)

        return -1 if length is None else length

    def __eq__(self, other):
        return self.compare(other, method='equality')

    def __ne__(self, other):
        return self.compare(other, method='equality', inverse=True)

    def __lt__(self, other):
        return self.compare(other, method='sizes') == -1

    def __gt__(self, other):
        return self.compare(other, method='sizes') == 1

    def __le__(self, other):
        return self.compare(other, method='sizes') in (-1, 0)

    def __ge__(self, other):
        return self.compare(other, method='sizes') in (0, 1)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.full_path)

    @property
    def _existence(self):
        return os.path.exists(self.full_path)

    @property
    def _directory(self):
        return os.path.isdir(self.full_path)

    @property
    def _file(self):
        return os.path.isfile(self.full_path)

    @property
    def _empty(self):
        if self._directory:
            returning = not self._count_lines(limit=1)

        elif self._file:
            returning = self._size() == 0

        else:
            returning = None

        return returning

    def _instance(self, path, class_=None, **kwargs):
        if isinstance(path, self.__class__):
            instance = path
        else:
            class_ = class_ or self.__class__
            instance = class_(
                path=path,
                root=self._root_instance,
                **kwargs
            )

        return instance

    def _replicate(self, other):
        for attribute, value in other.__dict__.items():
            setattr(self, attribute, value)

    def _size(self, recurse=True, limit=None):
        if self._existence:
            if self._directory:
                size = 0

                with utilities.directory(self.full_path):
                    for path, _, files in os.walk(os.curdir):
                        for file in files:
                            file_path = self._full_path_instance.join(
                                path,
                                file
                            ).normalise().path

                            try:
                                size += os.path.getsize(file_path)
                            except PermissionError:
                                pass

                            if limit and size >= limit:
                                size = True
                                break

                        if not recurse or (limit and size is True):
                            break

            else:
                size = os.path.getsize(self.full_path)

            return size

    # # break up into smaller functions
    def _count(self, recurse=True, separate=False, limit=None,
               limit_files=True, limit_directories=True):

        if self._existence:
            if self._directory:
                directory_count = 0
                file_count = 0
                combined_count = 0

                both_limited = limit_files and limit_directories
                both_not_limited = not limit_files and not limit_directories
                combined_limitation = both_limited or both_not_limited
                reached_limit = False

                for _, directories, files in os.walk(self.full_path):
                    directories_count = len(directories)
                    files_count = len(files)

                    directory_count += directories_count
                    file_count += files_count
                    combined_count += directories_count + files_count

                    if limit:
                        if combined_limitation:
                            limited = combined_count
                        elif limit_files:
                            limited = file_count
                        elif limit_directories:
                            limited = directory_count

                        reached_limit = limited >= limit

                    if not recurse or reached_limit:
                        break

                if reached_limit:
                    count = True

                elif separate:
                    count = {
                        'directories': directory_count,
                        'files': file_count
                    }

                else:
                    count = combined_count

            else:
                count = 1

            return count

    def _count_lines(self, limit=None, strip=False, skip=False):
        if self._file:
            content = self.read(generator=True, lines=True)
            feed = utilities.feed(content, skip=skip, strip=strip, split=False)
            length = 0

            for _ in feed:
                length += 1

                if limit and length == limit:
                    length = True
                    break

                return length

    def _compare_sameness(self, other):
        # # fix needed; see the second-to-last paragraph here:
        # # http:lucumr.pocoo.org/2010/1/7/pros-and-cons-about-python-3/
        return self is other or self.full_path == other.full_path

    @staticmethod
    def _compare_likeness(self_likeness, other_likeness):
        if self_likeness and not other_likeness:
            result = 1
        elif not self_likeness and other_likeness:
            result = -1
        else:
            result = 0

        return result

    def _compare_lengths(self, other, count=False, **kwargs):
        length = 0

        if not self._compare_sameness(other):
            self_exists = self._existence
            existence_comparison = self._compare_likeness(
                self_exists,
                other._existence
            )

            if existence_comparison:
                length = existence_comparison
            elif self_exists:
                self_is_directory = self._directory
                direction_comparison = self._compare_likeness(
                    self_is_directory,
                    other._directory
                )

                if direction_comparison:
                    length = direction_comparison
                else:
                    if count:
                        kwargs.update({'length': True})
                    else:
                        kwargs.update({'size': True})

                    self_length = self.property(**kwargs)
                    other_length = other.property(**kwargs)

                    if self_length > other_length:
                        length = 1
                    elif self_length < other_length:
                        length = -1

        return length

    def _compare_sizes(self, size_recurse=True, **kwargs):
        return self._compare_lengths(
            count=False,
            size_recurse=size_recurse,
            **kwargs
        )

    def _compare_counts(self, count_recurse=True, count_separate=False,
                        **kwargs):

        return self._compare_lengths(
            count=True,
            count_recurse=count_recurse,
            count_separate=count_separate,
            **kwargs
        )

    def _compare_equality_directory(self, comparator, shallow=True,
                                    recursive=True, inverse=False):

        truth = not inverse
        result = (
            not comparator.diff_files and
            not comparator.left_only and
            not comparator.right_only
        ) is truth

        if result:
            if shallow:
                result = not comparator.common_funny
            else:
                result = filecmp.cmpfiles(
                    comparator.left,
                    comparator.right,
                    comparator.common_files,
                    shallow=False
                ) is truth

        # for equality, all must be equal
        # for inequality, most can be equal
        if recursive and ((not result and not truth) or (result and truth)):
            for sub_comparator in comparator.subdirs.values():
                result = self._compare_equality_directory(
                    sub_comparator,
                    shallow=shallow,
                    recursive=recursive,
                    inverse=inverse
                )

                if (result and not truth) or (not result and truth):
                    break

        return result

    def _compare_equality(self, other, shallow=True, recurse=True,
                          inverse=False):

        result = True

        if self._existence and other._existence:
            self_is_directory = self._directory
            other_is_directory = other._directory

            if self_is_directory and other_is_directory:
                comparator = filecmp.dircmp(self.full_path, other.full_path)
                result = self._compare_equality_directory(
                    comparator,
                    shallow=shallow,
                    recursive=recurse,
                    inverse=inverse
                )

            elif not self_is_directory and not other_is_directory:
                result = filecmp.cmp(
                    self.full_path,
                    other.full_path,
                    shallow=shallow
                ) is not inverse

            else:
                result = False

        return result

    def _riter(self, blocks=False, binary=False, length=16384):
        # # compare and merge with http:stackoverflow.com/a/260433
        # # test if automatically skips blank lines; `if len(lines[index]):`

        '''
            From: http:stackoverflow.com/a/23646049

            A generator that returns the lines of the file in reverse order.
        '''

        binary = binary and blocks
        mode = 'r{}'.format('b' if binary else '')
        offset = 0

        if not blocks:
            segment = None

        with open(self.full_path, mode) as opened:
            opened.seek(0, os.SEEK_END)
            file_size = remaining_size = opened.tell()

            while remaining_size > 0:
                offset = min(file_size, offset + length)
                opened.seek(file_size - offset)

                read_amount = min(remaining_size, length)
                content = opened.read(read_amount)
                remaining_size -= length

                if blocks:
                    yield content
                else:
                    lines = content.split('\n')

                    # the first line of the buffer is probably not a complete
                    # line so we'll save it and append it to the last line of
                    # the next buffer we read
                    if segment is not None:
                        # if the previous chunk starts right from the beginning
                        # of line do not concact the segment to the last line
                        # of new chunk instead, yield the segment first
                        if content[-1] is not '\n':
                            lines[-1] += segment
                        else:
                            yield segment

                    segment = lines[0]

                    for index in range(len(lines) - 1, 0, -1):
                        if len(lines[index]):
                            yield lines[index]

                    # don't yield None if the file was empty
                    if segment is not None:
                        yield segment

    @staticmethod
    def _resolution(path, count):
        base, name = path.split(maximum=1)
        base_name, extension = os.path.splitext(name)
        proposed_name = '{}_{}{}'.format(base_name, count, extension)

        return utilities.Path(base, chain=True).join(proposed_name)

    def _resolve(self):

        '''
            This method was adapted from Flask-Uploads.

            If a file with `self.name` already exists, this method can be
            called to resolve the conflict. It returns a File instance with the
            resolved file name.

            To resolve the conflict, this method splits `self.name` into the
            name and extension, adds a suffix to the name consisting of an
            underscore and an incremented number starting with `1`, and tries
            that until it finds one that doesn't exist.
        '''

        if self._existence:
            count = 1
            path_instance = self._full_path_instance
            proposed_path_instance = self._resolution(path_instance, count)

            while os.path.exists(proposed_path_instance.path):
                count += 1
                proposed_path_instance = self._resolution(path_instance, count)

            resolved_name = proposed_path_instance.split(maximum=1)[1]
            resolved = self.sibling(resolved_name, instance=True)

        else:
            resolved = self

        return resolved

    def _uniquify(self, directories=False):
        base_name, extension = os.path.splitext(self.name)

        for file in os.listdir(self.full_parent_path):
            file_base_name, file_extension = os.path.splitext(file)
            matching_base_name = file_base_name == base_name

            if matching_base_name and file_extension != extension:
                file_path = self._parent_path_instance.join(file).path
                file_instance = self._instance(file_path)

                if directories or file_instance._file:
                    file_instance.remove()

    def _preoverwrite(self, level=False):
        destination = self

        if destination._existence:
            level_integer = 0 if level is None else int(level)

            if level_integer > 0:
                destination.remove()

                if level_integer > 1:
                    directories = level_integer > 2
                    destination._uniquify(directories=directories)

            elif level_integer == 0:
                destination = destination._resolve()

        return destination

    # adapted from: Flask-Uploads' save method
    def _prewrite(self, storage, extend=True, allowed=None):
        name = None

        if self._directory or not self.name:
            storage_name_instance = utilities.Path(
                storage.filename,
                chain=True,
            )

            name = storage_name_instance.strip().normalise().simplify().name()
            other = True

        elif self.name:
            name = self.name
            other = False

        if not name:
            name = utilities.salt(4)
            other = True

        storage_extension = os.path.splitext(storage.filename)[1]

        if not storage_extension.lstrip('.').lower() in allowed:
            # # need to remove temp file?
            raise utilities.StorageNotAllowed

        if extend:
            if name.endswith('.'):
                name = name.rstrip('.')

            name_instance = utilities.Path(name, chain=False)
            extension = name_instance.extension()
            pretake_storage_extension = not extension and storage_extension

            if pretake_storage_extension and len(storage_extension) > 1:
                name = name_instance.extension(storage_extension)

        if other:
            # # necessary to call bearer for instance?
            bearer = self._bearer(instance=True)
            destination = bearer.child(name, instance=True)
        else:
            destination = self

        return (destination, storage.stream)

    def _checksum_children(self, **kwargs):
        children = self.children(
            recursive=True,
            separate=True,
            files=True,
            directories=False,
            instances=True,
            hide=False
        )

        for child in children:
            yield child._checksum(**kwargs)

    def _checksum(self, algorithm='crc32'):
        if self._directory:
            content = self._checksum_children(algorithm=algorithm)
        else:
            content = self.read(
                generator=True,
                blocks=True,
                binary=True,
                reverse=False,
                length=65536
            )

        return utilities.checksum(content, algorithm=algorithm)

    def _bearer(self, instance=False, full=False):
        if self._directory:
            if instance:
                returning = self
            elif full:
                returning = self.full_path
            else:
                returning = self.path

        else:
            returning = self.parent(instance=instance, full=full)

        return returning

    def _director(self, sibling=False, **kwargs):
        is_directory = self._directory

        if sibling and (is_directory or self._file):
            get_directory = self.parent
        elif not sibling and is_directory:
            get_directory = self._bearer
        else:
            get_directory = None

        if get_directory:
            return get_directory(**kwargs)

    def _descendant(self, path, sibling=False, instance=False, full=False):
        parent = self._director(sibling=sibling, instance=False, full=False)
        if parent:
            child = utilities.Path(parent, posix=True, chain=False).join(path)

            if instance:
                returning = self._instance(child)
            elif full:
                returning = self._root_instance.join(child).normalise().path
            else:
                returning = child

            return returning

    @staticmethod
    def _descendants_filter_hidden(names, hidden):
        filtered = []

        for name in names:
            matches = [fnmatch.fnmatch(name, pattern) for pattern in hidden]

            if not any(matches):
                filtered.append(name)

        return filtered

    # # # exclude=True/[]/'', True excludes self
    def _descendants_filter(self, names, hide=False, glob=None, regex=None,
                            hide_extensions=None):

        if hide:
            names = self._descendants_filter_hidden(names, hide_extensions)

        if glob:
            names = [name for name in names if fnmatch.fnmatch(name, glob)]

        if regex:
            names = [name for name in names if re.match(regex, name)]

        return names

    def _descendants_map(self, relative_root_instance, names, instances=False,
                         paths=False, relatives=False, fulls=False):

        if instances or paths or relatives or fulls:
            names = [relative_root_instance.join(name) for name in names]

        if instances or paths or fulls:
            names = [self._path_instance.join(name) for name in names]

        if instances:
            names = [self._instance(name) for name in names]
        elif fulls:
            root_instance = self._root_instance
            names = [root_instance.join(n).normalise().path for n in names]

        return names

    def _descendants_milter(self, relative_root_instance, names,
                            instances=False, paths=False, relatives=False,
                            fulls=False, **kwargs):

        list_filtered = self._descendants_filter(names, **kwargs)

        return self._descendants_map(
            relative_root_instance,
            list_filtered,
            instances=instances,
            paths=paths,
            relatives=relatives,
            fulls=fulls
        )

    def _descendants(self, siblings=False, recursive=False, separate=False,
                     directories=None, files=None, limit=None, offset=None,
                     **kwargs):

        root_file = self._director(instance=True, sibling=siblings)
        offset_limit = limit + offset if limit and offset else limit
        count = 0

        with utilities.directory(root_file.full_path):
            for list_root, directory_list, file_list in os.walk('.'):
                count += 1

                if offset and offset >= count:
                    continue

                if offset_limit and offset_limit < count:
                    break

                content = {}
                relative_path_stripped = list_root.lstrip('.')
                relative_path_instance = utilities.Path(
                    relative_path_stripped,
                    chain=True,
                    posix=True
                ).normalise()

                just_files = files and not directories
                just_directories = directories and not files
                separate = separate or (just_files or just_directories)

                if separate:
                    if directories:
                        content.update({
                            'directories': root_file._descendants_milter(
                                relative_path_instance,
                                directory_list,
                                **kwargs
                            )
                        })

                    if files:
                        content.update({
                            'files': root_file._descendants_milter(
                                relative_path_instance,
                                file_list,
                                **kwargs
                            )
                        })

                else:
                    content.update({
                        'content': root_file._descendants_milter(
                            relative_path_instance,
                            directory_list + file_list,
                            **kwargs
                        )
                    })

                yielding = {'path': relative_path_instance.path}
                yielding.update(content)

                yield yielding

                if not recursive:
                    break

    def properties(self, existence=False, directory=False, file=False,
                   empty=False, size=False, count=False, modified=False,
                   accessed=False, created=False, checksum=False,
                   size_recurse=True, size_limit=None, count_recurse=True,
                   count_separate=True, count_limit=None,
                   count_limit_files=True, count_limit_directories=True,
                   checksum_algorithm='crc32'):

        property_dictionary = {}
        time_property_dictionary = {}

        if existence:
            property_dictionary.update({'existence': self._existence})

        if directory:
            property_dictionary.update({'directory': self._directory})

        if file:
            property_dictionary.update({'file': self._file})

        if empty:
            property_dictionary.update({'empty': self._empty})

        if size:
            property_dictionary.update({'size': self._size(
                recurse=size_recurse,
                limit=size_limit
            )})

        if count:
            property_dictionary.update({'count': self._count(
                recurse=count_recurse,
                separate=count_separate,
                limit=count_limit,
                limit_files=count_limit_files,
                limit_directories=count_limit_directories
            )})

        if checksum:
            for algorithm in utilities.array(checksum_algorithm):
                if algorithm:
                    checksum_key = 'checksum.{}'.format(algorithm)
                    checksum_value = self._checksum(algorithm=algorithm)
                    property_dictionary.update({checksum_key: checksum_value})

        if modified:
            time_property_dictionary.update({
                'modified': os.path.getmtime(self.full_path)
            })

        if accessed:
            time_property_dictionary.update({
                'accessed': os.path.getatime(self.full_path)
            })

        if created:
            time_property_dictionary.update({
                'created': os.path.getctime(self.full_path)
            })

        if time_property_dictionary:
            if len(time_property_dictionary) > 1:
                update_dictionary = {'times': time_property_dictionary}
            else:
                update_dictionary = time_property_dictionary

            property_dictionary.update(update_dictionary)

        if len(property_dictionary) == 1:
            returning = list(property_dictionary.values())[0]
        else:
            returning = property_dictionary

        return returning

    def property(self, **kwargs):
        return self.properties(**kwargs)

    def compare(self, other, method='equality', **kwargs):
        if method == 'equality':
            comparison = self._compare_equality(other, **kwargs)
        elif method == 'sizes':
            comparison = self._compare_sizes(other, **kwargs)
        elif method == 'counts':
            comparison = self._compare_counts(other, **kwargs)

        return comparison

    def plant(self):
        if not os.path.exists(self.full_parent_path):
            return self.parent(instance=True).write(directory=True)

    def write(self, content=None, directory=False, overwrite=False,
              lines=False, binary=False, extend=True, allowed=None,
              length=16384):

        '''
            :param content: Can be an instance of
                            :class:`werkzeug.FileStorage`, otherwise a
                            :class:`str` instance or :class:`bytes` instance
                            can be passed, or an iterator of the last two.

            :param overwrite: Can be 0 (or False), 1 (or True) or 2. 0 will
                              resolve conflicts by appending an underscore and
                              incremented number before the extension until an
                              unused name is found. 2 makes sure the name is
                              unique in the destination regardless of the
                              extension, removing any files that conflict.
        '''

        if hasattr(content, 'filename') and hasattr(content, 'stream'):
            destination, content = self._prewrite(
                content,
                extend=extend,
                allowed=allowed
            )

        else:
            destination = self

        if destination._existence:
            destination = destination._preoverwrite(level=overwrite)
        else:
            destination = destination

        if directory:
            os.makedirs(destination.full_path)
        else:
            append = overwrite == -1 or not content
            initial_mode = 'a{}' if append else 'w{}'
            mode = initial_mode.format('b' if binary else '')
            destination.plant()

            with open(destination.full_path, mode) as storage:
                if hasattr(content, 'read'):
                    shutil.copyfileobj(content, storage, length)
                elif content:
                    writer = storage.writelines if lines else storage.write
                    writer(content)

        return destination if destination._existence else False

    # # method='lines/blocks'
    def read(self, generator=True, lines=False, blocks=False, reverse=False,
             binary=False, length=16384):

        if generator and reverse:
            initial_return = self._riter(
                blocks=not lines if lines else blocks,
                binary=binary,
                length=length
            )

        else:
            mode = 'r{}'.format('b' if binary else '')

            with open(self.full_path, mode) as opened:
                if generator and blocks:
                    # from: http:stackoverflow.com/a/7829658
                    partial = functools.partial(opened.read, length)
                    initial_return = iter(partial, b'')
                elif generator:
                    initial_return = opened
                elif lines:
                    initial_return = opened.readlines()
                else:
                    initial_return = opened.read()

        if not generator and lines and reverse:
            returning = reversed(initial_return)
        else:
            returning = initial_return

        return returning

    def remove(self):
        if self._existence:
            remover = shutil.rmtree if self._directory else os.remove

            return remover(self.full_path)

    def copy(self, path, overwrite=False):
        preliminary_destination = self._instance(path)
        preliminary_destination.plant()
        destination = preliminary_destination._preoverwrite(level=overwrite)

        copier = shutil.copytree if self._directory else shutil.copy2
        copier(self.full_path, destination.full_path)

        return destination if destination._existence else False

    def move(self, *args, **kwargs):
        copied_instance = self.copy(*args, **kwargs)

        if copied_instance:
            self.remove()
            self._replicate(copied_instance)

        return copied_instance

    # # #
    def mirror(self, _r_sync=True):
        pass

    # # pass through update kwarg and all others accepted by compress
    # # overwrite=-1,0,1
    def compress(self, name=None, inside=True, **kwargs):
        if self._existence:
            is_directory = self._directory

            if is_directory:
                files = None
            else:
                files = [self.name]
                inside = False

            bearer = self._bearer(instance=True)
            compressed_name = utilities.compress(
                bearer.full_path,
                name=name,
                inside=inside,
                files=files,
                _update=False,
                include=True,
                **kwargs
            )

            relation = 'child' if inside or not is_directory else 'sibling'
            relater = getattr(bearer, relation)

            return relater(compressed_name, instance=True)

    def singular(self, **kwargs):
        if self._directory:
            returning = self.compress(**kwargs)
        else:
            returning = self

        return returning

    def parent(self, instance=False, full=False):
        if instance:
            returning = self._instance(self.parent_path)
        elif full:
            returning = self.full_parent_path
        else:
            returning = self.parent_path

        return returning

    def child(self, *args, **kwargs):
        return self._descendant(sibling=False, *args, **kwargs)

    def sibling(self, *args, **kwargs):
        return self._descendant(sibling=True, *args, **kwargs)

    def children(self, *args, **kwargs):
        return self._descendants(siblings=False, *args, **kwargs)

    def siblings(self, recurse=False, *args, **kwargs):
        return self._descendants(
            siblings=True,
            recurse=recurse,
            *args,
            **kwargs
        )
