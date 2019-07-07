#!/usr/bin/env python3
# pycdb.py - Python implementation of cdb
# Original Version:
#  https://github.com/euske/pytcdb
#  by Yusuke Shinyama
#  * public domain *
#

import sys
import os
from functools import reduce
from struct import pack, unpack
from array import array

# cdbhash(key)
def cdbhash(s):
    return reduce(lambda h,c: ((h*33) ^ c) & 0xffffffff, s, 5381)

# CDBWriter
class CDBWriter(object):

    # CDBWriter(cdbname)
    def __init__(self, cdbname):
        self.fn = cdbname
        self.fntmp = cdbname+'.tmp'
        self.numentries = 0
        self._fp = open(self.fntmp, 'wb')
        self._pos = 2048   # sizeof((h,p))*256
        self._size = 2048
        self._bucket = [array('I') for _ in range(256)]
        return

    # add(key, val)
    def add(self, k, v):
        assert isinstance(k, bytes)
        assert isinstance(v, bytes)
        (klen, vlen) = (len(k), len(v))
        self._fp.seek(self._pos)
        self._fp.write(pack('<II', klen, vlen))
        self._fp.write(k)
        self._fp.write(v)
        h = cdbhash(k)
        b = self._bucket[h % 256]
        b.append(h)
        b.append(self._pos)
        # sizeof(keylen)+sizeof(datalen)+sizeof(key)+sizeof(data)
        size = 8+klen+vlen
        self._pos += size
        self._size += size+16 # bucket
        self.numentries += 1
        return self

    # finish()
    def finish(self):
        self._fp.seek(self._pos)
        pos_hash = self._pos
        # write hashes
        for b1 in self._bucket:
            if not b1: continue
            blen = len(b1)
            a = array('I', [0]*blen*2)
            for j in range(0, blen, 2):
                (h,p) = (b1[j],b1[j+1])
                i = ((h >> 8) % blen)*2
                while a[i+1]: # is cell[i] already occupied?
                    i = (i+2) % len(a)
                a[i] = h
                a[i+1] = p
            self._fp.write(a.tobytes())
        assert self._fp.tell() == self._size
        # write header
        self._fp.seek(0)
        a = array('I')
        for b1 in self._bucket:
            a.append(pos_hash)
            a.append(len(b1))
            pos_hash += len(b1)*8
        self._fp.write(a.tobytes())
        # close
        self._fp.close()
        os.rename(self.fntmp, self.fn)
        return

# cdbmake(cdbname)
def cdbmake(cdbname):
    return CDBWriter(cdbname)

# cdbget(cdbname, key)
def cdbget(cdbname, k):
    assert isinstance(k, bytes)
    with open(cdbname, 'rb') as fp:
        h = cdbhash(k)
        fp.seek((h % 256) * 8)
        (pos_bucket, ncells) = unpack('<II', fp.read(8))
        if ncells == 0: raise KeyError
        start = (h >> 8) % ncells
        for i in range(ncells):
            fp.seek(pos_bucket + ((start+i) % ncells)*(8))
            (h1, p1) = unpack('<LL', fp.read(8))
            if p1 == 0: raise KeyError
            if h1 == h:
                fp.seek(p1)
                (klen, vlen) = unpack('<II', fp.read(8))
                k1 = fp.read(klen)
                if k1 == k:
                    # return the first match.
                    v1 = fp.read(vlen)
                    return v1
        raise KeyError

# test()
def test():
    cdb_writer = cdbmake('mycdb.cdb')
    d = {
        'key01': 'val01',
        'key02': 'val02',
        'key03': 'val03'
    }
    for (k, v) in d.items():
        cdb_writer.add(k.encode(), v.encode())
    cdb_writer.finish()
    assert cdbget('mycdb.cdb', 'key01'.encode()) == b'val01'
    assert cdbget('mycdb.cdb', 'key02'.encode()) == b'val02'
    assert cdbget('mycdb.cdb', 'key03'.encode()) == b'val03'
    try:
        cdbget('mycdb.cdb', 'key99'.encode())
        assert False
    except KeyError:
        pass
    return

if __name__ == '__main__':
    sys.exit(test())
