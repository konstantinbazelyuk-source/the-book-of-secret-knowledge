"""Frozen multiprocessing-safe CLI entrypoint for personal Windows installer."""
import multiprocessing
if __name__ == '__main__':
    multiprocessing.freeze_support()
    from miner import main
    main()