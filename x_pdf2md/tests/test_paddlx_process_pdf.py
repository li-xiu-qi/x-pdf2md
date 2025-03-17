import os
import time
import psutil
import threading
from typing import Dict

from paddlex import create_model

class ResourceMonitor:
    def __init__(self, interval=0.1):
        self.interval = interval
        self.cpu_percentages = []
        self.memory_usages = []
        self._stop_event = threading.Event()
        self.process = psutil.Process(os.getpid())

    def start(self):
        self.cpu_percentages = []
        self.memory_usages = []
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._monitor)
        self._thread.daemon = True
        self._thread.start()
        
    def stop(self):
        self._stop_event.set()
        self._thread.join()
        
    def _monitor(self):
        while not self._stop_event.is_set():
            try:
                self.cpu_percentages.append(self.process.cpu_percent())
                self.memory_usages.append(self.process.memory_info().rss / 1024 / 1024)  # MB
            except Exception:
                pass
            time.sleep(self.interval)
            
    def get_stats(self):
        if not self.cpu_percentages or not self.memory_usages:
            return {"avg_cpu": 0, "max_cpu": 0, "avg_memory": 0, "max_memory": 0}
            
        return {
            "avg_cpu": sum(self.cpu_percentages) / len(self.cpu_percentages),
            "max_cpu": max(self.cpu_percentages),
            "avg_memory": sum(self.memory_usages) / len(self.memory_usages),
            "max_memory": max(self.memory_usages)
        }

def detect_layout(image_path: str,
                  output_path: str = "./layout_output/layout_detection.json",
                  model_name= "PP-DocLayout-L",
                  batch_size: int = 8,
                  resource_monitor=None) -> Dict:
    """
    检测文档版面布局

    参数:
        image_path: 图像路径
        output_path: 输出路径
        model_name: 模型名称
        batch_size: 批次大小
        resource_monitor: 资源监控器

    返回:
        版面分析结果
    """
    # 创建输出目录
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # 设置json输出路径
    json_path = output_path if output_path.endswith(".json") else os.path.join(output_dir, "layout_detection.json")

    model = create_model(model_name=model_name)
    
    if resource_monitor:
        resource_monitor.start()
        
    start_time = time.time()
    output = model.predict(image_path, batch_size=batch_size, layout_nms=True)
    
    end_index = 0
    # 保存结果到JSON            
    for i, res in enumerate(output):
        print(f"第{i+1}页：")
        res.save_to_json(save_path=f"{json_path[:-5]}_{i+1}.json")
        res.save_to_img(save_path=f"{json_path[:-5]}_{i+1}.png")
        end_index = end_index + 1
    end_time = time.time()
    
    if resource_monitor:
        resource_monitor.stop()
        resource_stats = resource_monitor.get_stats()
    else:
        resource_stats = {}
    
    print(f"Batch size: {batch_size}, Time taken: {end_time - start_time:.2f} seconds")

    return {
        "time": end_time - start_time, 
        "batch_size": batch_size, 
        "pages": end_index,
        **resource_stats
    }
        
def benchmark_batch_sizes(image_path: str, batch_sizes=None):
    """测试不同批次大小的处理时间和资源使用情况"""
    if batch_sizes is None:
        batch_sizes = [1, 2, 4, 8, 16]
    
    results = []
    for batch_size in batch_sizes:
        print(f"\nTesting with batch_size={batch_size}")
        monitor = ResourceMonitor()
        result = detect_layout(image_path, batch_size=batch_size, resource_monitor=monitor)
        results.append(result)
    
    print("\nBenchmark Results:")
    print("-----------------")
    print(f"{'Batch Size':^10}|{'Pages':^7}|{'Time (s)':^10}|{'Avg CPU (%)':^12}|{'Max CPU (%)':^12}|{'Avg Mem (MB)':^14}|{'Max Mem (MB)':^14}")
    print("-" * 85)
    for result in results:
        print(f"{result['batch_size']:^10}|{result['pages']:^7}|{result['time']:^10.2f}|" +
              f"{result.get('avg_cpu', 0):^12.1f}|{result.get('max_cpu', 0):^12.1f}|" +
              f"{result.get('avg_memory', 0):^14.1f}|{result.get('max_memory', 0):^14.1f}")

if __name__ == "__main__":
    # 单次执行
    # detect_layout("test.pdf")
    
    # 批次大小基准测试
    benchmark_batch_sizes("test.pdf")
