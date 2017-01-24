#include "stdafx.h"
#include "Thread.h"
#include <memory.h>

#ifndef _WINDOWS
    #include <time.h>
#endif

namespace kmk
{
	

	Thread::Thread()
#ifdef _WINDOWS
		: m_handle(0), m_id(0)
#endif
	{
		memset(&_callbackArgs, 0, sizeof(CallbackArgs));
	}

    bool Thread::Start (ThreadProcFunc pFunction, void *pArg)
	{
		_callbackArgs.callbackProc = pFunction;
		_callbackArgs.pArg = pArg;

#ifdef _WINDOWS
        m_handle = CreateThread(0, 
								0, 
								CallbackProc,         
								&_callbackArgs,         
                                0,
								&m_id); 
		return (m_handle != NULL);
#else
        return (pthread_create(&m_thread, NULL, CallbackProc, &_callbackArgs) == 0);
#endif
	}


	Thread::~Thread ()
	{
#ifdef _WINDOWS
		CloseHandle (m_handle);
		m_handle = 0;
		m_id = 0;
#endif
	}

    int Thread::WaitForTermination()
	{
#ifdef _WINDOWS
        return WaitForSingleObject(m_handle, INFINITE);
#else
        return pthread_join(m_thread, NULL);
#endif
	}

#ifdef _WINDOWS
	DWORD WINAPI Thread::CallbackProc(void *pArg)
	{
		CallbackArgs *pArgs = (CallbackArgs*)pArg;
		if (pArgs->callbackProc != NULL)
		{ 
			return (*pArgs->callbackProc)(pArgs->pArg);
		}

		return 0;
	}
#else
	void *Thread::CallbackProc(void *pArg)
	{
		CallbackArgs *pArgs = (CallbackArgs*)pArg;
		if (pArgs->callbackProc != NULL)
		{
			return (void*)(*pArgs->callbackProc)(pArgs->pArg);
		}

		return (void*)0;
	}
#endif

void Thread::Sleep(int timeInMs)
{
#ifdef _WINDOWS
    ::Sleep(timeInMs);
#else
    struct timespec time;
    time.tv_sec = 0;
    time.tv_nsec = timeInMs * 1000000;
    nanosleep(&time, &time);
#endif
}

} // namespace kmk


