from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import ClassVar

import piexif


@dataclass
class ImageFileInfo:
    path: Path | None = None
    file_size_bytes: int | None = None
    file_type: str | None = None
    date_time_created: datetime | None = None
    date_time_modified: datetime | None = None
    date_time_original: datetime | None = None

    # class-level constants
    dto_tag: ClassVar[int] = piexif.ExifIFD.DateTimeOriginal

    @classmethod
    def from_path(cls, file_path: str | Path):
        obj = cls(path=Path(file_path))
        obj.reload()
        return obj

    def reload(self):
        self.path = Path(self.path)
        self.file_size_bytes = self.path.stat().st_size
        self.file_type = self.path.suffix.lower()
        self.date_time_created = datetime.fromtimestamp(self.path.stat().st_ctime)
        self.date_time_modified = datetime.fromtimestamp(self.path.stat().st_mtime)
        self.date_time_original = self._get_date_time_original(self.path)

    @staticmethod
    def _get_date_time_original(file_path: Path) -> datetime | None:
        exif_dict = piexif.load(str(file_path))
        if "Exif" in exif_dict and ImageFileInfo.dto_tag in exif_dict["Exif"]:
            dto_text = exif_dict["Exif"][ImageFileInfo.dto_tag].decode("utf-8")
            dto = datetime.strptime(dto_text, "%Y:%m:%d %H:%M:%S")
            return dto
        else:
            return None

    def set_date_time_original(self, new_dto: datetime) -> None:
        # load the exif info
        exif_dict = piexif.load(str(self.path))

        # create a new DateTimeOriginal string from new_datetime
        new_dto_text = new_dto.strftime("%Y:%m:%d %H:%M:%S")

        # save it to the dictionary and write it to the image file
        exif_dict["Exif"][self.dto_tag] = new_dto_text.encode("utf-8")
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, str(self.path))

        # reload image information
        self.reload()


def load_all_image_file_info(image_dir: Path | str, allowed_extensions=(".jpeg", ".jpg")):
    image_dir = Path(image_dir)

    image_file_info_list = []
    for path in Path.iterdir(image_dir):
        if path.is_file() and path.suffix in allowed_extensions:
            image_file_info_list.append(ImageFileInfo.from_path(path))

    return image_file_info_list


def get_new_sequential_date_time_original(
    num_images: int,
    start_datetime: datetime,
    time_between_images: timedelta,
):
    new_image_datetimes = [start_datetime + time_between_images * i for i in range(num_images)]
    return new_image_datetimes
