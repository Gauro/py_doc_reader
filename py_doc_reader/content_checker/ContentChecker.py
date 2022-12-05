"""
Class converts pdf and tiff files into image (jpg) format
It returns dictionary containing keys for every separated image.
"""
import io
import os
import shutil
from multiprocessing import Pool, cpu_count

import fitz
from PIL import Image
from pdf2image import *

from py_doc_reader.core.configuration import CPU_CORES, TEXT_BY_IMAGE_RATIO_THRESHOLD, REF_PAGES_TO_READ
from py_doc_reader.exceptions.logger import logger


class ContentChecker:
    def __init__(self):
        try:
            if CPU_CORES > cpu_count():
                self.gint_cores = cpu_count()
            else:
                self.gint_cores = CPU_CORES
        except Exception as e:
            logger.error(str(e), exc_info=True)

    def split_pdf(self, pstr_input_file_path, pstr_output_folder_path):
        try:

            # ================================================================================
            #  Create intermediate output folder for Content Checking
            # ================================================================================
            pstr_output_folder_path = pstr_output_folder_path + os.sep + "ContentChecker"

            if os.path.exists(pstr_output_folder_path):
                shutil.rmtree(pstr_output_folder_path, ignore_errors=False, onerror=None)
            os.makedirs(pstr_output_folder_path)

            lstr_pdf_name, _ = os.path.splitext(pstr_input_file_path.split(os.sep)[-1])
            lstr_no_of_pages = REF_PAGES_TO_READ
            lflt_text_by_image_ratio_thresh = TEXT_BY_IMAGE_RATIO_THRESHOLD

            # ===========================================================
            # calculate the number of pages required.
            # ===========================================================
            with fitz.open(pstr_input_file_path) as doc:
                if lstr_no_of_pages.lower() != 'all':
                    lint_no_of_pages = int(lstr_no_of_pages)
                    if lint_no_of_pages > doc.pageCount:
                        lint_no_of_pages = doc.pageCount
                else:
                    lint_no_of_pages = doc.pageCount

            # ===========================================================
            # check how many pages are editable.
            # ===========================================================
            llist_save_pdf_page_as_img_thread_params = [
                (pstr_input_file_path, lint_page_number, lflt_text_by_image_ratio_thresh, pstr_output_folder_path
                 ) for lint_page_number in range(1, lint_no_of_pages + 1)]

            with Pool(processes=self.gint_cores) as pool:
                llist_page_editable_info = pool.starmap(self.is_pdf_page_searchable,
                                                        llist_save_pdf_page_as_img_thread_params)
            # ===========================================================
            # set Navigation code
            # ===========================================================
            if len([x for x in llist_page_editable_info if not x["is_editable"]]) > 0:
                ldict_navigation = {"Preprocessor": True, "EditablePDFReader": False}
            else:
                ldict_navigation = {"Preprocessor": False, "EditablePDFReader": True}

            # ===========================================================
            # save pages as images
            # ===========================================================
            llist_save_pdf_page_as_img_thread_params = [
                (lint_page_number, pstr_output_folder_path, lstr_pdf_name, pstr_input_file_path,
                 ldict_navigation) for lint_page_number in range(1, lint_no_of_pages + 1)]

            with Pool(processes=self.gint_cores) as pool:
                llst_incomplete_page_info = pool.starmap(self.save_pdf_page_as_img,
                                                         llist_save_pdf_page_as_img_thread_params)
            del doc

            # ===========================================================
            # format return value
            # ===========================================================
            llst_page_info = \
                [{**x,
                    "is_editable": next(
                        y["is_editable"] for y in llist_page_editable_info if y["page_number"] == x["PageNo"])}
                    for x in llst_incomplete_page_info]
            return llst_page_info, ldict_navigation

        except Exception as ex:
            logger.error("Input Parameters: "
                         + "\n\tpstr_input_pdf_file_path: " + str(pstr_input_file_path) + "\n"
                         + "\n\tpstr_output_folder_path: " + str(pstr_output_folder_path) + "\n"
                         + "\n Error: " + str(ex))
            raise ex

    @staticmethod
    def is_pdf_page_searchable(pstr_input_file_path, pint_page_number, pflt_text_by_image_ratio_thresh,
                               pstr_output_folder_path):
        try:
            with fitz.open(pstr_input_file_path) as doc:
                lobj_page = doc[pint_page_number - 1]
                lbol_is_page_searchable = False

                # extract text
                llst_word_objects = lobj_page.getText("words")
                if llst_word_objects:
                    logger.debug(
                        f"Page number: {pint_page_number} has extractable text. Reference: {pstr_output_folder_path}")
                    lbol_is_page_searchable = True

                # extract images
                llst_page_images = [b for b in lobj_page.getText("dict")["blocks"] if b["type"] == 1]

                if llst_word_objects and llst_page_images:
                    logger.debug(
                        f"Page number: {pint_page_number} has images too. Reference: f{pstr_output_folder_path}")
                    # ===========================================================
                    # here, know that text and image both are present inside page
                    # so find out if considerable amount of text is present or not
                    # ===========================================================

                    # ===========================================================
                    # calculate area covered by images
                    # ===========================================================
                    llst_img_areas = []

                    for lint_img_index, lobj_img_info in enumerate(llst_page_images):
                        # calculate image area and add into list
                        lobj_bbox = lobj_img_info["bbox"]
                        llst_img_areas.append(round((lobj_bbox[2] - lobj_bbox[0]) * (lobj_bbox[3] - lobj_bbox[1])))
                        del lobj_bbox

                        # extract the image bytes and save it to local disk
                        lbyt_image = Image.open(io.BytesIO(lobj_img_info["image"]))
                        lbyt_image.save(pstr_output_folder_path + "/page_" + str(pint_page_number) + "_image_" +
                                        str(lint_img_index) + "." + lobj_img_info["ext"])
                        logger.debug(f"extracted images saved in path: {pstr_output_folder_path}/page_"
                                     f"{str(lobj_page.number)}_image_{str(lint_img_index)}.{lobj_img_info['ext']}")
                        del lbyt_image

                    lint_area_covered_by_images = sum(llst_img_areas)
                    del llst_img_areas

                    # ===========================================================
                    # calculate area covered by text
                    # ===========================================================
                    llst_text_boxes_areas = [round((lobj_word[2] - lobj_word[0]) * (lobj_word[3] - lobj_word[1]))
                                             for lobj_word in llst_word_objects]
                    lint_area_covered_by_text = sum(llst_text_boxes_areas)
                    del llst_text_boxes_areas

                    if lint_area_covered_by_text / lint_area_covered_by_images < pflt_text_by_image_ratio_thresh:
                        lbol_is_page_searchable = False
                    logger.debug(f"Output file path: {pstr_output_folder_path}, "
                                 f"Page number: {pint_page_number}, "
                                 f"Area covered by text: {lint_area_covered_by_text}, "
                                 f"Area covered by images: {lint_area_covered_by_images}, "
                                 f"Ratio of area text/area: {lint_area_covered_by_text / lint_area_covered_by_images}, "
                                 f"Page Searchable: {lbol_is_page_searchable}")
                    del llst_page_images
                    del llst_word_objects

            return {"page_number": pint_page_number, "is_editable": lbol_is_page_searchable}
        except Exception as ex:
            logger.error(str(ex), exc_info=True)
            raise ex

    @staticmethod
    def save_pdf_page_as_img(pint_page_number, pstr_output_folder_path, pstr_pdf_name, pstr_input_file_path,
                             ldict_navigation):
        try:
            with fitz.open(pstr_input_file_path) as doc:
                lobj_page = doc[pint_page_number - 1]
                # ===========================================================
                # save page as image using image2pdf lib page is searchable
                # else save page as image using PyMuPDF
                # ===========================================================
                lint_page_index = pint_page_number - 1
                lstr_image_path = f"{pstr_output_folder_path}{os.sep}{pstr_pdf_name}_{str(lint_page_index)}.jpg"
                if ldict_navigation["EditablePDFReader"]:
                    # render page to an image, default dpi is 72
                    pix = lobj_page.getPixmap(alpha=False)
                    # NOTE: this line was originally
                    # img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    # revert if not working.
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                    img.save(lstr_image_path, "JPEG")
                    del img
                    del pix
                elif ldict_navigation["Preprocessor"]:
                    llst_extracted_page_path = convert_from_path(
                        pstr_input_file_path, dpi=300, first_page=pint_page_number, last_page=pint_page_number,
                        output_folder=pstr_output_folder_path, paths_only=True)
                    lstr_extracted_page_path = llst_extracted_page_path[0]
                    del llst_extracted_page_path
                    lobj_image = Image.open(lstr_extracted_page_path)
                    lobj_image.save(lstr_image_path)
                    lobj_image.close()
                    os.remove(lstr_extracted_page_path)

            return {"PageNo": pint_page_number, "ImagePath": lstr_image_path}
        except Exception:
            raise
