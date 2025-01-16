import logging
import os
from dataclasses import dataclass
from typing import List

from supabase import create_client


@dataclass
class NecklaceData:
    necklace_id: str
    necklace_url: str
    x_lean_offset: float
    y_lean_offset: float
    x_broad_offset: float
    y_broad_offset: float
    category: str


supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)


def fetch_necklace_offset_each_store(storename: str) -> List[NecklaceData]:
    response = supabase.table("MagicMirror").select("*").eq("StoreName", storename).execute()

    necklace_data_list = []

    for item in response.data:
        jewellery_url = (
            f"https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/Stores/"
            f"{storename}/{item['Category']}/image/{item['Id']}.png"
        )

        necklace_data = NecklaceData(
            necklace_id=item['Id'],
            necklace_url=jewellery_url,
            x_lean_offset=item['x_lean'],
            y_lean_offset=item['y_lean'],
            x_broad_offset=item['x_chubby'],
            y_broad_offset=item['y_chubby'],
            category=item['Category']
        )

        necklace_data_list.append(necklace_data)

    return necklace_data_list


def fetch_model_body_type(image_url: str):
    try:
        response = supabase.table("JewelMirror_ModelImages").select("*").eq("image_url", image_url).execute()

        for item in response.data:
            print(item)
            return item['image_url'], item['body_structure']




    except Exception as e:
        print(f"The image url is not found in the table", {e})
        return None


def upload_information_to_new_table(necklace_id, nto_images_urls, cto_images_urls, mto_urls, video_urls, model_name):
    try:
        response_check = supabase.table("JM_Productpage").select("*").eq("Id", necklace_id).execute()

        if response_check.data:
            existing_record = response_check.data[0]

            updated_nto = f"{existing_record['nto_images_urls']},{nto_images_urls}" if existing_record[
                'nto_images_urls'] else nto_images_urls
            updated_cto = f"{existing_record['cto_images_urls']},{cto_images_urls}" if existing_record[
                'cto_images_urls'] else cto_images_urls
            updated_mto = f"{existing_record['mto_images_urls']},{mto_urls}" if existing_record[
                'mto_images_urls'] else mto_urls
            updated_video = f"{existing_record['video_urls']},{video_urls}" if existing_record[
                'video_urls'] else video_urls
            updated_model = f"{existing_record['model_name']},{model_name}" if existing_record[
                'model_name'] else model_name

            current_approve = existing_record.get('approve', {})
            if not isinstance(current_approve, dict):
                current_approve = {}

            if model_name not in current_approve:
                current_approve[model_name] = False

            logging.info(f"Updated model name: {updated_model}")
            logging.info(f"Updated approve status: {current_approve}")

            response = supabase.table("JM_Productpage").update({
                "nto_images_urls": updated_nto,
                "cto_images_urls": updated_cto,
                "mto_images_urls": updated_mto,
                "video_urls": updated_video,
                "model_name": updated_model,
                "approve": current_approve
            }).eq("Id", necklace_id).execute()

            print("Updated existing record")

        else:
            response = supabase.table("JM_Productpage").insert({
                "Id": necklace_id,
                "nto_images_urls": nto_images_urls,
                "cto_images_urls": cto_images_urls,
                "mto_images_urls": mto_urls,
                "video_urls": video_urls,
                "model_name": model_name,
                "approve": {
                    model_name: False
                }
            }).execute()

            print("Inserted new record")

        return response

    except Exception as e:
        print(f"Error in uploading the data to the table: {str(e)}")
        logging.error(f"Error in uploading the data to the table: {str(e)}")
        return None


def supabase_image_fetch_product_page(necklace_id, model_name):
    try:
        response = supabase.table("JM_Productpage").select("*").eq("Id", necklace_id).execute()

        if not response.data:
            print(f"No data found for necklace_id: {necklace_id}")
            return None

        # Get the first item from response
        item = response.data[0]

        def process_url_list(url_string):
            if not url_string:
                return []

            url_groups = url_string.replace("[", "").replace("]", "").split("],[")

            filtered_urls = []
            for group in url_groups:
                urls = [url.strip().strip('"\'') for url in group.split(",")]
                matching_urls = [url for url in urls if model_name in url]
                filtered_urls.extend(matching_urls)

            return filtered_urls

        try:
            nto_images = process_url_list(item.get('nto_images_urls', ''))
            cto_images = process_url_list(item.get('cto_images_urls', ''))
            mto_images = process_url_list(item.get('mto_images_urls', ''))
            print(f"nto_images: {nto_images}")
            print(f"cto_images: {cto_images}")
            print(f"mto_images: {mto_images}")

            video_urls = []
            if item.get('video_urls'):
                video_list = item['video_urls'].split(',')
                video_urls = [url.strip() for url in video_list if model_name in url]

            print(f"video_urls: {video_urls}")

        except AttributeError as e:
            print(f"Error parsing URLs: {e}")
            return None

        response = {
            'nto': nto_images,
            'cto': cto_images,
            'mto': mto_images,
            'video': video_urls,
            "status": "success"

        }

        return response
    except Exception as e:
        print(f"Error in fetching the data from the table: {e}")
        return None


