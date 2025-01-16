"""
project @ batch_generation_support_team
created @ 2025-01-09
author  @ github.com/ishworrsubedii
"""
import json

from fastapi import APIRouter

from src.components.supabase_information_fetch import supabase_image_fetch_product_page, supabase_product_page_approval, \
    supabase_fetch_not_approved_necklaces
from src.pipeline.main import combined_image_and_video_generation

router = APIRouter()


@router.get('/ping')
def ping():
    return "Running"


@router.post('/generate')
def generate(storename, image_url):
    response = combined_image_and_video_generation(storename=storename, image_url=image_url)
    return response


from fastapi.responses import JSONResponse


@router.post('/image_fetch_product_page')
def image_fetch_product_page(necklace_id, model_name):
    response = supabase_image_fetch_product_page(necklace_id, model_name)
    return response


@router.post('/approve')
def image_fetch_product_page(necklace_id, model_name):
    response = supabase_image_fetch_product_page(necklace_id, model_name)

    response_nto = json.loads(response["nto"]) if isinstance(response["nto"], str) else response["nto"]
    response_cto = json.loads(response["cto"]) if isinstance(response["cto"], str) else response["cto"]
    response_mto = json.loads(response["mto"]) if isinstance(response["mto"], str) else response["mto"]

    comma_seperated_nto = ",".join(response_nto)
    comma_seperated_cto = ",".join(response_cto)
    comma_seperated_mto = ",".join(response_mto)
    responsee = supabase_product_page_approval(necklace_id, comma_seperated_nto, comma_seperated_cto,
                                               comma_seperated_mto,
                                               response["video"], model_name=model_name)

    return JSONResponse(content=responsee)


@router.get('/list_necklace_id')
def list_not_approved_necklaces():
    response = supabase_fetch_not_approved_necklaces()

    necklace_models = {}

    for item in response:
        necklace_id = item.get('Id')
        approve_dict = item.get('approve', {})

        if necklace_id and approve_dict:
            # Get list of models that have False approval status
            unapproved_models = [
                model_name
                for model_name, status in approve_dict.items()
                if status is False
            ]

            if unapproved_models:  # Only include if there are unapproved models
                necklace_models[necklace_id] = unapproved_models

    return JSONResponse(content=necklace_models)
