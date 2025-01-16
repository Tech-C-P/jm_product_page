import logging
import os
import random
from datetime import datetime
from typing import List

from src.components.image_generation import batch_image_generation
from src.components.supabase_information_fetch import fetch_necklace_offset_each_store, fetch_model_body_type, \
    upload_information_to_new_table, upload_productpage_logs
from src.components.video_generation import generate_combined_video

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/running.log'),
        logging.StreamHandler()
    ]
)


def update_processed_necklaces(necklace_id: str, status: bool, model_name: str):
    response = upload_productpage_logs(necklace_id, status, model_name=model_name)


def get_random_clothing_combinations(clothing_list: List[str], colors: List[str], count: int = 5) -> List[str]:
    """Generate random clothing combinations."""
    combinations = []
    for _ in range(count):
        clothing = random.choice(clothing_list)
        color = random.choice(colors)
        combinations.append(f"{color} {clothing}")
    return combinations


def combined_image_and_video_generation(storename, image_url):
    logging.info("Starting combined image and video generation process")

    try:
        necklace_data = fetch_necklace_offset_each_store(storename=storename)
        url, typee = fetch_model_body_type(image_url=image_url)

        model_name = url.split("/")[-1].split(".")[0]

        for necklace in necklace_data:
            necklace_id = necklace.necklace_id
            response = upload_productpage_logs(necklace_id, True, model_name=model_name)
            if response['status'] == "error":
                print("Skipping", necklace_id)
                logging.info(f"Skipping {necklace_id} - already processed")
                continue

            start_time = datetime.now()
            logging.info(f"Processing necklace: {necklace_id}")

            try:
                if typee == "lean":
                    x_offset = necklace.x_lean_offset
                    y_offset = necklace.y_lean_offset
                    logging.info("Body Type: lean")

                elif typee == "medium":
                    x_offset = necklace.x_broad_offset
                    y_offset = necklace.y_broad_offset
                    logging.info("Body Type: medium")

                else:
                    logging.info("Body Type: None")
                    x_offset = None
                    y_offset = None

                clothing_combinations = get_random_clothing_combinations(
                    clothing_list=["Salwar Kameez", "South Indian Saree", "Kurti", "Lehenga", "Silk Saree"],
                    colors=["Red", "Blue", "Green", "Yellow", "Pink"]
                )

                makeup_data = {
                    "lipstick": "Carmine Red",
                    "eyeliner": "Black",
                    "eyeshadow": "Maroon"
                }

                image_params = {
                    "model_image": url,
                    "necklace_id": necklace_id,
                    "necklace_category": necklace.category,
                    "storename": storename,
                    "clothing_list": clothing_combinations,
                    "makeup_colors": makeup_data,
                    "x_offset": x_offset,
                    "y_offset": y_offset

                }
                print("image: params", image_params)
                logging.info("NTO-CTO-MTO images Generating for {}".format(necklace_id))

                image_results = batch_image_generation(**image_params)
                logging.info(f"Image generation result: {image_results}")

                if image_results.status != 'success':
                    raise Exception(f"Image generation failed: {image_results.message}")
                cto_urls = [result['url'] for result in image_results.cto_results[:4]]  # First four CTO images
                mto_urls = [image_results.mto_results[-1]['url']]
                video_params = {
                    "intro_video_path": f"{storename}_intro.mp4",
                    "font_path": "PlayfairDisplay-VariableFont.ttf",
                    "background_audio_path": "LoveIndianCinematicBGM.mp3",
                    "necklace_title": [necklace_id],
                    "necklace_images": [necklace.necklace_url],
                    "nto_image_title": [[necklace_id]],
                    "nto_cto_image_title": [[necklace_id, necklace_id, necklace_id, necklace_id]],
                    "makeup_image_title": [[necklace_id]],
                    "necklace_try_on_output_images": [[result['url'] for result in image_results.nto_results]],
                    "clothing_output_images": [cto_urls
                                               ],
                    "makeup_output_images": [
                        mto_urls
                    ],

                    "background_colors": [[245, 245, 245], [220, 245, 245]],
                    "outro_title": "Reach out to us for more information",
                    "address": "None",
                    "phone_numbers": "None",
                    "logo_url": "https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/MagicMirror/FullImages/default.png",
                    "outro_video_path": f"{storename}_outro.mp4"
                }

                logging.info("Video Generating for {}".format(necklace_id))

                video_result = generate_combined_video(**video_params)
                logging.info(f"Video generation result: {video_result}")

                if video_result.status != 'success':
                    raise Exception(f"Video generation failed: {video_result.message}")

                urls = {
                    'video_url': video_result.video_url,
                    'images_url': str([result['url'] for result in image_results.nto_results])
                }

                logging.info("Completed combined image and video generation process")
                upload_information_to_new_table(necklace_id=necklace_id,
                                                nto_images_urls=[result['url'] for result in image_results.nto_results],
                                                cto_images_urls=cto_urls,
                                                mto_urls=mto_urls,
                                                video_urls=video_result.video_url,
                                                model_name=model_name
                                                )

                update_processed_necklaces(
                    necklace_id=necklace_id,
                    status=True,
                    model_name=model_name

                )





            except Exception as e:

                raise e

                logging.error(f"Error processing {necklace_id}: {str(e)}")

                update_processed_necklaces(
                    necklace_id=necklace_id,
                    status=False,
                    model_name=model_name

                )
        return {
            "status": "success",
        }


    except Exception as e:
        raise e
        logging.error(f"Fatal error in combined generation process: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


if __name__ == "__main__":
    image_url = "https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/JewelmirrorModelImages/p_01.png"
    storename = "ChamundiJewelsMandir"
    result = combined_image_and_video_generation(image_url=image_url, storename=storename)
    print(f"Process completed with status: {result}")
