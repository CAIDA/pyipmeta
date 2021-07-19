/*
 * This file is part of pyipmeta
 *
 * CAIDA, UC San Diego
 * corsaro-info@caida.org
 *
 * Copyright (C) 2017-2020 The Regents of the University of California.
 * Authors: Alistair King
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include "_pyipmeta_record.h"
#include "pyutils.h"
#include <Python.h>
#include <libipmeta.h>

#define PYSTR_SAFE(cstr) ((cstr) ? PYSTR_FROMSTR(cstr) : PYSTR_FROMSTR(""))

/* source_name */
static PyObject *get_source(ipmeta_record_t *rec)
{
  return Py_BuildValue("i", rec->source);
}

/* ID */
static PyObject *get_id(ipmeta_record_t *rec)
{
  return Py_BuildValue("k", rec->id);
}

/* country code (iso2) */
static PyObject *get_country_code(ipmeta_record_t *rec)
{
  return PYSTR_SAFE(rec->country_code);
}

/* continent code */
static PyObject *get_continent_code(ipmeta_record_t *rec)
{
  return PYSTR_SAFE(rec->continent_code);
}

/* region */
static PyObject *get_region(ipmeta_record_t *rec)
{
  return PYSTR_SAFE(rec->region);
}

/* city */
static PyObject *get_city(ipmeta_record_t *rec)
{
  return PYSTR_SAFE(rec->city);
}

/* post code */
static PyObject *get_post_code(ipmeta_record_t *rec)
{
  return PYSTR_SAFE(rec->post_code);
}

/* lat/long */
static PyObject *get_lat_long(ipmeta_record_t *rec)
{
  return Py_BuildValue("dd", rec->latitude, rec->longitude);
}

/* metro code */
static PyObject *get_metro_code(ipmeta_record_t *rec)
{
  return Py_BuildValue("k", rec->metro_code);
}

/* area code */
static PyObject *get_area_code(ipmeta_record_t *rec)
{
  return Py_BuildValue("k", rec->area_code);
}

/* region code */
static PyObject *get_region_code(ipmeta_record_t *rec)
{
  return Py_BuildValue("H", rec->region_code);
}

/* connection speed */
static PyObject *get_connection_speed(ipmeta_record_t *rec)
{
  return PYSTR_SAFE(rec->conn_speed);
}

/* asn list */
static PyObject *get_asns(ipmeta_record_t *rec)
{
  PyObject *list;
  if ((list = PyList_New(0)) == NULL)
    return NULL;

  int i;
  for (i=0; i < rec->asn_cnt; i++) {
    if(PyList_Append(list, Py_BuildValue("k", rec->asn[i])) == -1) {
      goto err;
    }
  }

  return list;

 err:
  Py_DECREF(list);
  return NULL;
}

/* number of IP addresses that this ASN (or ASN group) 'owns' */
static PyObject *get_asn_ip_count(ipmeta_record_t *rec)
{
  return Py_BuildValue("k", rec->asn_ip_cnt);
}

/* list of polygon ids */
static PyObject *get_polygon_ids(ipmeta_record_t *rec)
{
  PyObject *list;
  if ((list = PyList_New(0)) == NULL)
    return NULL;

  int i;
  for (i=0; i < rec->polygon_ids_cnt; i++) {
    if(PyList_Append(list,
                     Py_BuildValue("k", rec->polygon_ids[i])) == -1) {
      goto err;
    }
  }

  return list;

 err:
  Py_DECREF(list);
  return NULL;
}

/* number of IPs in queried prefix covered by this record */
static PyObject *get_matched_ip_count(uint32_t num_ips)
{
  return Py_BuildValue("k", num_ips);
}

PyObject *
_pyipmeta_record_as_dict(ipmeta_record_t *rec, uint32_t num_ips)
{
  PyObject *dict = PyDict_New();
  if (dict == NULL)
    return NULL;

  add_to_dict(dict, "source", get_source(rec));
  add_to_dict(dict, "id", get_id(rec));
  add_to_dict(dict, "country_code", get_country_code(rec));
  add_to_dict(dict, "continent_code", get_continent_code(rec));
  add_to_dict(dict, "region", get_region(rec));
  add_to_dict(dict, "city", get_city(rec));
  add_to_dict(dict, "post_code", get_post_code(rec));
  add_to_dict(dict, "lat_long", get_lat_long(rec));
  add_to_dict(dict, "metro_code", get_metro_code(rec));
  add_to_dict(dict, "area_code", get_area_code(rec));
  add_to_dict(dict, "region_code", get_region_code(rec));
  add_to_dict(dict, "connection_speed",
              get_connection_speed(rec));
  add_to_dict(dict, "asns", get_asns(rec));
  add_to_dict(dict, "asn_ip_count", get_asn_ip_count(rec));
  add_to_dict(dict, "polygon_ids", get_polygon_ids(rec));
  add_to_dict(dict, "matched_ip_count",
              get_matched_ip_count(num_ips));

  return dict;
}
