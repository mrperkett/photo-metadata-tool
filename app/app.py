import os
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from pathlib import Path
from pathlib import PosixPath
from pathlib import PurePosixPath
from pathlib import PureWindowsPath
from pathlib import WindowsPath

import pandas as pd
import streamlit as st

from seqpix.api import get_new_sequential_date_time_original
from seqpix.api import load_all_image_file_info


def read_environment_variables():
    # USER_OS
    # by default, set to the same OS as is running the script
    USER_OS = os.getenv("USER_OS", os.name)
    st.session_state.USER_OS = USER_OS

    # USER_MOUNT_PATH: the user's folder mounted
    # default: set to "/" for posix and "C:/" for nt
    if USER_OS == "posix":
        st.session_state.user_path_cls = PurePosixPath
        USER_MOUNT_PATH_STR = os.getenv("USER_MOUNT_PATH", "/")
        st.session_state.USER_MOUNT_PATH = st.session_state.user_path_cls(USER_MOUNT_PATH_STR)
    elif USER_OS == "nt":
        st.session_state.user_path_cls = PureWindowsPath
        USER_MOUNT_PATH_STR = os.getenv("USER_MOUNT_PATH", "C:/")
        st.session_state.USER_MOUNT_PATH = PureWindowsPath(USER_MOUNT_PATH_STR)
    else:
        raise ValueError(f"'USER_OS' value not recognized ({USER_OS})")

    # INTERNAL_OS
    INTERNAL_OS = os.name
    st.session_state.INTERNAL_OS = INTERNAL_OS

    # INTERNAL_MOUNT_PATH
    # default: set to "/" for posix and "C:/" for nt
    if INTERNAL_OS == "posix":
        st.session_state.internal_path_cls = PosixPath
        INTERNAL_MOUNT_PATH_STR = os.getenv("INTERNAL_MOUNT_PATH", "/")
        st.session_state.INTERNAL_MOUNT_PATH = st.session_state.internal_path_cls(
            INTERNAL_MOUNT_PATH_STR
        )
    elif INTERNAL_OS == "nt":
        st.session_state.internal_path_cls = WindowsPath
        INTERNAL_MOUNT_PATH_STR = os.getenv("INTERNAL_MOUNT_PATH", "C:/")
        st.session_state.INTERNAL_MOUNT_PATH = st.session_state.internal_path_cls(
            INTERNAL_MOUNT_PATH_STR
        )
    else:
        raise ValueError(f"'INTERNAL_OS' value not recognized ({INTERNAL_OS})")


def get_internal_image_dir(
    user_image_dir_str: str,
    user_mount_path: Path,
    internal_mount_path: Path,
    user_path_cls: type,
    internal_path_cls: type,
) -> Path:
    # image directory (user OS)
    user_image_dir = user_path_cls(user_image_dir_str)

    # set the internal path of the directory
    try:
        # relative directory path (user OS)
        relative_path = user_image_dir.relative_to(user_mount_path)

        # full directory path (internal OS)
        internal_image_dir = internal_mount_path / internal_path_cls(str(relative_path))
    except ValueError as e:
        raise ValueError(
            f"Image Directory ('{user_image_dir}') is not a subdirectory of user_mount_path"
            f" ('{user_mount_path}')"
        ) from e

    # verify that internal_image_dir is a directory
    if not internal_image_dir.is_dir():
        raise ValueError(f"Internal Image Directory ('{internal_image_dir}') is not a directory")

    return internal_image_dir


