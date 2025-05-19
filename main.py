import heapq
from typing import Optional

from sympy.benchmarks.bench_meijerint import bench

from hcb import *
import threading
import keyboard  # pip install keyboard
import time
import pydirectinput


class OverlayWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.box_objects = []  # 中间box
        self.box_have = []  # 两边box
        self.grid_map = {}  # (row, col) -> 中间box
        self.element_boxes = []  # 中间box已识别
        self.element_boxes_have = {}  # 两边box已识别
        self.highlight_paths = []  # 放的路
        self.placement = {}  # 放法
        self.res = []
        self.mp = [[] for i in range(500)]
        self.flag = 0

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        # 全屏覆盖
        desktop = QtWidgets.QApplication.desktop()
        self.setGeometry(desktop.geometry())

        # 点击穿透
        hwnd = int(self.winId())
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x80000
        WS_EX_TRANSPARENT = 0x20
        WS_EX_TOOLWINDOW = 0x80
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style |= WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

        # 在后台线程监听全局快捷键
        threading.Thread(target=self.listen_hotkey, daemon=True).start()  # 添加快捷键触发
        threading.Thread(target=self.listen_hotkey2, daemon=True).start()  # 添加快捷键触发

    def listen_hotkey(self):
        keyboard.add_hotkey('ctrl+8', lambda: self.detect_boxes())
        keyboard.wait()  # 阻塞线程防止退出

    def listen_hotkey2(self):
        keyboard.add_hotkey('ctrl+5', lambda: self.mov())
        keyboard.wait()  # 阻塞线程防止退出

    def detect_boxes(self):
        # 初始化
        self.box_objects = []  # 中间box
        self.box_have = []  # 两边box
        self.grid_map = {}  # (row, col) -> 中间box
        self.element_boxes = []  # 中间box已识别
        self.element_boxes_have = {}  # 两边box已识别
        self.highlight_paths = []  # 放的路
        self.placement = {}  # 放法
        self.res = []

        lines = open(CONFIG_PATH, 'r').readlines()

        # 读两层点阵
        for layer in (0, 1):
            x0, y0, hs, hn, vs, vn, bs = map(float, lines[layer].split(','))
            bs = round(bs)
            for i in range(int(vn)):
                for j in range(int(hn)):
                    x = round(x0 + j * hs - bs / 2 + 32)
                    y = round(y0 + i * vs - bs / 2 + 32)
                    if layer == 0:
                        row, col = i * 2 + 1, j * 2
                    else:
                        row, col = i * 2, j * 2 + 1
                    b = Box(x, y, bs, row, col)
                    self.box_objects.append(b)
                    self.grid_map[(row, col)] = b

        for layer in (2, 3):
            x0, y0, hs, hn, vs, vn, bs = map(float, lines[layer].split(','))
            bs = round(bs)
            for i in range(int(vn)):
                for j in range(int(hn)):
                    x = round(x0 + j * hs - bs / 2 + 32)
                    y = round(y0 + i * vs - bs / 2 + 32)
                    b = Box(x, y, bs)
                    self.box_have.append(b)

        # 截图前隐藏窗口
        if self.flag:
            self.hide()
            QtWidgets.QApplication.processEvents()
            self.flag = 0
            return
        self.flag = 1
        screen = ImageGrab.grab()
        self.show()
        QtWidgets.QApplication.processEvents()
        # screen.show()

        all_box = {}
        self.serah = {}
        self.mp = [[] for i in range(500)]
        idx = 0
        cs = []

        for box in self.box_objects:
            r = box.rect
            crop = screen.crop((r.left(), r.top(), r.right(), r.bottom())).convert("RGB")
            pred = see(crop)
            box.label = pred
            if pred != 0:  # 0表示空
                all_box[(box.row, box.col)] = idx
                self.serah[idx] = (box.row, box.col)
                if box.label != 1:
                    cs.append((idx, box.label))
                idx += 1

        for box in self.box_have:
            r = box.rect
            crop = screen.crop((r.left(), r.top(), r.right(), r.bottom())).convert("RGB")
            pred = see(crop)
            box.label = pred
            if pred != 0:  # 0表示空
                self.element_boxes_have[pred] = box

        # 计算最优路径
        for k, v in all_box.items():
            ccs = get_hex_neighbors(k[0], k[1])
            for i, j in ccs:
                if (i, j) in all_box:
                    self.mp[v].append(all_box[(i, j)])
                    self.mp[all_box[(i, j)]].append(v)


        def find_paths_by_length(start: int, end: int, max_len: Optional[int] = 20) -> Dict[int, List[int]]:
            """
            在无向图 mp 上，查找从节点 start 到 end 的简单路径，
            对每个可能的长度 L返回一条路径。

            参数：
            - start: 起始节点 ID
            - end: 目标节点 ID
            - max_len: 搜索最大长度上界，默认为12

            返回：
            - dict: 键为路径长度 L，值为节点 ID 列表（含 start 和 end）
            """
            if max_len is None:
                max_len = 12
            result = {}
            # 处理起始节点等于结束节点的情况
            if start == end:
                return {0: [start]}
            # 初始化队列
            queue = deque()
            queue.append((start, 0, [start]))
            # visited记录每个节点已经处理过的路径长度
            visited = {start: {0}}
            while queue:
                u, current_len, path = queue.popleft()
                # 遍历所有邻居
                for v in self.mp[u]:
                    new_len = current_len + 1
                    if new_len > max_len:
                        continue
                    new_path = path + [v]
                    # 检查是否是终点
                    if v == end:
                        if new_len not in result:
                            result[new_len] = new_path
                    if vis[v] == 1:
                        continue
                    # 更新visited和队列
                    # 检查是否已经处理过该节点的该长度

                    lengths = visited.get(v, set())
                    if new_len not in lengths:
                        visited[v] = lengths | {new_len}
                        queue.append((v, new_len, new_path))
            return result


        def min_cost_item_sequence(src: int,
                                   dst: int,
                                   min_steps: int) -> Optional[tuple[int, list[int]]]:
            """
            在max_steps 步，找一条从 src 到 dst 的“连通路径”，
            使得中间所有物品代价总和最小。返回 (total_cost, [src, ..., dst])。
            如果无解，返回 None。
            """
            # 小顶堆元素：(当前总代价 cost, 当前路径 path_list)
            # 初始状态：只放 src，花费记为 src 本身的 cost
            heap = [(memo[src], [src])]
            # 用于简单剪枝：记录 (物品ID, 经过步数) 对应已知最优代价
            best = {(src, 0): memo[src]}

            while heap:
                cost, patha = heapq.heappop(heap)
                path = patha.copy()
                last = path[-1]
                steps = len(path) - 1
                # 超出允许步数
                if steps == min_steps and is_con(last, dst):
                    # 如果最后一步就能连到 dst，就直接返回
                    return cost + memo[dst], path + [dst]

                elif steps > min_steps:
                    continue

                if steps>min_steps+3:
                    return None

                # 枚举 last 能连通的所有下一个物品 next_id
                # 这里简单遍历所有 memo 键，也可以预先构建 con_idx 加速
                for next_id in cont[last]:
                    new_cost = cost + memo[next_id]
                    new_steps = steps + 1
                    key = (next_id, new_steps)
                    # 剪枝：如果这一步数、这物品的新代价不如已有记录，则跳过
                    if key in best and best[key] <= new_cost:
                        continue

                    best[key] = new_cost
                    heapq.heappush(heap, (new_cost, (path + [next_id]).copy()))
            return None

        #print(min_cost_item_sequence(44,31,3))

        ok = set()
        # cs
        ccs = []
        for i, _ in cs:
            ccs.append(i)

        if len(ccs)==0:
            return
        ok.add(ccs[0])
        ccs.pop(0)

        vis = [0] * 500

        while len(ccs):
            dan = {}
            for i in ok:
                for j in ccs:
                    ii = self.grid_map[self.serah[i]]
                    jj = self.grid_map[self.serah[j]]
                    fpbl = find_paths_by_length(i, j)
                    #print(fpbl, self.serah[i], self.serah[j])
                    bs = []
                    dj = {}
                    for k, v in fpbl.items():
                        aaaaa = min_cost_item_sequence(ii.label, jj.label, k-1)
                        if aaaaa is None:
                            continue
                        ww, wp = aaaaa[0], aaaaa[1]
                        dj[ww] = (wp, k)
                        bs.append(ww)
                    bs.sort()
                    if len(bs)==0:
                        continue
                    dan[bs[0]] = (fpbl[dj[bs[0]][1]], dj[bs[0]][0])

            bs = []
            for k, v in dan.items():
                bs.append(k)
            bs.sort()
            if len(bs)==0:
                break
            self.res.append(dan[bs[0]])
            ccs.remove(dan[bs[0]][0][-1])

            for i in range(len(dan[bs[0]][0])):
                vis[dan[bs[0]][0][i]] = 1
                self.grid_map[self.serah[dan[bs[0]][0][i]]].label = dan[bs[0]][1][i]
                ok.add(dan[bs[0]][0][i])

        # 示例用法
        # paths_by_len = find_paths_by_length(mp, 0, 5)
        # print(paths_by_len)

        # 示例调用：
        # result = steiner_approx(memo, mp, cs, is_con)
        # print("额外放置：", result)

        # 示例调用：
        # result = steiner_approx(memo, mp, cs, is_con)
        # print("额外放置：", result)

        # ——示例调用——
        # result = steiner_approx(memo, mp, cs, is_con)
        # print("额外放置：", result)

        print(self.res)

        self.update()
        # print(self.element_boxes_have)
        # print()



    def mov(self):
        is_ok = set()

        for ans in self.res:
            for jj in range(0, len(ans[0])-1):
                if ans[0][jj] in is_ok:
                    continue
                is_ok.add(ans[0][jj])
                be = self.grid_map[self.serah[ans[0][jj]]]
                bs = self.element_boxes_have[ans[1][jj]]
                # 起始位置（你要拖动的东西的位置）
                start_x, start_y = bs.x + 24, bs.y + 24
                # 目标位置（你要拖动到哪里）
                end_x, end_y = be.x + 24, be.y + 24

                pydirectinput.moveTo(start_x, start_y)
                pydirectinput.mouseDown()
                sleep(0.1)
                pydirectinput.moveTo(end_x, end_y, duration=0.3)
                pydirectinput.mouseUp()

    def paintEvent(self, ev):
        p = QtGui.QPainter(self)

        # —— 原来的背景网格、路径、格子绘制 —— #
        # # 画背景网格（淡青色）
        # for i in range(len(self.mp)):
        #     for j in range(len(self.mp[i])):
        #         b = self.grid_map[self.serah[i]]
        #         bb = self.grid_map[self.serah[self.mp[i][j]]]
        #
        #         p.setPen(QtGui.QPen(QtGui.QColor(0, 240, 240), 1))
        #         p.drawLine(b.center, bb.center)

        # # 画最小连通路径（粗黄色）
        p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 0), 5))
        # for a, b in self.highlight_paths:
        #     p.drawLine(a.center, b.center)

        for i in self.res:
            o = self.grid_map[self.serah[i[0][0]]]
            for j in range(1, len(i[0])):
                n = self.grid_map[self.serah[i[0][j]]]
                p.drawLine(o.center, n.center)
                o = n

            # b = self.grid_map[self.serah[i[0]]]
            # text = ids[i[1]]
            # pos = b.center + QtCore.QPoint(-p.fontMetrics().width(text) // 2, +4)
            # p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 4))
            # p.drawText(pos, text)

        # 再画已有格子上的元素
        for b in self.box_objects:
            b.draw(p)
        for b in self.box_have:
            b.draw(p)
        p.end()


if __name__ == '__main__':
    print("[INFO] Overlay started.")
    app = QtWidgets.QApplication(sys.argv)
    w = OverlayWindow()
    w.show()
    sys.exit(app.exec_())
