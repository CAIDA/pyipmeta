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
#include "_pyipmeta_provider.h"
#include "_pyipmeta_record.h"
#include "pyutils.h"
#include <arpa/inet.h>
#include <libipmeta.h>
#include <Python.h>

typedef struct {
  PyObject_HEAD

  /* libipmeta Instance Handle */
  ipmeta_t *ipm;

  /* reusable record set */
  ipmeta_record_set_t *recordset;

} IpMetaObject;

#define IpMetaDocstring "IpMeta object"

#define IpMetaTypeName "_pyipmeta.IpMeta"


static void
IpMeta_dealloc(IpMetaObject *self)
{
  if (self->ipm != NULL) {
      ipmeta_free(self->ipm);
  }
  if (self->recordset) {
      ipmeta_record_set_free(&self->recordset);
  }
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject *
IpMeta_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  IpMetaObject *self;

  self = (IpMetaObject *)type->tp_alloc(type, 0);
  if (self == NULL) {
    return NULL;
  }
  self->ipm = NULL;
  self->recordset = NULL;

  const char *dsname = NULL;
  static char *kwlist[] = { "datastructure", NULL };
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|s", kwlist, &dsname)) {
    return NULL;
  }

  ipmeta_ds_id_t dsid = IPMETA_DS_DEFAULT;
  if (dsname) {
    if ((dsid = ipmeta_ds_name_to_id(dsname)) == IPMETA_DS_NONE) {
      PyErr_SetString(PyExc_RuntimeError, "Invalid IpMeta Datastructure name");
      return NULL;
    }
  }
  if ((self->ipm = ipmeta_init(dsid)) == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "ipmeta_init failed");
    Py_DECREF(self);
    return NULL;
  }

  if ((self->recordset = ipmeta_record_set_init()) == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "ipmeta_record_set_init failed");
    Py_DECREF(self);
    return NULL;
  }

  return (PyObject *)self;
}

static int
IpMeta_init(IpMetaObject *self,
	       PyObject *args, PyObject *kwds)
{
  return 0;
}

/** Enable the given lookup provider */
static PyObject *
IpMeta_enable_provider(IpMetaObject *self, PyObject *args)
{
  ProviderObject *pyprov = NULL;
  const char *optstr = NULL;

  /* get the Provider argument */
  if (!PyArg_ParseTuple(args, "O!|s",
                        _pyipmeta_provider_get_ProviderType(),
                        &pyprov, &optstr)) {
    return NULL;
  }

  if (!pyprov->prov) {
    PyErr_SetString(PyExc_RuntimeError, "Invalid IpMeta Provider object");
    return NULL;
  }

  if (ipmeta_enable_provider(self->ipm, pyprov->prov, optstr) == 0) {
    Py_RETURN_TRUE;
  }

  Py_RETURN_FALSE;
}

/** Get the provider with the given ID */
static PyObject *
IpMeta_get_provider_by_id(IpMetaObject *self, PyObject *args)
{
  int id = -1;
  ipmeta_provider_t *prov;

  /* get the ID argument */
  if (!PyArg_ParseTuple(args, "i", &id)) {
    return NULL;
  }

  if ((prov = ipmeta_get_provider_by_id(self->ipm, id)) == NULL) {
    Py_RETURN_NONE;
  }

  return Provider_new((PyObject*)self, prov);
}

/** Get the provider with the given name */
static PyObject *
IpMeta_get_provider_by_name(IpMetaObject *self, PyObject *args)
{
  const char *namestr;
  ipmeta_provider_t *prov;

  /* get the name argument */
  if (!PyArg_ParseTuple(args, "s", &namestr)) {
    return NULL;
  }

  if ((prov = ipmeta_get_provider_by_name(self->ipm, namestr)) == NULL) {
    Py_RETURN_NONE;
  }

  return Provider_new((PyObject*)self, prov);
}

/** Get the all available providers */
static PyObject *
IpMeta_get_all_providers(IpMetaObject *self)
{
  ipmeta_provider_t **provs;
  PyObject *list;
  int i;

  /* get the array from ipmeta */
  if ((provs = ipmeta_get_all_providers(self->ipm)) == NULL) {
    return NULL;
  }

  /* create a list */
  if((list = PyList_New(0)) == NULL)
    return NULL;

  for(i=0; i<IPMETA_PROVIDER_MAX; i++) {
    if (provs[i] != NULL) {
      /* add provider to list */
      if(PyList_Append(list, Provider_new((PyObject*)self, provs[i])) == -1) {
        return NULL;
      }
    }
  }

  return list;
}

