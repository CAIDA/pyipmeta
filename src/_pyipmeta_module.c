
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

#include "_pyipmeta_ipmeta.h"
#include "_pyipmeta_provider.h"
#include "_pyipmeta_record.h"
#include <Python.h>

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#define ADD_OBJECT(modname, objname)                                             \
  do {                                                                  \
    if ((obj = _pyipmeta_##modname##_get_##objname##Type()) == NULL)   \
      return NULL;                                                      \
    if (PyType_Ready(obj) < 0)                                          \
      return NULL;                                                      \
    Py_INCREF(obj);                                                     \
    PyModule_AddObject(m, #objname, (PyObject*)obj);         \
  } while(0)

#define MODULE_DOCSTRING "Module that provides a low-level interface to libipmeta"

#if PY_MAJOR_VERSION > 2
static struct PyModuleDef module_def = {
	PyModuleDef_HEAD_INIT,
	"_pyipmeta",
	MODULE_DOCSTRING,
	-1,
	module_methods,
	NULL,
	NULL,
	NULL,
	NULL,
};
#endif

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

static PyObject *moduleinit(void)
{
  PyObject *m;
  PyTypeObject *obj;

#if PY_MAJOR_VERSION > 2
  m = PyModule_Create(&module_def);
#else
  m = Py_InitModule3("_pyipmeta",
					 module_methods,
					 MODULE_DOCSTRING);
#endif

  if (m == NULL)
    return NULL;

  /* IpMeta object */
  ADD_OBJECT(ipmeta, IpMeta);

  /* ipmeta provider object */
  ADD_OBJECT(provider, Provider);

  return m;
}

#if PY_MAJOR_VERSION > 2
PyMODINIT_FUNC
PyInit__pyipmeta(void)
{
  return moduleinit();
}
#else
PyMODINIT_FUNC
init_pyipmeta(void)
{
  moduleinit();
}
#endif
