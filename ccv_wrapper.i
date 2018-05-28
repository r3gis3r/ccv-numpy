%module(docstring="LibCCV bindings for python") libccv

%{
#define SWIG_FILE_WITH_INIT
#include "./ccv/lib/ccv.h"
%}

%include "numpy.i"
%fragment("NumPy_Fragments");
%init %{
import_array()
%}

%include "carrays.i"
%array_class(double, doubleArray);


/* ccv_dense_matrix as input */
%typemap(in)
    (ccv_dense_matrix_t*)
    (PyArrayObject* array=NULL, int is_new_object=0)
{
    array = (PyArrayObject*) obj_to_array_contiguous_allow_conversion($input, NPY_UINT8, &is_new_object);
    if (!array) SWIG_fail;
    int ctype = CCV_8U;
    size_t nl, nc, nb;
    nl = array_size(array, 0);
    nc = array_size(array, 1);
    nb = 1;
    if(array_numdims(array)>=3){
        nb = array_size(array, 2);
    }
    if(nb == 1) ctype |= CCV_C1;
    if(nb == 2) ctype |= CCV_C2;
    if(nb == 3) ctype |= CCV_C3;
    $1 = ccv_dense_matrix_new(nl, nc, ctype, 0, 0);
    memcpy($1->data.u8, array_data(array), nl * nc * nb);
}

%typemap(freearg)
    (ccv_dense_matrix_t*)
{
  if (is_new_object$argnum && array$argnum) Py_DECREF(array$argnum);
  ccv_matrix_free($1);
}

/* ccv_dense_matrix as arg-output */
%typemap(in,numinputs=0) 
    (ccv_dense_matrix_t **)
    (ccv_dense_matrix_t *out_array = 0) 
{
$1 = &out_array;
}

%typemap(argout) ccv_dense_matrix_t ** 
{
  //ccv_dense_matrix_t* out_mat = *$1;
  PyErr_SetString(PyExc_RuntimeError, "Not yet implemented");
  $result = NULL;
//  $result = SWIG_NewPointerObj($1, $1_descriptor, SWIG_POINTER_OWN);
}

/* ccv_array as output */
%typemap(out) ccv_array_t*
{
    $result = NULL;
    if ($1)
    {
        if($1->rsize == sizeof(ccv_rect_t))
        {
            npy_intp dims[2] = { $1->rnum, 4 };
            PyObject* res_array = PyArray_SimpleNew(2, dims, NPY_INT);
            int i;
            int* res_data = array_data(res_array);
            for (i = 0; i < $1->rnum; i++)
            {
                ccv_rect_t* rect = (ccv_rect_t*)ccv_array_get($1, i);
                res_data[i*4 + 0] = rect->x;
                res_data[i*4 + 1] = rect->y;
                res_data[i*4 + 2] = rect->width;
                res_data[i*4 + 3] = rect->height;
            }
            $result = SWIG_Python_AppendOutput($result, res_array);
        }
       
        ccv_array_free($1);
    }

    if($result == NULL)
    {
        PyErr_SetString(PyExc_RuntimeError, "Result not yet implemented");
    }
}


// Ignore obsolete declarations
%ignore ccv_dot;
%ignore ccv_compressive_sensing_reconstruct;
%ignore ccv_icf_multiscale_classifier_cascade_new;


%thread;
%include "./ccv/lib/ccv.h"
%nothread;

