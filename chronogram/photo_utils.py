from aiogram.types.input_file import FSInputFile
from aiogram.types.photo_size import PhotoSize
import os
import io
from PIL import Image

from config import config


class PhotoReader:
    def __init__(self, photo: list[PhotoSize], file_name):
        self.photo = photo
        self.file_name = file_name

    async def get_blob_image(self):
        file_info = await config.BOT.get_file(self.photo[-1].file_id)
        data = (await config.BOT.download_file(file_info.file_path)).read()
        return io.BytesIO(data).getvalue()

    async def load_image_from_tg(self):
        file_info = await config.BOT.get_file(self.photo[-1].file_id)
        img = Image.open(io.BytesIO((await config.BOT.download_file(file_info.file_path)).read()))
        img.save(self.file_name)
        return FSInputFile(self.file_name)

    async def delete(self):
        os.remove(self.file_name)
