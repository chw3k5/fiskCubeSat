#pragma once

//#include "types.h"

#ifndef _WINDOWS
    #include <pthread.h>
#endif

namespace kmk
{

	typedef int (*ThreadProcFunc)(void *);

	/** @brief A wrapper around the windows thread API.
	*/
	class Thread
	{
	public:
	
		Thread();
		~Thread ();

        bool Start (ThreadProcFunc func, void *pArg);

		void CancelSyncIO();

        int WaitForTermination();

        static void Sleep(int timeInMs);

	private:

		struct CallbackArgs
		{
			ThreadProcFunc callbackProc;
			void *pArg;
		};

		CallbackArgs _callbackArgs;

#ifdef _WINDOWS
		HANDLE m_handle;
		DWORD  m_id;
#else
        pthread_t m_thread;
#endif
		

#ifdef _WINDOWS
		static DWORD WINAPI CallbackProc(void *pArg);
#else
		static void *CallbackProc(void *pArg);

#endif
	};


} // namespace kmk
