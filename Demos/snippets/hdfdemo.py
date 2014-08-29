#!/usr/bin/env python
# Author: Subhasis Ray

import sys
sys.path.append('../../python')
import os
os.environ['NUMPTHREADS'] = '1'
import numpy
import moose

def example():
    """In this example 

    1. We create a passive neuronal compartment `comp`.

    2. We create an HDF5DataWriter object `hdfwriter` for writing to a
       file ``output_hdfdemo.h5``.  The `mode` of the HDF5DataWriter
       is set to `2` which means if a file of the same name exists, it
       will be overwritten.

    3. The membrane voltage `Vm` and membrane current `Im` of `comp`
       are connected to `hdfwriter` for recording.

    4. We set some attributes of the datasets and the file.

    5. We run the simulation, `hdfwriter` records and stores the `Vm`
       and `Im` values over time.

    6. We close the file by calling close() method of `hdfwriter`.

    Running this snippet creates the file ``output_defdemo.h5`` which
    reflects the structure of the model::

        c[0]
        |
        |___im
        |
        |___vm
        

    `im` and `vm` are datasets containing `Im` and `Vm` field values
    recorded from `comp`.

    """
    comp = moose.Compartment('c')
    hdfwriter = moose.HDF5DataWriter('h')
    hdfwriter.mode = 2 # Truncate existing file
    moose.connect(hdfwriter, 'requestOut', comp, 'getVm')
    moose.connect(hdfwriter, 'requestOut', comp, 'getIm')
    
    hdfwriter.filename = 'output_hdfdemo.h5'
    hdfwriter.compressor = 'zlib'
    hdfwriter.compression = 7
    
    # Flush data from memory to disk after accumulating every 1K entries.
    hdfwriter.flushLimit = 1024
    
    # We allow simple attributes of type string, double and long.
    # This allows for file-level metadata/annotation.
    hdfwriter.stringAttr['note'] = 'This is a test.'
    
    # All paths are taken relative to the root. The last token is the name
    # of the attribute.
    hdfwriter.doubleAttr['/c[0]/vm/a_double_attribute'] = 3.141592
    hdfwriter.longAttr['an_int_attribute'] = 8640
    
    # In addition, vectors of string, long and double can also be stored
    # as attributes.
    hdfwriter.stringVecAttr['stringvec'] = ['I wonder', 'why', 'I wonder']
    hdfwriter.doubleVecAttr['c[0]/dvec'] = [3.141592, 2.71828]
    hdfwriter.longVecAttr['c[0]/lvec'] = [3, 14, 1592, 271828]
    
    moose.setClock(0, 1e-5)
    moose.setClock(1, 1e-5)
    moose.setClock(2, 1e-5)
    moose.useClock(0, '/c', 'init')
    moose.useClock(1, '/##[TYPE!=HDF5DataWriter]', 'process')
    moose.useClock(2, '/##[TYPE=HDF5DataWriter]', 'process')
    
    moose.reinit()
    comp.inject = 0.1
    moose.start(30.0)
    hdfwriter.close()
    print 'Finished simulation. Data was saved in', hdfwriter.filename

   
if __name__ == '__main__':
    example()
