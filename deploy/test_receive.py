import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('receiver', Path(__file__).with_name('receive.py'))
receiver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receiver)
SHA = 'a' * 40


def archive(extra=None):
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode='w:gz') as tar:
        for name, content in [('index.html', b'hello'), ('version.json', json.dumps({'commit': SHA}).encode())]:
            info = tarfile.TarInfo(name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
        if extra:
            tar.addfile(extra)
    return data.getvalue()


class ReceiverTests(unittest.TestCase):
    def test_valid_site(self):
        with tempfile.TemporaryDirectory() as directory:
            receiver.unpack(archive(), Path(directory), SHA)
            self.assertEqual((Path(directory) / 'index.html').read_text(), 'hello')

    def test_rejects_traversal_symlinks_and_absolute_paths(self):
        for name, kind in [('../escape', tarfile.REGTYPE), ('/escape', tarfile.REGTYPE), ('link', tarfile.SYMTYPE)]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                info = tarfile.TarInfo(name)
                info.type = kind
                info.linkname = '/etc/passwd'
                with self.assertRaises(ValueError):
                    receiver.unpack(archive(info), Path(directory), SHA)

    def test_rejects_wrong_revision(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            receiver.unpack(archive(), Path(directory), 'b' * 40)


if __name__ == '__main__':
    unittest.main()