def supabase_product_page_approval(necklace_id, nto_images_urls, cto_images_urls, mto_images_urls, video_urls,
                                   model_name):
    try:
        existing_record = supabase.table("MagicMirror").select("*").eq("Id", necklace_id).execute()

        def append_urls(existing_urls, new_urls):
            existing = convert_to_string(existing_urls) if existing_urls else ""
            new = convert_to_string(new_urls) if new_urls else ""

            if existing and new:
                return f"{existing},{new}"
            return new or existing

        if existing_record.data:
            record = existing_record.data[0]

            update_data = {
                "nto_images_urls": append_urls(record.get("nto_images_urls"), nto_images_urls),
                "cto_images_urls": append_urls(record.get("cto_images_urls"), cto_images_urls),
                "mto_images_urls": append_urls(record.get("mto_images_urls"), mto_images_urls),
                "video_urls": append_urls(record.get("video_urls"), video_urls)
            }
        else:
            update_data = {
                "nto_images_urls": convert_to_string(nto_images_urls),
                "cto_images_urls": convert_to_string(cto_images_urls),
                "mto_images_urls": convert_to_string(mto_images_urls),
                "video_urls": convert_to_string(video_urls)
            }

        result = supabase.table("MagicMirror") \
            .update(update_data) \
            .eq("Id", necklace_id) \
            .execute()

        res = supabase_jmproductpage_approval_flag(necklace_id, model_name, True)

        print(f"Successfully updated URLs for necklace ID: {necklace_id}")
        return result.data

    except Exception as e:
        error_msg = f"Error updating URLs in MagicMirror table: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)


def convert_to_string(value):
    if value is None:
        return ""

    if isinstance(value, list):
        return ",".join(str(item) for item in value if item)

    if isinstance(value, str):
        # If it's already a string, clean it up
        items = [item.strip() for item in value.split(",") if item.strip()]
        return ",".join(items)

    return str(value)


def supabase_fetch_not_approved_necklaces():
    try:
        response = supabase.table("JM_Productpage").select("*").execute()

        unapproved_necklaces = []
        for record in response.data:
            approve_dict = record.get('approve', {})
            if not isinstance(approve_dict, dict):
                continue

            false_approvals = {
                model: status
                for model, status in approve_dict.items()
                if status is False
            }

            if false_approvals:
                filtered_record = {
                    'Id': record['Id'],
                    'approve': false_approvals
                }
                unapproved_necklaces.append(filtered_record)
        print(f"Unapproved necklaces: {unapproved_necklaces}")
        return unapproved_necklaces

    except Exception as e:
        print(f"Error fetching not approved necklaces: {str(e)}")
        raise e


def supabase_jmproductpage_approval_flag(necklace_id, model_name, flag_value):
    try:
        current_data = supabase.table("JM_Productpage").select("approve").eq("Id", necklace_id).execute()

        current_approve = current_data.data[0].get("approve", {}) if current_data.data else {}

        if model_name in current_approve and current_approve[model_name] is True:
            print(f"Skipping update for {model_name} as it's already approved")
            return current_data.data

        if isinstance(current_approve, dict):
            current_approve[model_name] = flag_value
        else:
            current_approve = {model_name: flag_value}

        response = supabase.table("JM_Productpage").update(
            {"approve": current_approve}
        ).eq("Id", necklace_id).execute()

        return response.data

    except Exception as e:
        print(f"Error updating approval flag for necklace ID {necklace_id}: {str(e)}")
        raise e


