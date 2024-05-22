from __future__ import annotations

import random
import shutil
from pathlib import Path

import yaml
from panda3d.core import Filename, Multifile

TEMP_DIR = Path("./temp")
CONTENT_PACK_FILE_PATH = Path("./Randomized Sounds.mf")
PACK_INFO_TEXT = """[PackInfo]
name=Randomized Sounds
description=Generated with https://github.com/glomatico/ttr-sound-randomizer"""


def get_phase_files(ttr_path: Path | str) -> list[Path]:
    ttr_path = Path(ttr_path) if isinstance(ttr_path, str) else ttr_path
    phase_files = [
        file for file in ttr_path.iterdir() if file.is_file() and file.suffix == ".mf"
    ]
    return phase_files


def get_multifile(multifile_path):
    multifile = Multifile()
    multifile.open_read(multifile_path)
    return multifile


def get_multifile_sound_subfiles_info(
    multifile,
    audio_subfile_type: str,
) -> list[tuple[int, str]]:
    multifile_sound_subfiles_info = []
    for index in range(multifile.get_num_subfiles()):
        subfile_name_split = multifile.get_subfile_name(index).split("/")
        if len(subfile_name_split) == 4:
            if (
                subfile_name_split[1] == "audio"
                and subfile_name_split[2] == audio_subfile_type
                and subfile_name_split[3].endswith(".ogg")
            ):
                multifile_sound_subfiles_info.append(
                    (
                        index,
                        multifile.get_subfile_name(index),
                    )
                )
        else:
            continue
    return multifile_sound_subfiles_info


def save_subfile(multifile, index: int, output_path: Path | str):
    output_path = Path(output_path) if isinstance(output_path, str) else output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    multifile.extract_subfile(
        index,
        output_path / multifile.get_subfile_name(index).split("/")[-1],
    )


def save_dict_as_yaml(yaml_dict: dict, output_file_path: Path | str):
    output_file_path = (
        Path(output_file_path)
        if isinstance(output_file_path, str)
        else output_file_path
    )
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_file_path.write_text(yaml.dump(yaml_dict))


def save_pack_info(pack_info_text: str, output_file_path: Path | str):
    output_file_path = (
        Path(output_file_path)
        if isinstance(output_file_path, str)
        else output_file_path
    )
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_file_path.write_text(pack_info_text)


def create_content_pack(
    to_include: list[Path],
    output_path: Path | str,
):
    output_path = Path(output_path) if isinstance(output_path, str) else output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    multifile = Multifile()
    multifile.open_read_write(output_path)
    for file_path in to_include:
        multifile.add_subfile(
            file_path.name,
            Filename.binaryFilename(file_path),
            6,
        )
        multifile.flush()
    multifile.close()


def main():
    ttr_path = input("Enter the path containing the Toontown Rewritten game files: ")
    phase_files = get_phase_files(ttr_path)
    if not phase_files:
        print("No phase files found in the specified path.")
        return
    sound_yml_dict = {}
    for audio_subfile_type in ("bgm", "dial", "sfx"):
        print(f"Randomizing {audio_subfile_type} audio files...")
        multifile_sound_subfiles_info = []
        for phase_file in phase_files:
            if not phase_file.is_file() or not phase_file.suffix == ".mf":
                continue
            multifile = get_multifile(phase_file)
            _multifile_sound_subfiles_info = get_multifile_sound_subfiles_info(
                multifile,
                audio_subfile_type,
            )
            multifile_sound_subfiles_info.extend(
                _multifile_sound_subfiles_info,
            )
            for index, _ in _multifile_sound_subfiles_info:
                save_subfile(
                    multifile,
                    index,
                    TEMP_DIR,
                )
        multifile_sound_subfiles_info_copy = multifile_sound_subfiles_info.copy()
        for _, subfile_path in multifile_sound_subfiles_info:
            random_index = random.randint(
                0, len(multifile_sound_subfiles_info_copy) - 1
            )
            subfile_path_split = subfile_path.split("/")
            phase_file_name = subfile_path_split[0]
            subfile_name = subfile_path_split[-1].rpartition(".")[0]
            subfile_name_random = (
                multifile_sound_subfiles_info_copy[random_index][1]
                .split("/")[-1]
                .rpartition(".")[0]
            )
            if not sound_yml_dict.get(phase_file_name):
                sound_yml_dict[phase_file_name] = {}
            if not sound_yml_dict[phase_file_name].get(audio_subfile_type):
                sound_yml_dict[phase_file_name][audio_subfile_type] = {}
            sound_yml_dict[phase_file_name][audio_subfile_type][subfile_name] = [
                subfile_name_random
            ]
    save_dict_as_yaml(sound_yml_dict, TEMP_DIR / "sound.yml")
    save_pack_info(PACK_INFO_TEXT, TEMP_DIR / "info.ini")
    print("Creating content pack...")
    create_content_pack(
        list(TEMP_DIR.iterdir()),
        CONTENT_PACK_FILE_PATH,
    )
    print(
        "Content pack created successfully at "
        f'"{CONTENT_PACK_FILE_PATH.absolute()}"!'
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("Exiting...")
        if TEMP_DIR.exists():
            shutil.rmtree(TEMP_DIR)
