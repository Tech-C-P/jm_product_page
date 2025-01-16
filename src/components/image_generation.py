"""
project @ batch_generation_support_team
created @ 2025-01-07
author  @ github.com/ishworrsubedii
"""
from dataclasses import dataclass
from typing import List, Dict
from urllib.parse import quote

import requests


@dataclass
class MakeupColors:
    lipstick: str
    eyeliner: str
    eyeshadow: str


@dataclass
class ImageGenerationResult:
    nto_results: List[Dict[str, str]]
    cto_results: List[Dict[str, str]]
    mto_results: List[Dict[str, Dict]]
    status: str
    message: str


def batch_image_generation(
        model_image: str,
        necklace_id: str,
        necklace_category: str,
        storename: str,
        clothing_list: List[str],
        makeup_colors: Dict[str, str],
        x_offset: float = 0.2,
        y_offset: float = 0.35
) -> ImageGenerationResult:
    base_url = "https://techconspartners-video-gen.hf.space/product_page_image_generation"

    encoded_model_image = quote(model_image)

    url = f"{base_url}?model_image={encoded_model_image}&necklace_id={necklace_id}&necklace_category={quote(necklace_category)}&storename={quote(storename)}&x_offset={x_offset}&y_offset={y_offset}"

    payload = {
        "clothing_list": clothing_list,
        "makeup_colors": makeup_colors
    }

    # Set up headers
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()

        if data.get("status") != "success":
            raise ValueError(f"API returned error: {data.get('message', 'Unknown error')}")

        result = ImageGenerationResult(
            status=data["status"],
            message=data["message"],
            nto_results=data["nto_results"],
            cto_results=data["cto_results"],
            mto_results=data["mto_results"]
        )

        return result

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to make API request: {str(e)}")
    except (KeyError, ValueError) as e:
        raise ValueError(f"Error processing API response: {str(e)}")


if __name__ == "__main__":
    test_params = {
        "model_image": "https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/JewelmirrorModelImages/M0X75f993d5c22ab292b647e3c9J.png",
        "necklace_id": "CJM002",
        "necklace_category": "Gold Necklaces",
        "storename": "ChamundiJewelsMandir",
        "clothing_list": ["Red Silk saree", "Green south indian saree", "Purple kurti"],
        "makeup_colors": {
            "lipstick": "Carmine Red",
            "eyeliner": "Black",
            "eyeshadow": "Maroon"
        }
    }

    try:
        result = batch_image_generation(**test_params)
        with open("image_generation_response.json", "w") as f:
            f.write(str(result))
        print(f"Status: {result.status}")
        print(f"Message: {result.message}")
        print(f"Number of NTO results: {len(result.nto_results)}")
        print(f"Number of CTO results: {len(result.cto_results)}")
        print(f"Number of MTO results: {len(result.mto_results)}")
    except Exception as e:
        print(f"Error: {str(e)}")