def upload_productpage_logs(necklace_id: str, status: bool, model_name: str) -> dict:
    try:
        existing_record = supabase.table("JM_productpagelog").select("*").eq("id", necklace_id).execute()

        if not existing_record.data:
            response = supabase.table("JM_productpagelog").insert([{
                "id": necklace_id,
                "status": bool(status),
                "model_name": model_name
            }]).execute()
            print("Inserted new record")
            return {
                "status": "success",
                "message": "Record inserted successfully"
            }
        else:
            existing_models = existing_record.data[0].get('model_name', '').split(',')
            existing_models = [model.strip() for model in existing_models]

            if model_name in existing_models:
                return {
                    "status": "error",
                    "message": f"Record already exists with model {model_name} and {necklace_id}"
                }
            else:
                updated_models = ','.join(existing_models + [model_name])

                response = supabase.table("JM_productpagelog").update({
                    "model_name": updated_models
                }).eq("id", necklace_id).execute()

                print(f"Updated record with new model {model_name}")
                return {
                    "status": "success",
                    "message": f"Added new model {model_name} to existing record"
                }

    except Exception as e:
        error_msg = f"Error updating product page log for necklace {necklace_id}: {str(e)}"
        logging.error(error_msg)
        raise Exception(f"Failed to update product page log: {str(e)}")


def fetch_productpage_logs(necklace_id):
    try:
        response = supabase.table("JM_productpagelog").select("*").eq("id", necklace_id).execute()
        for item in response.data:
            return item['status']
    except Exception as e:
        print(f"Error in fetching the data from the table", {e})
        return None


if __name__ == "__main__":
    # store_name = "ChamundiJewelsMandir"
    # necklaces = fetch_necklace_offset_each_store(store_name)
    #
    # count = 0
    # for necklace in necklaces:
    #     print(f"Necklace ID: {necklace.necklace_id}")
    #     print(f"URL: {necklace.necklace_url}")
    #     print(f"Lean offsets (x, y): ({necklace.x_lean_offset}, {necklace.y_lean_offset})")
    #     print(f"Broad offsets (x, y): ({necklace.x_broad_offset}, {necklace.y_broad_offset})")
    #     print(f"Category: {necklace.category}")
    #     print("-" * 50)
    #     count += 1
    #
    # print(f"Total necklaces fetched: {count}")
    # image_url = "https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/JewelmirrorModelImages/M0X9e22b54f110493113feb79e3J.png"
    # url,type=fetch_model_body_type(image_url)
    # print(url,type)
    # ---------------------------------
    #
    # upload_information_to_new_table(necklace_id="CJM0025",
    #                                 nto_images_urls="https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/CJM0025-M0X0f16ad748dd979a48d3f79b4J-nto-Gold_Necklaces.png",
    #                                 cto_images_urls="https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/CJM0025-cto-Blue Lehenga.png,https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/CJM0025-cto-Blue Kurti.png",
    #                                 mto_urls="https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/CJM0025-M0X0f16ad748dd979a48d3f79b4J-mto-Blue_Kurti-lip_Carmine_Red_eye_Black_shadow_Maroon.png",
    #                                 video_urls="https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/JewelmirrorVideoGeneration/video_bd48d59bc8f358c3.mp4")
    # --------------------------------
    # nto, cto, mto, video = supabase_image_fetch_product_page("CJM0025")
    #
    # print("nto", nto)
    # print("cto", cto)
    # print("mto", mto)
    # print("video", video)
    # # --------------------------------
    # res = supabase_product_page_approval(necklace_id="CJM0025",
    #                                      nto_images_urls="https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/CJM0025-M0X0f16ad748dd979a48d3f79b4J-nto-Gold_Necklaces.png",
    #                                      cto_images_urls="https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/CJM0025-cto-Blue Lehenga.png,https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/CJM0025-cto-Blue Kurti.png",
    #                                      mto_images_urls="https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/ProductPageOutputs/CJM0025-M0X0f16ad748dd979a48d3f79b4J-mto-Blue_Kurti-lip_Carmine_Red_eye_Black_shadow_Maroon.png",
    #                                      video_urls="https://lvuhhlrkcuexzqtsbqyu.supabase.co/storage/v1/object/public/JewelmirrorVideoGeneration/video_bd48d59bc8f358c3.mp4")
    # print(res)

    # res = supabase_fetch_not_approved_necklaces()
    # print(res)
    # --------------------------------
    # res = supabase_jmproductpage_approval_flag("CJM001")
    # print(res)

    response = upload_productpage_logs("CJM0025", "True")

    # -------------------------------
    response = fetch_productpage_logs("CJM0025")
    print(response)
