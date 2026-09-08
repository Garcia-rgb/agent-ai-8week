import json


# 1. 列表：按顺序保存多个数据
names = ["apple", "banana", "apple", "orange", "banana"]

# 2. 循环和判断：去掉重复内容
unique_names = []

for name in names:
    if name not in unique_names:
        unique_names.append(name)

print("去重结果：", unique_names)


# 3. 字典：统计每个数据出现的次数
counts = {}

for name in names:
    if name not in counts:
        counts[name] = 1
    else:
        counts[name] += 1

print("出现次数：", counts)


# 4. 函数：把一段功能包装起来
def count_words(items):
    result = {}

    for item in items:
        result[item] = result.get(item, 0) + 1

    return result


print("函数结果：", count_words(names))


# 准备一些任务数据
tasks = [
    {"title": "学习 Python", "done": True},
    {"title": "学习 FastAPI", "done": False},
]

file_path = "tasks.json"


# 1. 保存到 JSON 文件
def save_tasks(tasks: list[dict], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)
    print("任务已保存")


# 2. 从 JSON 文件读取
def load_tasks(file_path: str) -> list[dict]:
    try:
        with open(file_path, encoding="utf-8") as file:
            loaded_tasks = json.load(file)
        print(loaded_tasks)
        return loaded_tasks

    except FileNotFoundError:
        print(f"文件不存在：{file_path}")
        return []

    except json.JSONDecodeError:
        print(f"JSON 内容损坏：{file_path}")
        return []


save_tasks(tasks, "tasks.json")
load_tasks(file_path)
