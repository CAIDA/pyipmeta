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
/*
 * This file is part of pybgpstream
 *
 * CAIDA, UC San Diego
 * bgpstream-info@caida.org
 *
 * Copyright (C) 2012 The Regents of the University of California.
 * Authors: Alistair King, Chiara Orsini
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

#include "_pyipmeta_record.h"
#include "pyutils.h"
#include <Python.h>
#include <libipmeta.h>

#define RecordDocstring "IpMeta Record object"

#define PYSTR_SAFE(cstr) ((cstr) ? PYSTR_FROMSTR(cstr) : PYSTR_FROMSTR(""))

static void Record_dealloc(RecordObject *self)
{
  self->rec = NULL;
  Py_TYPE(self)->tp_free((PyObject *)self);
}

static int Record_init(RecordObject *self, PyObject *args, PyObject *kwds)
{
  return 0;
}

/* ID */
static PyObject *Record_get_id(RecordObject *self, void *closure)
{
  return Py_BuildValue("k", self->rec->id);
}

/* country code (iso2) */
static PyObject *Record_get_country_code(RecordObject *self, void *closure)
{
  return PYSTR_SAFE(self->rec->country_code);
}

/* continent code */
static PyObject *Record_get_continent_code(RecordObject *self, void *closure)
{
  return PYSTR_SAFE(self->rec->continent_code);
}

/* region */
static PyObject *Record_get_region(RecordObject *self, void *closure)
{
  return PYSTR_SAFE(self->rec->region);
}

/* city */
static PyObject *Record_get_city(RecordObject *self, void *closure)
{
  return PYSTR_SAFE(self->rec->city);
}

/* post code */
static PyObject *Record_get_post_code(RecordObject *self, void *closure)
{
  return PYSTR_SAFE(self->rec->post_code);
}

/* lat/long */
static PyObject *Record_get_lat_long(RecordObject *self, void *closure)
{
  return Py_BuildValue("dd", self->rec->latitude, self->rec->longitude);
}

/* lat */
static PyObject *Record_get_lat(RecordObject *self, void *closure)
{
  return Py_BuildValue("d", self->rec->latitude);
}

/* long */
static PyObject *Record_get_long(RecordObject *self, void *closure)
{
  return Py_BuildValue("d", self->rec->longitude);
}

/* metro code */
static PyObject *Record_get_metro_code(RecordObject *self, void *closure)
{
  return Py_BuildValue("k", self->rec->metro_code);
}

/* area code */
static PyObject *Record_get_area_code(RecordObject *self, void *closure)
{
  return Py_BuildValue("k", self->rec->area_code);
}

/* region code */
static PyObject *Record_get_region_code(RecordObject *self, void *closure)
{
  return Py_BuildValue("H", self->rec->region_code);
}

/* connection speed */
static PyObject *Record_get_connection_speed(RecordObject *self, void *closure)
{
  return PYSTR_SAFE(self->rec->conn_speed);
}

/* asn list */
static PyObject *Record_get_asns(RecordObject *self, void *closure)
{
  PyObject *list;
  if ((list = PyList_New(0)) == NULL)
    return NULL;

  int i;
  for (i=0; i < self->rec->asn_cnt; i++) {
    if(PyList_Append(list, Py_BuildValue("k", self->rec->asn[i])) == -1) {
      goto err;
    }
  }

  return list;

 err:
  Py_DECREF(list);
  return NULL;
}

/* number of IP addresses that this ASN (or ASN group) 'owns' */
static PyObject *Record_get_asn_ip_count(RecordObject *self, void *closure)
{
  return Py_BuildValue("k", self->rec->asn_ip_cnt);
}

/* list of polygon ids */
static PyObject *Record_get_polygon_ids(RecordObject *self, void *closure)
{
  PyObject *list;
  if ((list = PyList_New(0)) == NULL)
    return NULL;

  int i;
  for (i=0; i < self->rec->polygon_ids_cnt; i++) {
    if(PyList_Append(list,
                     Py_BuildValue("k", self->rec->polygon_ids[i])) == -1) {
      goto err;
    }
  }

  return list;

 err:
  Py_DECREF(list);
  return NULL;
}

/* number of IPs in queried prefix covered by this record */
static PyObject *Record_get_matched_ip_count(RecordObject *self, void *closure)
{
  return Py_BuildValue("k", self->num_ips);
}

static PyObject *
Record_as_dict(PyObject *pyself)
{
  RecordObject *self = (RecordObject *)pyself;

  /* create the dictionary */
  PyObject *dict = PyDict_New();
  if (dict == NULL)
    return NULL;

  add_to_dict(dict, "id", Record_get_id(self, NULL));
  add_to_dict(dict, "country_code", Record_get_country_code(self, NULL));
  add_to_dict(dict, "continent_code", Record_get_continent_code(self, NULL));
  add_to_dict(dict, "region", Record_get_region(self, NULL));
  add_to_dict(dict, "city", Record_get_city(self, NULL));
  add_to_dict(dict, "post_code", Record_get_post_code(self, NULL));
  add_to_dict(dict, "lat_long", Record_get_lat_long(self, NULL));
  add_to_dict(dict, "metro_code", Record_get_metro_code(self, NULL));
  add_to_dict(dict, "area_code", Record_get_area_code(self, NULL));
  add_to_dict(dict, "region_code", Record_get_region_code(self, NULL));
  add_to_dict(dict, "connection_speed",
              Record_get_connection_speed(self, NULL));
  add_to_dict(dict, "asns", Record_get_asns(self, NULL));
  add_to_dict(dict, "asn_ip_count", Record_get_asn_ip_count(self, NULL));
  add_to_dict(dict, "polygon_ids", Record_get_polygon_ids(self, NULL));
  add_to_dict(dict, "matched_ip_count",
              Record_get_matched_ip_count(self, NULL));

  return dict;
}