def generate_dfs():
    # load the image file information from file
    image_name_to_image_info = {}
    for image_file_info in load_all_image_file_info(st.session_state.internal_image_dir):
        image_name = image_file_info.path.name
        if image_name in image_name_to_image_info:
            raise ValueError(f"image_name ('{image_name}') is repeated")
        image_name_to_image_info[image_name] = image_file_info

    if len(image_name_to_image_info) == 0:
        raise ValueError("No images were found in the image directory")

    # build df_orig to hold all the image information
    fields = [
        "path",
        "file_size_bytes",
        "date_time_created",
        "date_time_modified",
        "date_time_original",
    ]
    data = [[im.__dict__[field] for field in fields] for im in image_name_to_image_info.values()]
    df_current = pd.DataFrame(data, columns=fields)
    df_current["file_name"] = df_current.apply(lambda row: Path(row["path"]).name, axis=1)
    df_current["file_size_megabytes"] = df_current["file_size_bytes"] / (1024 * 1024.0)
    df_current = df_current.rename(columns={"path": "file_path"})

    columns = [
        "file_path",
        "file_name",
        "file_size_bytes",
        "file_size_megabytes",
        "date_time_original",
        "date_time_modified",
        "date_time_created",
    ]
    df_current = df_current[columns]
    df_current = df_current.sort_values(by=["date_time_original", "file_name"]).reset_index(
        drop=True
    )

    df_target = df_current.copy()

    # sort df_target
    if st.session_state.input_sort_order_str == "File Name (A-Z)":
        df_target = df_target.sort_values(by="file_name", ascending=True).reset_index(drop=True)
    elif st.session_state.input_sort_order_str == "File Name (Z-A)":
        df_target = df_target.sort_values(by="file_name", ascending=False).reset_index(drop=True)
    else:
        raise ValueError(
            f"sort_order_str ('{st.session_state.input_sort_order_str}') not recognized"
        )

    # set the new date_time_original based on the sort order
    new_date_time_originals = get_new_sequential_date_time_original(
        len(image_name_to_image_info),
        st.session_state.start_datetime,
        st.session_state.time_between_images,
    )
    df_target["date_time_original"] = new_date_time_originals

    # store variables in st.session_state
    st.session_state.new_date_time_originals = new_date_time_originals
    st.session_state.image_name_to_image_info = image_name_to_image_info
    st.session_state.df_current = df_current
    st.session_state.df_target = df_target


def get_start_datetime(start_date: date, start_time: time) -> datetime:
    start_datetime = datetime.combine(start_date, start_time)
    return start_datetime


def get_time_interval(time_step: int, time_step_units: str) -> timedelta:
    if time_step <= 0:
        raise ValueError(f"time_step ({time_step}) <= 0")
    if time_step_units == "seconds":
        time_between_images = timedelta(seconds=time_step)
    elif time_step_units == "minutes":
        time_between_images = timedelta(minutes=time_step)
    elif time_step_units == "hours":
        time_between_images = timedelta(hours=time_step)
    elif time_step_units == "days":
        time_between_images = timedelta(hours=24 * time_step)
    else:
        raise ValueError(f"time_step_units ('{time_step_units}') not recognized")
    return time_between_images


def display_dfs():
    column_config = {
        "file_path": None,
        "file_name": "File Name",
        "file_size_bytes": None,
        "file_size_megabytes": "Size (MB)",
        "date_time_original": "Date Taken",
        "date_time_modified": "Date Modified",
        "date_time_created": "Date Created",
    }

    st.markdown("## Current Image Info")
    st.dataframe(st.session_state.df_current, column_config=column_config)

    st.markdown("## Preview of Target Image Info")
    if st.session_state.df_current.equals(st.session_state.df_target):
        st.markdown("✅ Target matches current image info")
    st.dataframe(st.session_state.df_target, column_config=column_config)


def set_session_state_defaults():
    # TODO: clean this up
    st.session_state.initialized = True
    st.session_state.setdefault("USER_OS", None)
    st.session_state.setdefault("USER_MOUNT_PATH", None)
    st.session_state.setdefault("INTERNAL_OS", None)
    st.session_state.setdefault("INTERNAL_MOUNT_PATH", None)
    st.session_state.setdefault("user_path_cls", None)
    st.session_state.setdefault("internal_path_cls", None)

    st.session_state.setdefault("user_image_dir", None)
    st.session_state.setdefault("start_datetime", None)
    st.session_state.setdefault("time_between_images", None)

    st.session_state.setdefault("image_file_info_list", None)
    st.session_state.setdefault("df_orig", None)
    st.session_state.setdefault("df_new", None)
    st.session_state.setdefault("new_date_time_originals", None)
    st.session_state.setdefault("show_preview", False)
    st.session_state.setdefault("run_clicked", False)

    st.session_state.setdefault("input_image_dir_str", None)
    st.session_state.setdefault("input_sort_order_str", None)
    st.session_state.setdefault("input_start_date", None)
    st.session_state.setdefault("input_start_time", None)
    st.session_state.setdefault("input_time_step", None)
    st.session_state.setdefault("input_time_step_units", None)
    st.session_state.setdefault("input_overwrite_original", None)

    st.session_state.setdefault("display_image_info", False)
    st.session_state.setdefault("allow_run", False)


