import shutil
from multiprocessing import Pool, cpu_count

import cv2
import fitz
import numpy as np
import pandas as pd
from PIL import Image

from py_doc_reader.core.configuration import *
from py_doc_reader.exceptions.logger import logger


class EditableDocExtractor:
    def __init__(self):
        try:
            if CPU_CORES > cpu_count():
                self.gint_cpu_cores = cpu_count()
            else:
                self.gint_cpu_cores = CPU_CORES
        except Exception as e:
            logger.error(str(e), exc_info=True)

    @staticmethod
    def draw_boxes_on_image(pstr_ip_image_path, pstr_output_file_path, plst_word_objects):
        try:
            larr_temp_img = cv2.imread(pstr_ip_image_path)

            for lobj_word in plst_word_objects:
                cv2.rectangle(larr_temp_img, (lobj_word[0], lobj_word[1]), (lobj_word[2], lobj_word[3]), (0, 255, 0), 1)

            cv2.imwrite(pstr_output_file_path, larr_temp_img)

            del larr_temp_img

        except Exception as e:
            logger.error(str(e),
                         extra={"Input Parameters": {"pstr_ip_image_path": pstr_ip_image_path,
                                                     "pstr_output_file_path": pstr_output_file_path,
                                                     "plst_word_objects": plst_word_objects}
                                })
            raise

    @staticmethod
    def merge_all_of_objects(plst_objects, pstr_merged_object_text_seperator=" "):
        """
        Input
        ------
            plst_objects = list of boxes i.e [[x1,y1,x2,y2,"text1"],[x1,y1,x2,y2,"text2"]]

        Description
        -----------
            merge the all boxes

        Output
        ------
            llst_merged_box = [x1,y1,x2,y2, "text1 text2"]
        """
        try:
            llint_row_xmin = sorted(plst_objects, key=lambda k: [k[0]])[0][0]
            llint_row_ymin = sorted(plst_objects, key=lambda k: [k[1]])[0][1]
            llint_row_xmax = sorted(plst_objects, key=lambda k: [k[2]])[-1][2]
            llint_row_ymax = sorted(plst_objects, key=lambda k: [k[3]])[-1][3]
            llst_text = [llst_object[4].strip() for llst_object in plst_objects]

            llst_merged_box = [llint_row_xmin, llint_row_ymin, llint_row_xmax, llint_row_ymax,
                               pstr_merged_object_text_seperator.join(llst_text).strip()]

            return llst_merged_box
        except Exception as e:
            logger.error("Input Parameter:"
                         + "\n\tplst_objects: " + str(plst_objects)
                         + "\n\tpstr_merged_object_text_seperator: " + str(pstr_merged_object_text_seperator)
                         + "\n Error:" + str(e))
            raise

    def draw_obj_row_box_on_image(self, pstr_ip_image_path, pstr_output_file_path, plst_line_wise_object_groups):
        try:
            llst_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 255)]
            lint_color_index = 0
            larr_temp_img = cv2.imread(pstr_ip_image_path)

            for llst_objects_in_line in plst_line_wise_object_groups:
                llst_merged_box = self.merge_all_of_objects(llst_objects_in_line)
                cv2.rectangle(larr_temp_img, (llst_merged_box[0], llst_merged_box[1]),
                              (llst_merged_box[2], llst_merged_box[3]), llst_colors[lint_color_index], 2)
                lint_color_index = lint_color_index + 1

                if lint_color_index == len(llst_colors):
                    lint_color_index = 0

            cv2.imwrite(pstr_output_file_path, larr_temp_img)

            del larr_temp_img

        except Exception as e:
            logger.error(str(e),
                         extra={"Input Parameters": {"pstr_ip_image_path": pstr_ip_image_path,
                                                     "pstr_output_file_path": pstr_output_file_path,
                                                     "plst_line_wise_object_groups": plst_line_wise_object_groups}
                                })
            raise

    def extract_object_rows_from_pdf(self, pstr_pdf_path, lstr_intermediate_dir, lint_page_number):
        try:
            with fitz.open(pstr_pdf_path) as doc:
                page = doc[lint_page_number]

                # ldf_tables = tabula.read_pdf(pstr_pdf_path, pages='all', lattice=True, password=pstr_pdf_password)
                lint_page_no = page.number + 1
                lstr_output_folder_path = lstr_intermediate_dir + os.sep + "page_" + str(lint_page_no)
                os.makedirs(lstr_output_folder_path)

                # =======================================================================
                # Extract words from page with 72 dpi
                # =======================================================================
                # render page to an image, default dpi is 72

                # adding 100 as confidence and page number to the modified list by getText to save in df
                llst_word_objects = [
                    [*[round(i) if isinstance(i, float) else i for i in lobj_word][0:5], 100, lint_page_no] for
                    lobj_word in page.getText("words")]
                ldf_word_objects = pd.DataFrame(llst_word_objects,
                                                columns=["x1", "y1", "x2", "y2", "word", "word_confidence",
                                                         "page_number"])

                # if SAVE_INTERMEDIATE:
                # create object map csv
                ldf_word_objects.to_csv(lstr_output_folder_path + os.sep + "fitz_page_no_"
                                        + str(lint_page_no) + "_object_map.csv",
                                        index=False, header=True)

                # =======================================================================
                # save image 72 dpi
                # =======================================================================

                # if SAVE_INTERMEDIATE:
                pix = page.getPixmap(alpha=False)
                # draw word boxes on image
                lstr_pdf_page_path = lstr_output_folder_path + os.sep + "fitz_page_no_" + str(
                    lint_page_no) + ".jpg"
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(lstr_pdf_page_path, "JPEG")
                del img

                self.draw_boxes_on_image(lstr_pdf_page_path, lstr_output_folder_path + os.sep
                                         + "fitz_page_no_" + str(lint_page_no) + "_word_objects.jpg",
                                         ldf_word_objects.values.tolist())
                del pix

                # =======================================================================
                # remove garbage i.e non english character
                # =======================================================================
                if not ldf_word_objects.empty:
                    ldf_word_objects["word"] = \
                        ldf_word_objects["word"].to_frame().applymap(
                            lambda x: str(x).encode('utf-8').decode('ascii', 'ignore'))["word"]

                    # ldf_word_objects['text'] = ldf_word_objects['text'].apply(
                    #     lambda lstr_word: tp.remove_non_english_characters(lstr_word).strip())

                    # remove all blank rows
                    ldf_word_objects = ldf_word_objects.replace(r'^\s*$', np.NaN, regex=True)
                    ldf_word_objects.dropna(axis=0, how='any', inplace=True)
                    ldf_word_objects.reset_index(inplace=True, drop=True)

                    # if SAVE_INTERMEDIATE:
                    lstr_pdf_page_path = lstr_output_folder_path + os.sep + "fitz_page_no_" + str(
                        lint_page_no) + ".jpg"
                    # create object map csv
                    ldf_word_objects.to_csv(lstr_output_folder_path + os.sep + "fitz_page_no_"
                                            + str(lint_page_no) + "_non_eng_free_object_map.csv",
                                            index=False, header=True)
                    # draw word boxes on image
                    self.draw_boxes_on_image(lstr_pdf_page_path, lstr_output_folder_path + os.sep
                                             + "fitz_page_no_" + str(lint_page_no)
                                             + "_garbage_free_word_objects.jpg",
                                             ldf_word_objects.values.tolist())

                return ldf_word_objects
        except Exception as e:
            logger.error(str(e), extra={"Input Parameters": {"pstr_pdf_path": pstr_pdf_path}})
            raise e

    def perform_line_identification(self, ldf_line_details, plist_file_paths, pstr_intermediate_output_folder_path):
        llist_line_details = list()
        try:
            lobj_line_details_groups = ldf_line_details.groupby("page_number")
            for _, ldf_line_details_page in lobj_line_details_groups:
                # group by "ymin" and keep element with minimum "xmin"
                ldf_word_objects = ldf_line_details_page.sort_values(["y1", "x1"])

                lft_distance_between_two_rows = 3

                # =======================================================================
                # add "line_index" column in dataframe
                # =======================================================================
                ldf_word_objects.loc[
                    (ldf_word_objects["y2"].shift() < ldf_word_objects["y2"] - lft_distance_between_two_rows) & (
                            ldf_word_objects["y1"].shift() != ldf_word_objects["y1"] - lft_distance_between_two_rows),
                    "LineIndex"] = 1
                ldf_word_objects["LineIndex"] = ldf_word_objects["LineIndex"].cumsum().ffill().fillna(0)
                ldf_word_objects = ldf_word_objects.groupby(by="LineIndex").apply(lambda x: x.sort_values("x1"))

                llist_line_details.append(ldf_word_objects)

            ldf_line_details = pd.concat(llist_line_details, ignore_index=True)

            # Assign Line x1 values
            # ldf_line_details["Line_x1"] = ldf_line_details.apply(func=lambda x: ldf_line_details[
            #     (ldf_line_details["LineIndex"] == x["LineIndex"]) & (
            #             ldf_line_details["page_number"] == x["page_number"])]["x1"].min(), axis=1)
            # # Assign Line y1 values
            # ldf_line_details["Line_y1"] = \
            #     ldf_line_details.apply(func=lambda x: ldf_line_details[
            #         (ldf_line_details["LineIndex"] == x["LineIndex"]) & (
            #                 ldf_line_details["page_number"] == x["page_number"])]["y1"].min(), axis=1)
            # # Assign Line x2 values
            # ldf_line_details["Line_x2"] = ldf_line_details.apply(func=lambda x: ldf_line_details[
            #     (ldf_line_details["LineIndex"] == x["LineIndex"]) & (
            #             ldf_line_details["page_number"] == x["page_number"])]["x2"].max(), axis=1)
            # # Assign Line y2 values
            # ldf_line_details["Line_y2"] = ldf_line_details.apply(func=lambda x: ldf_line_details[
            #     (ldf_line_details["LineIndex"] == x["LineIndex"]) & (
            #             ldf_line_details["page_number"] == x["page_number"])]["y2"].max(), axis=1)

            # if SAVE_INTERMEDIATE:
            #     for ldict_file_path in plist_file_paths:
            #         lstr_image_path = ldict_file_path["page_path"]
            #         lstr_image_file_name, _ = os.path.splitext(lstr_image_path.split(os.sep)[-1])
            #         larr_temp_img = cv2.imread(lstr_image_path).copy()
            #         ldf_grouped_lines = ldf_line_details[
            #             ldf_line_details["page_number"] == ldict_file_path[
            #                 "page_number"]].groupby(by="LineIndex").max()
            #         ldf_grouped_lines.apply(
            #             func=lambda x: cv2.rectangle(larr_temp_img, (
            #                 x["Line_x1"],
            #                 x["Line_y1"]), (
            #                                              x["Line_x2"],
            #                                              x["Line_y2"]), (0, 255, 0), 2),
            #             axis=1)
            #         cv2.imwrite(
            #             pstr_intermediate_output_folder_path + os.sep + lstr_image_file_name + "_line_object_map.jpg",
            #             larr_temp_img)
            return ldf_line_details
        except Exception as e:
            logger.error(str(e), exc_info=True)
            raise

    def extract_text(self, pstr_file_copy_path, plst_page_info, pstr_output_folder_path):
        try:
            # ================================================================================
            #  Create intermediate output folder for Editable Doc Reader
            # ================================================================================
            pstr_output_folder_path = pstr_output_folder_path + os.sep + "EditableDocExtractor"

            if os.path.exists(pstr_output_folder_path):
                shutil.rmtree(pstr_output_folder_path, ignore_errors=False, onerror=None)
            os.makedirs(pstr_output_folder_path)

            # ===================================================================
            # extracting text from pdf
            # ===================================================================
            with fitz.open(pstr_file_copy_path) as doc:
                llist_params_for_text_extraction = \
                    [(pstr_file_copy_path, pstr_output_folder_path, lobj_page[0])
                     for lobj_page in enumerate(doc)]
            with Pool(processes=self.gint_cpu_cores) as pool:
                llst_detected_objects = pool.starmap(self.extract_object_rows_from_pdf,
                                                     llist_params_for_text_extraction)
            ldf_line_details = pd.concat(llst_detected_objects, ignore_index=True)
            ldf_line_details["Id"] = pd.Series(
                range(0, ldf_line_details.shape[0]))

            # ===================================================================
            # Assign Line number to each word object detected
            # ===================================================================
            ldf_line_details = self.perform_line_identification(ldf_line_details, plst_page_info,
                                                                pstr_output_folder_path)
            return ldf_line_details

        except Exception as e:
            logger.critical(f"{e}.", exc_info="True")
            raise