static PyMethodDef Record_methods[] = {

  {
    "as_dict",
    (PyCFunction)Record_as_dict,
    METH_VARARGS,
    "Convert the Record to a standard dict "
    "(useful for printing or conversion to json)"
  },

  {NULL} /* Sentinel */
};

static PyGetSetDef Record_getsetters[] = {

  /* ID */
  {"id", (getter)Record_get_id, NULL, "ID", NULL},

  /* country code (iso2) */
  {"country_code", (getter)Record_get_country_code, NULL,
   "ISO2 Country Code", NULL},

  /* continent code */
  {"continent_code", (getter)Record_get_continent_code, NULL,
   "Continent Code", NULL},

  /* region */
  {"region", (getter)Record_get_region, NULL, "Region", NULL},

  /* city */
  {"city", (getter)Record_get_city, NULL, "City", NULL},

  /* post code */
  {"post_code", (getter)Record_get_post_code, NULL, "Post Code", NULL},

  /* lat/long */
  {"lat_long", (getter)Record_get_lat_long, NULL, "(Lat, Long)", NULL},

  /* lat */
  {"latitude", (getter)Record_get_lat, NULL, "Latitude", NULL},

  /* long */
  {"longitude", (getter)Record_get_long, NULL, "Longitude", NULL},

  /* metro code */
  {"metro_code", (getter)Record_get_metro_code, NULL, "Metro Code", NULL},

  /* area code */
  {"area_code", (getter)Record_get_area_code, NULL, "Area Code", NULL},

  /* region code */
  {"region_code", (getter)Record_get_region_code, NULL, "Region Code", NULL},

  /* connection speed */
  {"connection_speed", (getter)Record_get_connection_speed, NULL,
   "Connection Speed", NULL},

  /* asn list */
  {"asns", (getter)Record_get_asns, NULL, "ASNs", NULL},

  /* number of IP addresses that this ASN (or ASN group) 'owns' */
  {"asn_ip_count", (getter)Record_get_asn_ip_count, NULL,
   "Number of IPs 'owned' by these ASes", NULL},

  /* list of polygon ids */
  {"polygon_ids", (getter)Record_get_polygon_ids, NULL,
   "Polygon Table IDs", NULL},

  /* number of IPs in queried prefix covered by this record */
  {"matched_ip_count", (getter)Record_get_matched_ip_count, NULL,
   "Number of IPs in queried prefix covered by this record", NULL},

  {NULL} /* Sentinel */
};

static PyTypeObject RecordType = {
  PyVarObject_HEAD_INIT(NULL, 0) "_pyipmeta.Record", /* tp_name */
  sizeof(RecordObject),                                 /* tp_basicsize */
  0,                                                     /* tp_itemsize */
  (destructor)Record_dealloc,                           /* tp_dealloc */
  0,                                                     /* tp_print */
  0,                                                     /* tp_getattr */
  0,                                                     /* tp_setattr */
  0,                                                     /* tp_compare */
  0,                                                     /* tp_repr */
  0,                                                     /* tp_as_number */
  0,                                                     /* tp_as_sequence */
  0,                                                     /* tp_as_mapping */
  0,                                                     /* tp_hash */
  0,                                                     /* tp_call */
  0,                                                     /* tp_str */
  0,                                                     /* tp_getattro */
  0,                                                     /* tp_setattro */
  0,                                                     /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,              /* tp_flags */
  RecordDocstring,                                      /* tp_doc */
  0,                                                     /* tp_traverse */
  0,                                                     /* tp_clear */
  0,                                                     /* tp_richcompare */
  0,                                                     /* tp_weaklistoffset */
  0,                                                     /* tp_iter */
  0,                                                     /* tp_iternext */
  Record_methods,                                       /* tp_methods */
  0,                                                     /* tp_members */
  Record_getsetters,                                    /* tp_getset */
  0,                                                     /* tp_base */
  0,                                                     /* tp_dict */
  0,                                                     /* tp_descr_get */
  0,                                                     /* tp_descr_set */
  0,                                                     /* tp_dictoffset */
  (initproc)Record_init,                                /* tp_init */
  0,                                                     /* tp_alloc */
  0,                                                     /* tp_new */
};

PyTypeObject *_pyipmeta_record_get_RecordType()
{
  return &RecordType;
}

/* only available to c code */
PyObject *Record_new(ipmeta_record_t *rec, uint32_t num_ips)
{
  RecordObject *self;

  self = (RecordObject *)(RecordType.tp_alloc(&RecordType, 0));
  if (self == NULL) {
    return NULL;
  }

  self->rec = rec;
  self->num_ips = num_ips;

  return (PyObject *)self;
}
