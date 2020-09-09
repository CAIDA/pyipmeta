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
#ifndef ___pyipmeta_provider_H
#define ___pyipmeta_provider_H

#include <Python.h>
#include <libipmeta.h>

typedef struct {
  PyObject_HEAD

  /* IpMeta handle */
  PyObject *pyipm;

  /* Provider instance Handle */
  ipmeta_provider_t *prov;

} ProviderObject;

/** Expose the ProviderType structure */
PyTypeObject *_pyipmeta_provider_get_ProviderType(void);

/** Expose our new function as it is not exposed to Python */
PyObject *Provider_new(PyObject *pyipm, ipmeta_provider_t *prov);

#endif /* ___pyipmeta_provider_H */
