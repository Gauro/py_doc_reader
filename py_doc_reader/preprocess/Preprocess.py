import shutil
from multiprocessing import Pool, cpu_count
from subprocess import Popen, PIPE

from py_doc_reader.core.configuration import *
from py_doc_reader.exceptions.logger import logger


def deskew_image_using_leptonica(pstr_input_page_path, pstr_temp_folder_path, pint_page_number):
    lstr_input_page_abs_path = None
    lstr_deskew_corrected_image_abs_path = None
    try:
        # ==============================
        #   properly making paths
        # ==============================
        lstr_input_page_abs_path = pstr_input_page_path
        lstr_image_file_name, _ = os.path.splitext(lstr_input_page_abs_path.split(os.sep)[-1])
        lstr_deskew_corrected_image_abs_path = pstr_temp_folder_path + os.path.sep + lstr_image_file_name + \
                                               "_deskew_corrected.jpg"

        # ===================================================================
        # perform de-skew on image
        # ===================================================================
        # change directory
        try:
            os.chdir(LEPTONICA_PATH)
        except OSError:
            logger.info("LEPTONICA_PATH " + LEPTONICA_PATH + " is not correct")
            raise
        except Exception:
            raise

        # executing command using subprocess
        lstr_command = './skewtest ' + '"' + lstr_input_page_abs_path + '" "' + lstr_deskew_corrected_image_abs_path + '"'
        try:
            lobj_process = Popen(lstr_command, stderr=PIPE, shell=True)
        except NameError:
            raise
        except Exception:
            logger.info("lstr_command: " + lstr_command + " is not properly formed")
            raise

        # ===========================================================
        # check return code of process
        # if return code==0, then process has executed with no errors
        # else, process has failed
        # ===========================================================
        _, lbyt_error = lobj_process.communicate()

        if lobj_process.returncode != 0:
            lstr_info = "deskew failed with error code: %d and error: %s" % (
                lobj_process.returncode, lbyt_error.decode("utf-8"))
            logger.error("command is not valid"
                         + "\ncommand: " + lstr_command
                         + "\ninfo: " + lstr_info
                         + "\nImportant Parameters:"
                         + "\n\tpstr_input_img_path: " + str(lstr_input_page_abs_path)
                         + "\n\tpstr_output_image_path: " + str(lstr_deskew_corrected_image_abs_path)
                         + "\n\tLEPTONICA_PATH: " + str(LEPTONICA_PATH))
            raise Exception(lstr_info)
        else:
            logger.debug(f"Image {lstr_input_page_abs_path} de-skewed successfully.")
            return {
                "preprocessed_image_path": lstr_deskew_corrected_image_abs_path,
                "page_number": pint_page_number,
            }

    except Exception:
        logger.error("Input Parameter:"
                     + "\n\tpstr_input_img_path: " + str(lstr_input_page_abs_path)
                     + "\n\tpstr_output_image_path: " + str(lstr_deskew_corrected_image_abs_path)
                     + "Important Variables:"
                     + "\n\tLEPTONICA_PATH: " + str(LEPTONICA_PATH))
        raise


class Preprocess:

    def __init__(self):
        try:
            if CPU_CORES > cpu_count():
                self.gint_cpu_cores = cpu_count()
            else:
                self.gint_cpu_cores = CPU_CORES
        except Exception:
            raise

    def perform_preprocessing(self, plist_file_paths, pstr_temp_folder_path):
        try:

            # ================================================================================
            #  Create intermediate output folder for Editable Doc Reader
            # ================================================================================
            pstr_temp_folder_path = pstr_temp_folder_path + os.sep + "Preprocessing"

            if os.path.exists(pstr_temp_folder_path):
                shutil.rmtree(pstr_temp_folder_path, ignore_errors=False, onerror=None)
            os.makedirs(pstr_temp_folder_path)

            llist_deskew_image_using_leptonica_params = \
                [(x["ImagePath"], pstr_temp_folder_path, x["PageNo"]) for x in plist_file_paths]

            # Perform Deskew for skewed images
            with Pool(processes=self.gint_cpu_cores) as pool:
                llist_preprocessed_image_paths = pool.starmap(deskew_image_using_leptonica,
                                                              llist_deskew_image_using_leptonica_params)
            return llist_preprocessed_image_paths
        except Exception as e:
            raise
