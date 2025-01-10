"""
project @ batch_generation_support_team
created @ 2025-01-07
author  @ github.com/ishworrsubedii
"""
from dataclasses import dataclass
from typing import List

import requests


@dataclass
class VideoTimings:
    file_download_time: float
    video_creation_time: float
    supabase_upload_time: float


@dataclass
class VideoGenerationResult:
    status: str
    message: str
    video_url: str
    timings: VideoTimings


def generate_combined_video(
        intro_video_path: str,
        font_path: str,
        background_audio_path: str,
        necklace_title: List[str],
        necklace_images: List[str],
        nto_image_title: List[List[str]],
        nto_cto_image_title: List[List[str]],
        makeup_image_title: List[List[str]],
        necklace_try_on_output_images: List[List[str]],
        clothing_output_images: List[List[str]],
        makeup_output_images: List[List[str]],
        background_colors: List[List[int]],
        outro_title: str,
        address: str,
        phone_numbers: str,
        logo_url: str,
        image_display_duration: float = 2.5,
        fps: int = 30,
        transition_duration: float = 0.5,
        transition_type: str = "None",
        direction: str = "left",
        outro_video_path: str = "default_outro.mp4"
) -> VideoGenerationResult:
    url = "https://techconspartners-video-gen.hf.space/createcombinedvideo/"

    payload = {
        "intro_video_path": intro_video_path,
        "font_path": font_path,
        "background_audio_path": background_audio_path,
        "image_display_duration": image_display_duration,
        "fps": fps,
        "necklace_title": necklace_title,
        "nto_image_title": nto_image_title,
        "nto_cto_image_title": nto_cto_image_title,
        "makeup_image_title": makeup_image_title,
        "necklace_images": necklace_images,
        "necklace_try_on_output_images": necklace_try_on_output_images,
        "clothing_output_images": clothing_output_images,
        "makeup_output_images": makeup_output_images,
        "background_colors": background_colors,
        "outro_title": outro_title,
        "address": address,
        "phone_numbers": phone_numbers,
        "logo_url": logo_url,
        "transition_duration": transition_duration,
        "transition_type": transition_type,
        "direction": direction,
        "outro_video_path": outro_video_path
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    try:

        response = requests.post(url, headers=headers, json=payload)
        # response.raise_for_status()

        data = response.json()

        if data.get("status") != "success":
            raise ValueError(f"API returned error: {data.get('message', 'Unknown error')}")

        timings = VideoTimings(
            file_download_time=data["timings"]["file_download_time"],
            video_creation_time=data["timings"]["video_creation_time"],
            supabase_upload_time=data["timings"]["supabase_upload_time"]
        )

        result = VideoGenerationResult(
            status=data["status"],
            message=data["message"],
            video_url=data["video_url"],
            timings=timings
        )

        return result

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to make API request: {str(e)}")
    except (KeyError, ValueError) as e:
        raise ValueError(f"Error processing API response: {str(e)}")


if __name__ == "__main__":
    # test_params = {
    #     "intro_video_path": "Vellaimani_intro.mp4",
    #     "font_path": "PlayfairDisplay-VariableFont.ttf",
    #     "background_audio_path": "LoveIndianCinematicBGM.mp3",
    #     "necklace_title": ["ARA01DI001"],
    #     "necklace_images": [
    #         "https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/Stores/VellaimaniJewellery/Diamond%20Necklaces/image/ARA01DI001.png"
    #     ],
    #     "nto_image_title": [["ARA01DI001"]],
    #     "nto_cto_image_title": [["ARA01DI001", "ARA01DI001"]],
    #     "makeup_image_title": [["ARA01DI001"]],
    #     "necklace_try_on_output_images": [[
    #         "https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/ARA01DI001-M0X75f993d5c22ab292b647e3c9J-nto-Diamond_Necklaces.png"
    #     ]],
    #     "clothing_output_images": [[
    #         "https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/ARA01DI001-cto-Red Silk saree.png",
    #         "https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/ARA01DI001-cto-Green south indian saree.png"
    #     ]],
    #     "makeup_output_images": [[
    #         "https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/ARA01DI001-M0X75f993d5c22ab292b647e3c9J-mto-Purple_kurti-lip_Carmine_Red_eye_Black_shadow_Maroon.png"
    #     ]],
    #     "background_colors": [[245, 245, 245], [220, 245, 245]],
    #     "outro_title": "Reach out to us for more information",
    #     "address": "123, ABC Street, XYZ City",
    #     "phone_numbers": "1234567890",
    #     "logo_url": "https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/MagicMirror/FullImages/default.png"
    # }

    with open("/home/ishwor/Desktop/TCP/batch_generation_support_team/combined_video_params.json", "r") as f:
        test_params = str(f.read())

    try:
        result = generate_combined_video(**test_params)
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")
        print(f"Video URL: {result.video_url}")
        print(
            f"Total processing time: {result.timings.file_download_time + result.timings.video_creation_time + result.timings.supabase_upload_time:.2f} seconds")
    except Exception as e:
        print(f"Error: {str(e)}")
