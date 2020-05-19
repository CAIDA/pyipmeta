/*
 * This file is part of pyipmeta
 *
 * CAIDA, UC San Diego
 * corsaro-info@caida.org
 *
 * Copyright (C) 2012 The Regents of the University of California.
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
    PYSTR_FORMAT(pystr, arg_tuple);}

#if 0
/* Look up an IP address or a prefix */
static PyObject *
Provider_lookup(ProviderObject *self, PyObject *args)
{
  if (ipmeta_is_provider_enabled(self->prov) == 0) {
    PyErr_SetString(PyExc_RuntimeError,
                    "Cannot perform lookup before provider is enabled.");
    return NULL;
  }

  const char *pyaddrstr = NULL;
  /* get the prefix/address argument */
  if (!PyArg_ParseTuple(args, "s", &pyaddrstr)) {
    return NULL;
  }

  /* we need to copy the string because python is trusting that we don't mess
     with it */
  char *addrstr = strdup(pyaddrstr);
  if (!addrstr) {
    return NULL;
  }

  /* extract the mask from the prefix */
  char *mask_str = addrstr;
  uint8_t mask;
  if((mask_str = strchr(addrstr, '/')) != NULL) {
    *mask_str = '\0';
    mask_str++;
    mask = atoi(mask_str);
  } else {
    mask = 32;
  }
  uint32_t addr = inet_addr(addrstr);

  /* create a list */
  PyObject *list = NULL;
  if((list = PyList_New(0)) == NULL)
    return NULL;

  ipmeta_record_set_t *set = NULL;
  PyObject *pyrec = NULL;

  // a bit inefficient, but we create a record set just for this single use
  if ((set = ipmeta_record_set_init()) == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to create record set");
    goto err;
  }

  if (mask == 32) {
    if (ipmeta_provider_lookup_records(self->prov, addr, mask, set) < 0) {
      PyErr_SetString(PyExc_RuntimeError, "Failed to lookup IP address");
      goto err;
    }
  } else {
    if (ipmeta_provider_lookup_record_single(self->prov, addr, set) < 0) {
      PyErr_SetString(PyExc_RuntimeError, "Failed to lookup prefix");
      goto err;
    }
  }

  ipmeta_record_set_rewind(set);
  ipmeta_record_t *record = NULL;
  uint32_t num_ips = 0;
  while ((record = ipmeta_record_set_next(set, &num_ips)) != NULL) {
    pyrec = _pyipmeta_record_as_dict(record, num_ips);
    if(PyList_Append(list, pyrec) == -1) {
      goto err;
    }
    Py_DECREF(pyrec);
    pyrec = NULL;
  }
  ipmeta_record_set_free(&set);

  return list;

 err:
  ipmeta_record_set_free(&set);
  if (list != NULL) {
    Py_DECREF(list);
  }
  if (pyrec != NULL) {
    Py_DECREF(pyrec);
  }
  return NULL;
}
#endif

static PyMethodDef Provider_methods[] = {

#if 0
  {
    "lookup",
    (PyCFunction)Provider_lookup,
    METH_VARARGS,
    "Look up metadata for an IP address or prefix"
  },
#endif

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
