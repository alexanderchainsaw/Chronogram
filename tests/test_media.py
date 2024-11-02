from aiogram.types.input_file import FSInputFile


def test_inbox_picture_present():
    assert FSInputFile('media/inbox_pic.jpg')
