"""
Created on 27-Oct-2022
@author: Gaurav Ail
"""
import time

from py_doc_reader.content_checker.ContentChecker import *
from py_doc_reader.editable_doc_extractor.EditableDocExtractor import *
from py_doc_reader.exceptions.exceptions import *
from py_doc_reader.preprocess.Preprocess import *
from py_doc_reader.scanned_doc_extractor.ScannedDocExtractor import *


def run():
    try:
        lstr_input = INPUT_PATH
        lstr_temp_path = INTERMEDIATE_OUTPUT_PATH

        for file in os.listdir(lstr_input):
            print("Processing file: ", file)
            start = time.time()
            if file.lower().endswith(('.png', '.jpg', '.jpeg', ".pdf")):
                # ================================================================================
                #  Create output folder for Input Doc
                # ================================================================================
                lstr_file_path = lstr_input + os.sep + file
                lstr_file_name = os.path.basename(file).split(".")[0]
                lstr_file_temp_folder_path = lstr_temp_path + os.sep + str(lstr_file_name)
                lstr_final_output_path = lstr_file_temp_folder_path + os.sep + lstr_file_name + ".csv"

                if os.path.exists(lstr_file_temp_folder_path):
                    shutil.rmtree(lstr_file_temp_folder_path, ignore_errors=False, onerror=None)
                os.makedirs(lstr_file_temp_folder_path)

                lstr_file_copy_path = lstr_file_temp_folder_path + os.sep + file
                shutil.copy(lstr_file_path, lstr_file_copy_path)

                # ===================================
                #   Check Input File Type
                # ===================================
                lstr_file_format = os.path.splitext(lstr_file_copy_path)[1]
                lobj_content_checker = ContentChecker()
                llst_page_info = []
                if lstr_file_format == ".pdf":
                    llst_page_info, ldict_navigation = lobj_content_checker.split_pdf(lstr_file_copy_path,
                                                                                      lstr_file_temp_folder_path)

                else:
                    try:
                        # verify contents of file, Check if image file is broken.
                        lobj_image = Image.open(lstr_file_copy_path)
                        lobj_image.verify()
                        lobj_image.close()
                        llst_page_info.append({"PageNo": 1, "ImagePath": lstr_file_copy_path, "is_editable": False})
                        ldict_navigation = {"Preprocessor": True, "EditablePDFReader": False}
                    except Exception as e:
                        raise NonRecoverableException(str(e))

                # =============================================================================
                #  Check Navigation and Route accordingly.
                #  If image file/ scanned doc, route for preprocessing and deskew
                #  If Editable pdf, then route to editable pdf reader .
                # =============================================================================

                if llst_page_info and ldict_navigation["Preprocessor"]:
                    # preprocess before performing ocr
                    lobj_preprocess = Preprocess()
                    llst_preprocessed_image_details = lobj_preprocess.perform_preprocessing(llst_page_info,
                                                                                            lstr_file_temp_folder_path)

                    # perform ocr using tesseract
                    if llst_preprocessed_image_details:
                        lobj_ocr_extraction = ScannedDocExtractor()
                        ldf_line_details = lobj_ocr_extraction.perform_scanned_doc_extraction(
                            llst_preprocessed_image_details, lstr_file_temp_folder_path)
                        ldf_line_details.to_csv(lstr_final_output_path, index=False)

                # extract text from editable pdf
                elif llst_page_info and ldict_navigation["EditablePDFReader"]:
                    lobj_epdf_reader = EditableDocExtractor()
                    ldf_line_details = lobj_epdf_reader.extract_text(lstr_file_copy_path, llst_page_info,
                                                                     lstr_file_temp_folder_path)
                    ldf_line_details.to_csv(lstr_final_output_path, index=False)
                time_taken = time.time() - start

                # log processing time taken for file 
                logger.info(f"{file} processed successfully. Time taken for processing file: {time_taken}")
                print(f"{file} processed successfully. Time taken for processing file: {time_taken}")
            else:
                logger.error(f"File Type Unknown, file {file} cannot be processed. ")

    except Exception as e:
        logger.error(str(e))


if __name__ == '__main__':
    run()