/* Look up an IP address or a prefix */
static PyObject *
IpMeta_lookup(IpMetaObject *self, PyObject *args)
{
  const char *pyaddrstr = NULL;
  int provmask = 0;
  /* get the prefix/address argument */
  if (!PyArg_ParseTuple(args, "s|i", &pyaddrstr, &provmask)) {
    return NULL;
  }

  /* create a list */
  PyObject *list = NULL;
  if((list = PyList_New(0)) == NULL)
    return NULL;

  PyObject *pyrec = NULL;

  int rc = ipmeta_lookup(self->ipm, pyaddrstr, provmask, self->recordset);
  if (rc < 0) {
    if (rc == IPMETA_ERR_INPUT) {
      PyErr_Format(PyExc_ValueError, "Invalid address or prefix '%s'", pyaddrstr);
    } else {
      PyErr_SetString(PyExc_RuntimeError, "Internal error");
    }
    goto err;
  }
  ipmeta_record_set_rewind(self->recordset);
  ipmeta_record_t *record = NULL;
  uint64_t num_ips = 0;
  while ((record = ipmeta_record_set_next(self->recordset, &num_ips)) != NULL) {
    pyrec = _pyipmeta_record_as_dict(record, num_ips);
    if(PyList_Append(list, pyrec) == -1) {
      goto err;
    }
    Py_DECREF(pyrec);
    pyrec = NULL;
  }
  ipmeta_record_set_clear(self->recordset);

  return list;

 err:
  ipmeta_record_set_clear(self->recordset);
  if (list != NULL) {
    Py_DECREF(list);
  }
  if (pyrec != NULL) {
    Py_DECREF(pyrec);
  }
  return NULL;
}

static PyMethodDef IpMeta_methods[] = {

  {
    "enable_provider",
    (PyCFunction)IpMeta_enable_provider,
    METH_VARARGS,
    "Enable the given IpMeta Provider"
  },

  {
    "get_provider_by_id",
    (PyCFunction)IpMeta_get_provider_by_id,
    METH_VARARGS,
    "Get the provider with the given ID"
  },

  {
    "get_provider_by_name",
    (PyCFunction)IpMeta_get_provider_by_name,
    METH_VARARGS,
    "Get the provider with the given name"
  },

  {
    "get_all_providers",
    (PyCFunction)IpMeta_get_all_providers,
    METH_NOARGS,
    "Get a list of all available providers"
  },

  {
    "lookup",
    (PyCFunction)IpMeta_lookup,
    METH_VARARGS,
    "Look up metadata for an IP address or prefix"
  },

  {NULL}  /* Sentinel */
};

static PyTypeObject IpMetaType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  IpMetaTypeName,             /* tp_name */
  sizeof(IpMetaObject), /* tp_basicsize */
  0,                                    /* tp_itemsize */
  (destructor)IpMeta_dealloc,        /* tp_dealloc */
  0,                                    /* tp_print */
  0,                                    /* tp_getattr */
  0,                                    /* tp_setattr */
  0,                                    /* tp_compare */
  0,                                    /* tp_repr */
  0,                                    /* tp_as_number */
  0,                                    /* tp_as_sequence */
  0,                                    /* tp_as_mapping */
  0,                                    /* tp_hash */
  0,                                    /* tp_call */
  0,                                    /* tp_str */
  0,                                    /* tp_getattro */
  0,                                    /* tp_setattro */
  0,                                    /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
  IpMetaDocstring,      /* tp_doc */
  0,		               /* tp_traverse */
  0,		               /* tp_clear */
  0,		               /* tp_richcompare */
  0,		               /* tp_weaklistoffset */
  0,		               /* tp_iter */
  0,		               /* tp_iternext */
  IpMeta_methods,             /* tp_methods */
  0,             /* tp_members */
  0,                         /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  (initproc)IpMeta_init,  /* tp_init */
  0,                         /* tp_alloc */
  IpMeta_new,             /* tp_new */
};

PyTypeObject *_pyipmeta_ipmeta_get_IpMetaType()
{
  return &IpMetaType;
}
