"""Personal desktop window launching the *actual* authenticated local miner.

The native Windows build bundles this and the separate worker executable.
The desktop window remains open as the background HTTP controller runs.
"""
from __future__ import annotations
import multiprocessing
import os
from pathlib import Path
import sys
import threading
import webbrowser


def main():
    import tkinter as tk
    from tkinter import messagebox
    from app import Server, Handler, get_token, DEFAULT_DATA
    from ripple_miner.controller import Controller

    data=DEFAULT_DATA
    data.mkdir(parents=True,exist_ok=True)
    controller=Controller(data)
    token=get_token(data)
    try:
        server=Server(('127.0.0.1',8877),Handler,controller,token)
    except OSError as exc:
        controller.close()
        root=tk.Tk();root.withdraw()
        messagebox.showerror('Ripple Miner','Could not start the local mining dashboard on port 8877: '+str(exc))
        root.destroy()
        return 1
    node=Path(sys.executable).resolve().parent.parent/'node'/'node.exe'
    if getattr(sys,'frozen',False) and node.is_file():os.environ['RIPPLE_NODE_BIN']=str(node)
    webthread=threading.Thread(target=server.serve_forever,kwargs={'poll_interval':.25},daemon=True)
    webthread.start()

    root=tk.Tk();root.title('Ripple Miner · Personal Controller');root.geometry('460x310')
    root.minsize(420,280)
    root.configure(bg='#14232a')
    fg='#e1f4ef'; bg='#14232a'
    tk.Label(root,text='RIPPLE MINER',font=('Segoe UI',22,'bold'),fg='#8ce3ce',bg=bg).pack(pady=(24,8))
    tk.Label(root,text='Your local authenticated mining controller is running.',fg=fg,bg=bg).pack(pady=5)
    tk.Button(root,text='Open Mining Dashboard',font=('Segoe UI',12,'bold'),command=lambda:webbrowser.open('http://127.0.0.1:8877')).pack(pady=8)
    tk.Button(root,text='Copy Dashboard Access Token',command=lambda:(root.clipboard_clear(),root.clipboard_append(token),root.update())).pack(pady=5)
    tk.Label(root,text='Pool credentials are entered in the dashboard.\nKeep this window open while mining.',fg=fg,bg=bg,justify='center').pack(pady=7)
    closing=False
    def finish():
        nonlocal closing
        if closing:return
        closing=True
        server.shutdown();server.server_close()
        controller.close()
        root.destroy()
    root.protocol('WM_DELETE_WINDOW',finish)
    root.mainloop()
    return 0

if __name__=='__main__':
    multiprocessing.freeze_support()
    raise SystemExit(main())