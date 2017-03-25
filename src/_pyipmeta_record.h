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
#include <Python.h>

#ifndef ___pyipmeta_record_H
#define ___pyipmeta_record_H

#include <libipmeta.h>

typedef struct {
  PyObject_HEAD

  /* Record instance Handle */
  ipmeta_record_t *rec;

  /* number of IPs of the queried prefix that this record covers */
  uint32_t num_ips;

} RecordObject;

/** Expose the RecordType structure */
PyTypeObject *_pyipmeta_record_get_RecordType(void);

/** Expose our new function as it is not exposed to Python */
PyObject *Record_new(ipmeta_record_t *rec, uint32_t num_ips);

#endif /* ___pyipmeta_record_H */
