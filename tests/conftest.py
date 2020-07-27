import pytest
import pathlib


@pytest.fixture(scope='session')
def videofile(tmp_path_factory) -> pathlib.Path:
    videofile = tmp_path_factory.mktemp('subfinder_test') / 'Yellowstone.2018.S03E04.1080p.WEB.H264-METCON.mkv'
    videofile.touch()
    return videofile