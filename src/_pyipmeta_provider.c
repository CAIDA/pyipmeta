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

#define ProviderDocstring "IpMeta Provider object"

#define ProviderTypeName "_pyipmeta.Provider"

static void
Provider_dealloc(ProviderObject *self)
{
  Py_DECREF(self->pyipm);
  self->pyipm = NULL;
  self->prov = NULL;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
Provider_init(ProviderObject *self,
	          PyObject *args, PyObject *kwds)
{
  return 0;
}

/* enabled? */
static PyObject *
Provider_get_enabled(ProviderObject *self, void *closure)
{
  if (ipmeta_is_provider_enabled(self->prov) != 0) {
    Py_RETURN_TRUE;
  }

  Py_RETURN_FALSE;
}

/* id */
static PyObject *
Provider_get_id(ProviderObject *self, void *closure)
{
  return Py_BuildValue("i", ipmeta_get_provider_id(self->prov));
}

/* mask */
static PyObject *
Provider_get_mask(ProviderObject *self, void *closure)
{
  return Py_BuildValue("i",
      IPMETA_PROV_TO_MASK(ipmeta_get_provider_id(self->prov)));
}

/* name */
static PyObject *
Provider_get_name(ProviderObject *self, void *closure)
{
  return PYSTR_FROMSTR(ipmeta_get_provider_name(self->prov));
}

static PyObject *
Provider_repr(PyObject *pyself)
{
  ProviderObject *self = (ProviderObject *)pyself;
  PyObject *arg_tuple = Py_BuildValue("OOO",
                                      Provider_get_id(self, NULL),
                                      Provider_get_name(self, NULL),
                                      Provider_get_enabled(self, NULL));

  PyObject *pystr =
    PYSTR_FROMSTR("<"ProviderTypeName" (id: %i, name: %s, enabled: %s)>");

  return
    PYSTR_FORMAT(pystr, arg_tuple);
}

static PyMethodDef Provider_methods[] = {
  {NULL}  /* Sentinel */
};

static PyGetSetDef Provider_getsetters[] = {

  /* enabled */
  {
    "enabled",
    (getter)Provider_get_enabled, NULL,
    "Enabled?",
    NULL
  },

  /* id */
  {
    "id",
    (getter)Provider_get_id, NULL,
    "ID",
    NULL
  },

  /* mask */
  {
    "mask",
    (getter)Provider_get_mask, NULL,
    "Mask",
    NULL
  },

  /* Name */
  {
    "name",
    (getter)Provider_get_name, NULL,
    "Name",
    NULL
  },

  {NULL} /* Sentinel */
};

static PyTypeObject ProviderType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  ProviderTypeName,             /* tp_name */
  sizeof(ProviderObject), /* tp_basicsize */
  0,                                    /* tp_itemsize */
  (destructor)Provider_dealloc,        /* tp_dealloc */
  0,                                    /* tp_print */
  0,                                    /* tp_getattr */
  0,                                    /* tp_setattr */
  0,                                    /* tp_compare */
  Provider_repr,                                    /* tp_repr */
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
  ProviderDocstring,      /* tp_doc */
  0,		               /* tp_traverse */
  0,		               /* tp_clear */
  0,		               /* tp_richcompare */
  0,		               /* tp_weaklistoffset */
  0,		               /* tp_iter */
  0,		               /* tp_iternext */
  Provider_methods,             /* tp_methods */
  0,             /* tp_members */
  Provider_getsetters,                         /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  (initproc)Provider_init,  /* tp_init */
  0,                         /* tp_alloc */
  0,             /* tp_new */
};

PyTypeObject *_pyipmeta_provider_get_ProviderType()
{
  return &ProviderType;
}

/* only available to c code */
PyObject *Provider_new(PyObject *pyipm, ipmeta_provider_t *prov)
{
  ProviderObject *self;

  self = (ProviderObject *)(ProviderType.tp_alloc(&ProviderType, 0));
  if(self == NULL) {
    return NULL;
  }

  // claim a reference to the IpMeta instance, since destroying the IpMeta
  // instance also destroys the provider.
  Py_INCREF(pyipm);
  self->pyipm = pyipm;
  self->prov = prov;

  return (PyObject *)self;
}
