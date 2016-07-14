- document
- unit tests
- change things like `File._descendant/_descendants_map`'s `instance`, `full`,
  etc keyword parameters to a `method` keyword parameter taking
  'instance/full/'
- have compress support both includes and excludes; remove the 'files'
  parameter
- improve `compress`' `update` ability
- remove `compress`' `inside` parameter; allow `name` to be a relative path
- implement a `limit` for `feed`
- implement a `decompress` function in `utilities` and method on `File`
- merge `Path` with `pathlib`
- remove redundant unit tests
- allow optionally separate limits for files and directories in
  `File.properties`
- have unit tests use `tempfile.TemporaryDirectory`
- have `Path.split` not change the separator
- use a recursive os.scandir instead of os.walk
- support `File('./../.././../file')`
- dry in tests, particularly TestPath
- implement `.__contains__` for `Path`
- implement `.__contains__`, `.__iter__`, `.__getitem__`, `.__setitem__`,
  `.__delitem__` and `.__index__` and  for `File`
- rename `hide_extensions`; ambiguous
