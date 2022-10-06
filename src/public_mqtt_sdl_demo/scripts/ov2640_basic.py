# from ov2640 import esp8266_ov2640 as ov2640
import gc
import sys
import time

from ov2640 import ov2640

FNAME = "image2.jpg"


def main():
    try:
        print("initializing camera")
        cam = ov2640.ov2640(
            sclpin=9,  # board pin 12
            sdapin=8,  # board pin 11
            cspin=5,  # board pin 7
            sckpin=2,  # board pin 4
            mosipin=3,  # board pin 5
            misopin=4,  # board pin 6
            spi_id=0,
            i2c_id=0,
            resolution=ov2640.OV2640_320x240_JPEG,
        )
        # cam = ov2640.ov2640(resolution=ov2640.OV2640_1024x768_JPEG)
        print("clearing memory")
        print(gc.mem_free())

        print("capturing to file")
        clen = cam.capture_to_file(FNAME, True)
        print("captured image is %d bytes" % clen)
        print("image is saved to %s" % FNAME)

        time.sleep(10)
        sys.exit(0)

    except KeyboardInterrupt:
        print("exiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
