from CHECLabPy.plotting.camera import CameraImage
import numpy as np
import os


class CameraImage2(CameraImage):
    @staticmethod
    def crop(path):
        from PyPDF2 import PdfFileWriter, PdfFileReader
        with open(path, "rb") as in_f:
            input1 = PdfFileReader(in_f)
            output = PdfFileWriter()

            num_pages = input1.getNumPages()
            for i in range(num_pages):
                page = input1.getPage(i)
                page.cropBox.lowerLeft = (100, 20)
                page.cropBox.upperRight = (280, 220)
                output.addPage(page)

            pdf_path = os.path.splitext(path)[0] + "_cropped.pdf"
            with open(pdf_path, "wb") as out_f:
                output.write(out_f)
                print("Cropped figure saved to: {}".format(pdf_path))


ci = CameraImage2.from_camera_version("1.1.0")
ci.pixels.set_facecolor('white')
ci.pixel_highlighting.set_facecolor('white')
ci.pixel_highlighting.set_linewidth(0.2)
ci.pixel_highlighting.set_edgecolor('black')
ci.add_pixel_text(np.arange(2048)%64, color='black', size=1)
ci.save("/Users/Jason/Downloads/camera.pdf")
