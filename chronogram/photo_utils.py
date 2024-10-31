from aiogram import Bot
from dotenv import load_dotenv
from aiogram.types.input_file import FSInputFile
from aiogram.types.photo_size import PhotoSize
import os
import io
from PIL import Image


load_dotenv()
bot = Bot(os.getenv('API_TOKEN'))


class PhotoReader:
    def __init__(self, photo: list[PhotoSize], file_name):
        self.photo = photo
        self.file_name = file_name

    async def get_blob_image(self):
        file_info = await bot.get_file(self.photo[-1].file_id)
        data = (await bot.download_file(file_info.file_path)).read()
        return io.BytesIO(data).getvalue()

    async def load_image_from_tg(self):
        file_info = await bot.get_file(self.photo[-1].file_id)
        img = Image.open(io.BytesIO((await bot.download_file(file_info.file_path)).read()))
        img.save(self.file_name)
        return FSInputFile(self.file_name)

    async def delete(self):
        os.remove(self.file_name)