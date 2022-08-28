"""
This file licensed under the MIT License and incorporates work covered by
the following copyright and permission notice:

The MIT License (MIT)

Copyright (c) 2022-2022 Rob Hamerling

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

""" Dictionary with specific SMUX configurations for AS7341
    See AMS Application Note AS7341_AN000666_1.01.pdf
    for detailed instructions how to configure the channel mapping.
    The Application Note can be found in one of the evaluation packages, e.g.
    AS7341_EvalSW_Reflection_v1-26-3/Documents/application notes/SMUX/

    This file should be imported by AS7341.py with:
        from as7341_smux_select import *
"""
AS7341_SMUX_SELECT = {
    # F1 through F4, CLEAR, NIR:
    "F1F4CN": b"\x30\x01\x00\x00\x00\x42\x00\x00\x50\x00\x00\x00\x20\x04\x00\x30\x01\x50\x00\x06",
    # F5 through F8, CLEAR, NIR:
    "F5F8CN": b"\x00\x00\x00\x40\x02\x00\x10\x03\x50\x10\x03\x00\x00\x00\x24\x00\x00\x50\x00\x06",
    # F2 through F7:
    "F2F7": b"\x20\x00\x00\x00\x05\x31\x40\x06\x00\x40\x06\x00\x10\x03\x50\x20\x00\x00\x00\x00",
    # Flicker Detection only:
    "FD": b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x60",
}

#
