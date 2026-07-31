"""Async utility helpers for running coroutines safely inside Streamlit threads."""
import asyncio
import concurrent.futures


def run_async(coro):
    """Executes async coroutine safely inside Streamlit thread context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)
