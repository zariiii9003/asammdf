#ifndef ZLIB_ISAL_H
#define ZLIB_ISAL_H

#include <Python.h>

#define ISAL_ZLIB 3
#define ISAL_DEF_MAX_HIST_BITS 15
#define ISAL_DECOMP_OK 0
#define Py_MIN(x, y) (((x) > (y)) ? (y) : (x))

static Py_ssize_t arrange_output_buffer_with_maximum(uint32_t *avail_out,
                                                     uint8_t **next_out,
                                                     uint8_t **buffer,
                                                     Py_ssize_t length,
                                                     Py_ssize_t max_length);

#endif // ZLIB_ISAL_H