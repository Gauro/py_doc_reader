import json
import shutil
from multiprocessing import Pool, cpu_count

import pandas as pd

from py_doc_reader.core.configuration import *
from py_doc_reader.exceptions.logger import logger
from py_doc_reader.scanned_doc_extractor.tesseract import create_objects_using_hocr


def perform_ocr_extraction_on_a_page(pdict_file_path, pstr_temp_folder_abs_path):
    try:
        lstr_page_abs_path = pdict_file_path["preprocessed_image_path"]
        ldf_line_details_page = pd.DataFrame(
            create_objects_using_hocr(lstr_page_abs_path, pstr_temp_folder_abs_path))
        ldf_line_details_page.rename(
            {'WordX1': "x1",
             'WordY1': "y1",
             "WordX2": "x2",
             "WordY2": "y1",
             "Word": "word",
             "WordConf": "word_confidence"}, axis=1,
            inplace=True)
        ldf_line_details_page.drop("Index", axis=1, inplace=True)
        ldf_line_details_page["page_number"] = pdict_file_path["page_number"]
        return ldf_line_details_page
    except Exception as e:
        logger.error(str(e))
        raise


class ScannedDocExtractor:
    def __init__(self):
        try:
            if CPU_CORES > cpu_count():
                self.gint_cpu_cores = cpu_count()
            else:
                self.gint_cpu_cores = CPU_CORES
        except Exception as e:
            logger.error(str(e), exc_info=True)

    def perform_scanned_doc_extraction(self, plst_preprocessed_image_details, pstr_temp_folder_path):
        try:
            llist_file_paths = plst_preprocessed_image_details
            # ================================================================================
            #  Create intermediate output folder for Editable Doc Reader
            # ================================================================================
            pstr_output_folder_path = pstr_temp_folder_path + os.sep + "ScannedDocExtractor"

            if os.path.exists(pstr_output_folder_path):
                shutil.rmtree(pstr_output_folder_path, ignore_errors=False, onerror=None)
            os.makedirs(pstr_output_folder_path)

            llist_ocr_page_params = [(x, pstr_output_folder_path) for x in llist_file_paths]
            with Pool(processes=self.gint_cpu_cores) as pool:
                llst_detected_objects = pool.starmap(func=perform_ocr_extraction_on_a_page,
                                                     iterable=llist_ocr_page_params)
            # Uncomment for testing one page at a time
            # llst_detected_objects = []
            # for ltuple_page in llist_ocr_page_params:
            #     llst_detected_objects.append(perform_ocr_extraction_on_a_page(ltuple_page[0],ltuple_page[1]))

            ldf_line_details = pd.concat(llst_detected_objects, ignore_index=True)
            ldf_line_details["ID"] = pd.Series(
                range(0, ldf_line_details.shape[0]))
            lstr_char_details_file_path = os.path.join(pstr_output_folder_path, f"character_details.json")
            with open(lstr_char_details_file_path, "wb") as file:
                file.write(bytes(json.dumps(ldf_line_details[["CharDetails", "ID"]].to_dict("records")), "utf-8"))
                file.close()
            return ldf_line_details

        except Exception as e:
            logger.error(str(e))
            raise
