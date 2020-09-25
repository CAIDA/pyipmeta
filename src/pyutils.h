/*
 * This file is part of pyipmeta
 *
 * CAIDA, UC San Diego
 * corsaro-info@caida.org
 *
 * Copyright (C) 2017-2020 The Regents of the University of California.
 * Authors: Alistair King
 *
 * This program is free software; you can redistribute it and/or modify it under
 * the terms of the GNU General Public License as published by the Free Software
 * Foundation; either version 2 of the License, or (at your option) any later
 * version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef ___PYUTILS_H
#define ___PYUTILS_H

#include <Python.h>

#ifndef PyVarObject_HEAD_INIT
#define PyVarObject_HEAD_INIT(type, size) PyObject_HEAD_INIT(type) size,
#endif

#if PY_MAJOR_VERSION > 2
#define MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)
#else
#define MOD_INIT(name) PyMODINIT_FUNC init##name(void)
#endif

#ifndef Py_TYPE
#define Py_TYPE(ob) (((PyObject *)(ob))->ob_type)
#endif

#if PY_MAJOR_VERSION > 2
// Unlike PyUnicode_FromString(str), this will gracefully handle invalid utf8
#define PYSTR_FROMSTR(str) PyUnicode_DecodeUTF8(str, strlen(str), "replace")
#define PYSTR_FORMAT(str, arg_tuple) PyUnicode_Format(str, arg_tuple)
#define PYNUM_FROMLONG(num) PyLong_FromLong(num)
#else
#define PYSTR_FROMSTR(str) PyString_FromString(str)
#define PYSTR_FORMAT(str, arg_tuple) PyString_Format(str, arg_tuple)
#define PYNUM_FROMLONG(num) PyInt_FromLong(num)
#endif

static inline int add_to_dict(PyObject *dict, const char *key_str,
                              PyObject *value)
{
  PyObject *key = PYSTR_FROMSTR(key_str);
  int err = PyDict_SetItem(dict, key, value);
  Py_DECREF(key);
  Py_DECREF(value);
  return err;
}

#endif
