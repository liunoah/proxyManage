import os
import tkinter as tk
from tkinter import ttk, messagebox
import json
import winreg


class ProxyConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("代理配置器")
        self.root.geometry("400x300")

        self.proxies = {}
        self.load_proxies()
        self.create_widgets()

    def create_widgets(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, pady=10)

        self.add_btn = tk.Button(self.top_frame, text="添加", command=self.add_proxy)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.edit_btn = tk.Button(self.top_frame, text="修改", command=self.edit_proxy)
        self.edit_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = tk.Button(self.top_frame, text="删除", command=self.delete_proxy)
        self.delete_btn.pack(side=tk.LEFT, padx=5)

        self.use_btn = tk.Button(self.top_frame, text="使用", command=self.use_proxy)
        self.use_btn.pack(side=tk.LEFT, padx=5)

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.bottom_frame, columns=("IP", "Port"))
        self.tree.heading("#0", text="代理名称")
        self.tree.heading("IP", text="IP")
        self.tree.heading("Port", text="端口")
        self.tree.column("#0", width=150)
        self.tree.column("IP", width=150)
        self.tree.column("Port", width=100)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.load_tree()
        self.tree.bind("<<TreeviewSelect>>", self.use_proxy)
    
    def load_proxies(self):
        if os.path.exists("proxies.json"):
            with open("proxies.json", "r") as f:
                self.proxies = json.load(f)
        else:
            self.save_proxies()

    def save_proxies(self):
        with open("proxies.json", "w") as f:
            json.dump(self.proxies, f)

    def load_tree(self):
        for proxy_name, proxy_info in self.proxies.items():
            self.tree.insert("", tk.END, proxy_name, text=proxy_name, values=(proxy_info["ip"], proxy_info["port"]))

    def add_proxy(self):
        def save_new_proxy():
            proxy_name = name_var.get()
            proxy_ip = ip_var.get()
            proxy_port = port_var.get()

            if not proxy_name or not proxy_ip or not proxy_port:
                messagebox.showerror("错误", "请填写所有字段")
                return

            self.proxies[proxy_name] = {"ip": proxy_ip, "port": proxy_port}
            self.save_proxies()
            self.tree.insert("", tk.END, proxy_name, text=proxy_name, values=(proxy_ip, proxy_port))
            add_window.destroy()

        add_window = tk.Toplevel(self.root)
        add_window.title("添加代理")
        add_window.geometry("300x150")

        name_var = tk.StringVar()
        ip_var = tk.StringVar()
        port_var = tk.StringVar()

        tk.Label(add_window, text="代理名称:").grid(row=0, column=0, pady=5, padx=5, sticky=tk.E)
        tk.Entry(add_window, textvariable=name_var).grid(row=0, column=1, padx=5)

        tk.Label(add_window, text="IP 地址:").grid(row=1, column=0, pady=5, padx=5, sticky=tk.E)
        tk.Entry(add_window, textvariable=ip_var).grid(row=1, column=1, padx=5)

        tk.Label(add_window, text="端口:").grid(row=2, column=0, pady=5, padx=5, sticky=tk.E)
        tk.Entry(add_window, textvariable=port_var).grid(row=2, column=1, padx=5)

        tk.Button(add_window, text="保存", command=save_new_proxy).grid(row=3, column=1, pady=10, padx=5, sticky=tk.E)

    def edit_proxy(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("错误", "请选择要编辑的代理")
            return

        def save_edited_proxy():
            proxy_name = name_var.get()
            proxy_ip = ip_var.get()
            proxy_port = port_var.get()

            if not proxy_name or not proxy_ip or not proxy_port:
                messagebox.showerror("错误", "请填写所有字段")
                return

            self.proxies[proxy_name] = {"ip": proxy_ip, "port": proxy_port}
            self.save_proxies()
            self.tree.item(selected_item, text=proxy_name, values=(proxy_ip, proxy_port))
            edit_window.destroy()

        edit_window = tk.Toplevel(self.root)
        edit_window.title("编辑代理")
        edit_window.geometry("300x150")

        name_var = tk.StringVar()
        ip_var = tk.StringVar()
        port_var = tk.StringVar()

        proxy_info = self.proxies[selected_item[0]]

        name_var.set(selected_item[0])
        ip_var.set(proxy_info["ip"])
        port_var.set(proxy_info["port"])

        tk.Label(edit_window, text="代理名称:").grid(row=0, column=0, pady=5, padx=5, sticky=tk.E)
        tk.Entry(edit_window, textvariable=name_var).grid(row=0, column=1, padx=5)

        tk.Label(edit_window, text="IP 地址:").grid(row=1, column=0, pady=5, padx=5, sticky=tk.E)
        tk.Entry(edit_window, textvariable=ip_var).grid(row=1, column=1, padx=5)

        tk.Label(edit_window, text="端口:").grid(row=2, column=0, pady=5, padx=5, sticky=tk.E)
        tk.Entry(edit_window, textvariable=port_var).grid(row=2, column=1, padx=5)

        tk.Button(edit_window, text="保存", command=save_edited_proxy).grid(row=3, column=1, pady=10, padx=5, sticky=tk.E)

    def delete_proxy(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("错误", "请选择要删除的代理")
            return

        del self.proxies[selected_item[0]]
        self.save_proxies()
        self.tree.delete(selected_item)

    def use_proxy(self,event=None):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("错误", "请选择要使用的代理")
            return

        proxy_info = self.proxies[selected_item[0]]

        # socks.set_default_proxy(socks.SOCKS5, proxy_info["ip"], int(proxy_info["port"]))
        # socket.socket = socks.socksocket
        # print(proxy_info["ip"], int(proxy_info["port"]))

        
        # 设置代理服务器地址和端口号
        proxy_server = proxy_info["ip"] + ":" + proxy_info["port"]

        # 打开Internet选项设置项
        internet_settings = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                            r'Software\Microsoft\Windows\CurrentVersion\Internet Settings', 0, winreg.KEY_ALL_ACCESS)

        # 启用代理
        winreg.SetValueEx(internet_settings, 'ProxyEnable', 0, winreg.REG_DWORD, 1)

        # 设置代理服务器地址和端口号
        winreg.SetValueEx(internet_settings, 'ProxyServer', 0, winreg.REG_SZ, proxy_server)

        # 关闭Internet选项设置项
        winreg.CloseKey(internet_settings)
        
        if event==None:
            messagebox.showinfo("代理已设置", f"已将 {selected_item[0]} 设置为当前代理")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProxyConfigurator(root)
    root.mainloop()