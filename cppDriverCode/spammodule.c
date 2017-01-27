//
//  spammodule.c
//  
//
//  Created by Caleb Wheeler on 1/23/17.
//
//

#include "spammodule.h"

// below this executes the spam_system variable above when the compiled c program is called

static PyObject *
spam_system(PyObject *self, PyObject *args)
{
    const char *command;
    int sts;
    
    if (!PyArg_ParseTuple(args, "s", &command))
        return NULL;
    sts = system(command);
    return Py_BuildValue("i", sts);
}

// This is the module's initialization functions

static PyMethodDef SpamMethods[] = {
    {"system",  spam_system, METH_VARARGS,
        "Execute a shell command."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initspam(void)
{
    (void) Py_InitModule("spam", SpamMethods);
}

// below this exicutes the spam_system variable above when the complided c programm is called

int
main(int argc, char *argv[])
{
    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(argv[0]);
    
    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();
    
    /* Add a static module */
    initspam();
    
}
