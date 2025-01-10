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


supabase_url =os.getenv("SUPABASE_URL")
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


def upload_information_to_new_table(necklace_id, nto_images_urls, cto_images_urls, mto_urls, video_urls):
    try:
        response = supabase.table("JM_Productpage").insert([
            {"Id": necklace_id, "nto_images_urls": nto_images_urls, "cto_images_urls": cto_images_urls,
             "mto_images_urls": mto_urls,
             "video_urls": video_urls}]).execute()
        print(response)
    except Exception as e:
        print(f"Error in uploading the data to the table", {e})
        return None


def supabase_image_fetch_product_page(necklace_id):
    try:
        response = supabase.table("JM_Productpage").select("*").eq("Id", necklace_id).execute()
        for item in response.data:
            return item['nto_images_urls'], item['cto_images_urls'], item['mto_images_urls'], item['video_urls']
    except Exception as e:
        print(f"Error in fetching the data from the table", {e})
        return None


def supabase_product_page_approval(necklace_id, nto_images_urls, cto_images_urls, mto_images_urls, video_urls):
    try:
        nto_string = convert_to_string(nto_images_urls)
        cto_string = convert_to_string(cto_images_urls)
        mto_string = convert_to_string(mto_images_urls)
        video_string = convert_to_string(video_urls)

        update_data = {
            "nto_images_urls": nto_string,
            "cto_images_urls": cto_string,
            "mto_images_urls": mto_string,
            "video_urls": video_string
        }

        result = supabase.table("MagicMirror") \
            .update(update_data) \
            .eq("Id", necklace_id) \
            .execute()
        res = supabase_jmproductpage_approval_flag(necklace_id)

        print(f"Successfully updated URLs for necklace ID: {necklace_id}")
        return result.data

    except Exception as e:
        print(f"Error updating URLs in MagicMirror table: {str(e)}")
        raise e


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
        response = supabase.table("JM_Productpage").select("*").eq("approve", False).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching not approved necklaces: {str(e)}")
        raise e


def supabase_jmproductpage_approval_flag(necklace_id):
    try:
        response = supabase.table("JM_Productpage").update({"approve": True}).eq("Id", necklace_id).execute()
        return response.data
    except Exception as e:
        print(f"Error updating approval flag for necklace ID: {necklace_id}")
        raise e


def upload_productpage_logs(necklace_id: str, status: bool) -> dict:
    try:
        existing_record = supabase.table("JM_productpagelog").select("*").eq("id", necklace_id).execute()

        if not existing_record.data:
            response = supabase.table("JM_productpagelog").insert([{
                "id": necklace_id,
                "status": bool(status),
            }]).execute()
            print("Inserted new record")
            response = {
                "status": "success",
                "message": "Record inserted successfully"
            }
            return response
        else:
            response = {
                "status": "error",
                "message": "Record already exists"
            }
            return response


    except Exception as e:
        logging.error(f"Error updating product page log for necklace {necklace_id}: {str(e)}")
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
