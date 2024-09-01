import tkinter as tk
from tkinter import filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.stats import linregress

class DataViewer:
    def __init__(self, master):
        self.master = master
        self.current_line = 0
        self.is_linear_analyzed = False
        self.lines = []

        # 创建标签、按钮、文本框和复选框
        self.label = tk.Label(master, text="请选择文件:")
        self.label.pack(pady=10)

        self.button = tk.Button(master, text="选择文件", command=self.on_button_click)
        self.button.pack(pady=10)

        self.analyze_button = tk.Button(master, text="手动线性分析", command=self.on_analyze_button_click)
        self.analyze_button.pack(pady=10)

        self.auto_analyze_var = tk.IntVar()
        self.auto_analyze_checkbox = tk.Checkbutton(master, text="自动线性分析", variable=self.auto_analyze_var)
        self.auto_analyze_checkbox.pack(pady=10)

        self.text_var = tk.StringVar()
        self.info_text = tk.Entry(master, textvariable=self.text_var, state='readonly', width=50)
        self.info_text.pack(pady=10)

        # 创建画布
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack()

        # 创建Treeview用于显示线性分析的结果
        self.tree = ttk.Treeview(master, columns=("row", "slope", "intercept", "r_value"))
        self.tree.heading("#0", text="行数")
        self.tree.heading("row", text="行数")
        self.tree.heading("slope", text="斜率 (Slope)")
        self.tree.heading("intercept", text="截距 (Intercept)")
        self.tree.heading("r_value", text="R值 (R-value)")
        self.tree.pack(pady=10)

        # 隐藏默认的行号列
        self.tree["show"] = "headings"

        # 在初始化时清空 Treeview 中的内容
        self.tree.delete(*self.tree.get_children())

        # 监听键盘事件
        master.bind("<Up>", self.on_up_key)
        master.bind("<Down>", self.on_down_key)

        # 显示初始信息
        self.update_info_text()

        # 启动自动线性分析任务
        self.auto_analyze()
        
        # 创建保存按钮
        self.save_button = tk.Button(master, text="保存分析结果", command=self.on_save_button_click)
        self.save_button.pack(pady=10)

    def on_button_click(self):
        try:
            # 弹出文件选择对话框
            file_path = filedialog.askopenfilename()

            # 检查用户是否取消了文件选择
            if not file_path:
                return

            # 打开文件并读取数据
            with open(file_path, 'r') as file:
                self.lines = file.readlines()
                self.is_linear_analyzed = False  # 重新选择文件后，重置线性分析标志

                # 更新画布和Treeview显示
                self.update_display()

        except Exception as e:
            self.label.config(text="发生错误: " + str(e))

    def on_analyze_button_click(self):
        # 手动线性分析按钮点击事件
        if not self.is_linear_analyzed and self.lines:
            # 取当前行的数据
            line = self.lines[self.current_line]
            data = [float(x) for x in line.strip().split()[1:]]  # 从第二个元素开始读取数据

            # 计算线性回归
            x_values = np.arange(0.2, 1.2, 0.2)
            slope, intercept, r_value, p_value, std_err = linregress(x_values, data)

            # 在Treeview中插入一行数据
            row_number = self.current_line + 1
            self.tree.insert("", "end", values=(row_number, slope, intercept, r_value))

            # 绘制回归线
            self.ax.plot(x_values, intercept + slope * x_values, color='red', label='线性回归')

            # 刷新画布
            self.canvas.draw()

            # 设置线性分析标志为True，防止重复分析
            self.is_linear_analyzed = True

            # 显示图例
            self.ax.legend()

            # 更新信息文本
            self.update_info_text()

    def update_display(self):
        # 清空画布上的内容
        self.ax.clear()

        # 取当前行的数据
        line = self.lines[self.current_line]
        data = [float(x) for x in line.strip().split()[1:]]  # 从第二个元素开始读取数据
        name = line.strip().split()[0]  # 第一个元素作为名字

        # 绘制散点图
        x_values = np.arange(0.2, 1.2, 0.2)
        self.ax.scatter(x_values, data, label=name)

        # 设置x轴标签
        self.ax.set_xlabel('数据点')

        # 刷新画布
        self.canvas.draw()

        # 更新标签文本显示当前行数
        self.label.config(text=f"总共 {len(self.lines)} 行数据")

        # 更新信息文本
        self.update_info_text()

    def update_info_text(self):
        # 显示当前行号和第一列数据
        if self.lines:
            line_data = self.lines[self.current_line].strip().split()
            current_row_number = self.current_line + 1
            first_column_data = line_data[0]
            self.text_var.set(f"当前行号: {current_row_number}, 第一列数据: {first_column_data}")

    def on_up_key(self, event):
        # 上键，选择上一行
        if self.current_line > 0:
            self.current_line -= 1
            self.is_linear_analyzed = False  # 每次切换行重置线性分析标志
            self.update_display()

    def on_down_key(self, event):
        # 下键，选择下一行
        if self.current_line < len(self.lines) - 1:
            self.current_line += 1
            self.is_linear_analyzed = False  # 每次切换行重置线性分析标志
            self.update_display()

    def auto_analyze(self):
        # 自动线性分析任务
        if self.auto_analyze_var.get():
            self.on_analyze_button_click()  # 执行线性分析
        self.master.after(1000, self.auto_analyze)  # 每隔1秒自动执行一次
        
    def on_save_button_click(self):
        # 保存分析结果到文件
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                # 写入表头
                file.write("行数\t斜率\t截距\tR值\n")

                # 遍历Treeview中的数据，并写入文件
                for child in self.tree.get_children():
                    values = self.tree.item(child, 'values')
                    file.write(f"{values[0]}\t{values[1]}\t{values[2]}\t{values[3]}\n")

# 创建主窗口
app = tk.Tk()
app.title("逐行显示数据的GUI应用")

# 创建DataViewer实例
data_viewer = DataViewer(app)

# 启动主循环
app.mainloop()
