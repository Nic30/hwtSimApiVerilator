#include "signal_mem_proxy.h"
#include <structmember.h>
#include <assert.h>


void SignalMemProxy_c_init(SignalMemProxy_t * self, bool is_read_only,
		uint8_t * signal, size_t signal_size, bool is_signed, const char * name,
		std::unordered_set<SignalMemProxy_t*> * signals_checked_for_change) {
	self->is_read_only = is_read_only;
	self->signal = signal;
	assert(signal_size > 0);
	self->signal_size = signal_size;
	self->is_signed = is_read_only;
	self->name = PyUnicode_FromString(name);
	self->signals_checked_for_change = signals_checked_for_change;
	self->value_cache = new uint8_t[signal_size];
}


static PyMemberDef
SignalMemProxy_members[] = {
	{(char *)"name", T_OBJECT, offsetof(SignalMemProxy_t, name), 0, (char *)"name of signal in simulation"},
	{(char *)"_name", T_OBJECT, offsetof(SignalMemProxy_t, _name), 0, (char *)"logical name of signal in simulation"},
	{(char *)"_dtype", T_OBJECT, offsetof(SignalMemProxy_t, _dtype), 0, (char *)"type of signal in simulation"},
	{(char *)"_origin", T_OBJECT, offsetof(SignalMemProxy_t, _origin), 0, (char *)"original signal object for this signal proxy in simulation"},
	{(char *)"_ag", T_OBJECT, offsetof(SignalMemProxy_t, _origin), 0, (char *)"simulation agent which drive or monitor this signal"},
    {nullptr}  /* Sentinel */
};


static PyObject *
SignalMemProxy_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	SignalMemProxy_t *self = (SignalMemProxy_t *)type->tp_alloc(type, 0);
    if (self == nullptr) {
        PyErr_SetString(PyExc_MemoryError, "Can not create new instance of SignalMemProxy");
        return nullptr;
    }
    self->is_read_only = true;
    self->signal = nullptr;
    self->signal_size = 0;
    self->is_signed = false;
    self->name = nullptr;
    self->callbacks = new std::vector<PyObject*>();
    if (self->callbacks == nullptr)
        return nullptr;

    self->value_cache = nullptr;
    self->signals_checked_for_change = nullptr;

    return (PyObject *)self;
}


static PyObject *
SignalMemProxy_read(SignalMemProxy_t* self, PyObject* args)
{
	PyObject * val = _PyLong_FromByteArray(self->signal, self->signal_size, 1, self->is_signed);
    if (val == nullptr) {
    	PyErr_SetString(PyExc_AssertionError, "Can not create a PyLongObject from value in simulation.");
    	return nullptr;
    }
	//Py_INCREF(val);
    return val;
}

static PyObject *
SignalMemProxy_write(SignalMemProxy_t* self, PyObject* args)
{
    PyLongObject * val = nullptr;
	if(!PyArg_ParseTuple(args, "O", &val)) {
		return nullptr;
	}

	if (!PyLong_Check(val)) {
		PyErr_SetString(PyExc_ValueError, "Argument has to be an integer.");
		return nullptr;
	}

	if( _PyLong_AsByteArray(val, self->signal, self->signal_size, 1, self->is_signed)) {
    	return nullptr;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
SignalMemProxy_onChangeAdd(SignalMemProxy_t* self, PyObject* args)
{
    PyObject * cb = nullptr;
	if(!PyArg_ParseTuple(args, "O", &cb)) {
		return nullptr;
	}
	Py_INCREF(cb);

	SignalMemProxy_cache_value(self);
	self->callbacks->push_back(cb);
	self->signals_checked_for_change->insert(self);

    Py_INCREF(Py_None);
    return Py_None;
}

void
SignalMemProxy_cache_value(SignalMemProxy_t* self)
{
    memcpy(self->value_cache, self->signal, self->signal_size);
}

bool
SignalMemProxy_value_changed(SignalMemProxy_t* self)
{
    return memcmp(self->value_cache, self->signal, self->signal_size) != 0;
}

static void
SignalMemProxy_dealloc(SignalMemProxy_t* self)
{
	for (auto cb: *self->callbacks) {
		Py_DECREF(cb);
	}
	delete self->callbacks;
	delete[] self->value_cache;

	Py_DECREF(self->name);
	Py_DECREF(self->_name);
	Py_DECREF(self->_origin);
	Py_DECREF(self->_dtype);

	Py_TYPE(self)->tp_free((PyObject*)self);
}


static PyMethodDef SignalMemProxy_methods[] = {
        {"read", (PyCFunction)SignalMemProxy_read, METH_NOARGS, "read value from signal"},
        {"write", (PyCFunction)SignalMemProxy_write, METH_VARARGS, "write value to signal (signal can not be read only)"},
		{"registerOnChangeCallback", (PyCFunction)SignalMemProxy_onChangeAdd, METH_VARARGS, "add onChange callback function for this signal"},
        {nullptr}  /* Sentinel */
};


PyTypeObject SignalMemProxy_pytype = {
    PyVarObject_HEAD_INIT(nullptr, 0)
    "SignalMemProxy",            /* tp_name */
    sizeof(SignalMemProxy_t),   /* tp_basicsize */
    0,                          /* tp_itemsize */
	(destructor)SignalMemProxy_dealloc, /* tp_dealloc */
    0,                          /* tp_print */
    0,                          /* tp_getattr */
    0,                          /* tp_setattr */
    0,                          /* tp_reserved */
    0,                          /* tp_repr */
    0,                          /* tp_as_number */
    0,                          /* tp_as_sequence */
    0,                          /* tp_as_mapping */
    0,                          /* tp_hash  */
    0,                          /* tp_call */
    0,                          /* tp_str */
    0,                          /* tp_getattro */
    0,                          /* tp_setattro */
    0,                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_BASETYPE,    /* tp_flags */
    "Simulation proxy for signal in HDL simulation\n(set/get for memory in simulator where value of signal is stored)",/* tp_doc */
    0,                          /* tp_traverse */
    0,                          /* tp_clear */
    0,                          /* tp_richcompare */
    0,                          /* tp_weaklistoffset */
    0,                          /* tp_iter */
    0,                          /* tp_iternext */
	SignalMemProxy_methods,     /* tp_methods */
	SignalMemProxy_members,     /* tp_members */
	0,                          /* tp_getset */
    0,                          /* tp_base */
    0,                          /* tp_dict */
    0,                          /* tp_descr_get */
    0,                          /* tp_descr_set */
    0,                          /* tp_dictoffset */
    0,                          /* tp_init */
    0,                          /* tp_alloc */
	(newfunc)SignalMemProxy_new,/* tp_new */
    0, // tp_free
    0, // tp_is_gc
    0, // tp_bases
    0, // tp_mro
    0, // tp_cache
    0, // tp_subclasses
    0, // tp_weaklist
};