def display_user_input_fields():
    st.title("Photo Metadata Tool")
    with st.expander("Usage", expanded=False):
        st.markdown("This is an in-depth explanation of how to use this tool")

    # Disabled text input showing the user mounted base directory
    st.text_input(
        "Mounted Base Directory",
        value=st.session_state.USER_MOUNT_PATH,
        disabled=True,
        help="A value specified through configuration during deployment.  The *Image Directory*"
        "must start with this path",
    )

    # Text input for image directory path
    st.session_state.input_image_dir_str = st.text_input(
        "Image Directory",
        value=st.session_state.USER_MOUNT_PATH,
        help="Copy and paste the full path to the directory containing the photos to be modified."
        "⚠️ Note that the beginning of this path must match *Mounted Base Directory*",
    )

    # Radio buttons for sort order
    options = ["File Name (A-Z)", "File Name (Z-A)"]
    st.session_state.input_sort_order_str = st.radio(
        "Sort Order",
        options=options,
        index=0,
        help="Select how images will be ordered before sequentially updating their"
        " *Date Time Original* metadata",
    )

    # Start date / time
    st.markdown("#### Select the start date and time")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.input_start_date = st.date_input(
            "Start Date",
            value=date(year=1986, month=1, day=1),
            help="Set the new *Date Taken* value for the first image in the sequence",
        )
    with col2:
        st.session_state.input_start_time = st.time_input(
            "Start Time",
            value=time(hour=0, minute=0, second=0, microsecond=0),
            step=timedelta(minutes=15),
            help="Set the new *Date Taken* value for the first image in the sequence",
        )

    st.markdown("#### Select the time interval between images")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.input_time_step = st.number_input(
            "Time step", value=1, min_value=1, step=1, help="time step between images"
        )
    with col2:
        st.session_state.input_time_step_units = st.selectbox(
            "Units", options=["seconds", "minutes", "hours", "days"], index=0
        )

    # Checkbox for whether to overwrite the original file
    st.session_state.input_overwrite_original = st.checkbox(
        "Overwrite original images",
        value=True,
        help="By default, the original images will be updated.  If not selected, the modified"
        " images will be written to a separate subfolder",
    )

    # TODO: implement functionality for case where original images should not be overwritten


def process_inputs():
    # set start_datetime
    start_datetime = get_start_datetime(
        st.session_state.input_start_date, st.session_state.input_start_time
    )

    # set time_between_images
    time_between_images = get_time_interval(
        st.session_state.input_time_step, st.session_state.input_time_step_units
    )

    # set the internal image directory
    internal_image_dir = get_internal_image_dir(
        st.session_state.input_image_dir_str,
        st.session_state.USER_MOUNT_PATH,
        st.session_state.INTERNAL_MOUNT_PATH,
        st.session_state.user_path_cls,
        st.session_state.internal_path_cls,
    )

    # save variables to session_state
    st.session_state.start_datetime = start_datetime
    st.session_state.time_between_images = time_between_images
    st.session_state.internal_image_dir = internal_image_dir


def update_metadata():
    for _, row in st.session_state.df_target.iterrows():
        image_name = row["file_name"]
        new_date_time_original = row["date_time_original"].to_pydatetime()
        image_file_info = st.session_state.image_name_to_image_info[image_name]
        image_file_info.set_date_time_original(new_date_time_original)


def main():
    if "initialized" not in st.session_state:
        set_session_state_defaults()
    read_environment_variables()

    display_user_input_fields()

    # Button to preview changes
    st.session_state.preview_button_clicked = st.button(
        "Preview", help="Click to preview images in folder and output"
    )

    # Generate dataframes with original and new image info upon click
    if st.session_state.preview_button_clicked:
        process_inputs()
        generate_dfs()
        st.session_state.display_image_info = True
        st.session_state.allow_run = True

    # Button to run the metadata update
    st.session_state.run_button_clicked = st.button(
        "Run Metadata Update",
        disabled=not st.session_state.allow_run,
        help="Update the *Date Taken* metadata",
    )

    # Update image metadata
    if st.session_state.run_button_clicked:
        update_metadata()
        generate_dfs()

    # Display dataframes
    if st.session_state.display_image_info:
        display_dfs()


if __name__ == "__main__":
    main()
