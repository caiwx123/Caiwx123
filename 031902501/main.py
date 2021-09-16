
import pypinyin
import sys


class Node(object):
    def __init__(self, value=None):
        # value = 单个词的拼音 ， fail = 跳转结点位置 ， next = 子结点字典 ，word = 到目前节点所产生的的垃圾词

        self.value = value
        self.fail = None
        self.next = dict()
        self.word = ''


class AC(object):
    # 以AC自动机来解决垃圾邮件过滤

    def __init__(self, words):
        # line:行号列表 lj_in_txt:文中垃圾词列表  lj_words: 垃圾词原型的列表 count:已发现几个敏感词
        self.line = []
        self.lj_in_txt = []
        self.lj_words = []
        self.count = 0
        self.pinyin = dict()
        self.root = AC.ac_build(self, words)

    def c_pinyin(self, c):
        if c in self.pinyin.keys():
            c = self.pinyin[c]
        else:
            s = c
            for x in pypinyin.pinyin(c, style=pypinyin.NORMAL):
                c = ''.join(x)
            self.pinyin[s] = c
        return c

    def ac_build(self, f):
        # 建立AC自动机
        words = ''
        try:
            with open(f, 'r', encoding='UTF-8') as file_object:
                words = file_object.read().split('\n')
        except FileNotFoundError:
            print("无法打开指定文件")
        except UnicodeError:
            print("读文件时解码错误")
        root = Node()
        # 树建立 key为拼音
        for word in words:
            # p 父亲结点列表
            p = []
            p.append(root)
            for c in word:
                # 判断c是否为中文 是中文则改成拼音
                if '\u4e00' <= c <= '\u9fff':
                    c=self.c_pinyin(c)
                else:
                    # 将字母小写化
                    c = c.lower()
                if c in p[0].next.keys():
                    p[0] = p[0].next[c]
                    continue
                else:
                    # 建树的结点有 全拼音 以及 拼音首字母 例如 ‘lun’ 以及 ‘l'
                    son = []
                    son.append(Node(c))
                    if len(c) > 1:
                        # 全拼音首字母
                        son.append(Node(c[0]))
                    # 11111111111111 加个识别这个汉字可否拆分

                    # 连接父亲结点与儿子结点
                    for i in range(0, len(p)):
                        for s in son:
                            p[i].next[s.value] = s
                    # 多字母拼音的连接
                    if len(c) > 1:
                        # 单个首字母
                        son.append(son[1])
                        # 将 全拼音变成 多个单拼音进行连接 例如 ’lun‘ 变成 ’l‘->'u'->'n'
                        for x in range(1, len(c)):
                            son[1].next[c[x]] = Node(c[x])
                            son[1] = son[1].next[c[x]]

                    # 22222222222 加个如果是汉字拆分后建树
                p = son.copy()
            for i in range(0, len(p)):
                p[i].word = word
        # fail 指针的连接
        q = []
        q.insert(0, root)
        while q:
            parent = q.pop()
            for i in parent.next.values():
                temp = parent.fail
                while True:
                    if not temp:
                        i.fail = root
                        break
                    else:
                        if i.value in temp.next.keys():
                            i.fail = temp.next[i.value]
                            break
                    temp = temp.fail
                q.insert(0, i)
        root.fail = root
        return root

    def search(self, f):
        # 从f中寻找敏感词汇并写入out_file
        t = []
        try:
            with open(f, 'r', encoding='UTF-8') as file_object:
                t = file_object.read().split('\n')
        except FileNotFoundError:
            print("无法打开指定文件")
        except UnicodeError:
            print("读文件时解码错误")

        for j in range(0, len(t)):
            # txt:原文的第J行 tg:文中垃圾词中最后出现的连续的无意字符个数 begin:垃圾词的开头index
            txt = t[j]
            p = self.root
            tg = 0
            begin = 0
            i = -1
            while i < len(txt) - 1:
                i += 1
                c = txt[i]
                if p == self.root:
                    begin = i
                if '\u4e00' <= c <= '\u9fff':
                    # 前面已经出现了超过20个连续无意字符 则前面的词失效
                    if tg > 20:
                        begin = i
                        tg = 0
                    # 将中文转成拼音
                    c=self.c_pinyin(c)
                elif 'a' <= c <= 'z' or 'A' <= c <= 'Z':
                    c = c.lower()
                # 此词为无意词 进行 相应操作并跳过
                elif tg <= 20:
                    tg += 1
                    continue
                else:
                    if p.word:
                        self.put_in(j, p.word, txt[begin:i - tg])
                    p = self.root
                    tg = 0
                    continue
                if c in p.next.keys():
                    p = p.next[c]
                    tg = 0
                else:
                    if p == self.root:
                        tg = 0
                        continue
                    if p.word:
                        self.put_in(j, p.word, txt[begin:i - tg])
                        i -= 1
                        p = self.root
                        continue
                    p = p.fail
                    i -= 1
            # 解决由于垃圾词在结尾的问题
            if p.word:
                self.put_in(j, p.word, txt[begin:i + 1 - tg])

    def put_in(self, j, word, word_in_txt):
        # 将词入库

        self.line.append(j)
        self.lj_words.append(word)
        self.lj_in_txt.append(word_in_txt)
        self.count += 1

    def out_f(self, out_file):
        # 输出到文件中
        try:
            with open(out_file, 'w', encoding='UTF-8') as file_out:
                file_out.write(f"Total : {self.count}")
                file_out.write('\n')
                for i in range(0, self.count):
                    file_out.write(f"Line{self.line[i] + 1}: <{self.lj_words[i]}> {self.lj_in_txt[i]}")
                    file_out.write('\n')
        except FileNotFoundError:
            print("无法打开指定文件")
        except UnicodeError:
            print("读文件时解码错误")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Wrong number of parameters\nplease reenter")
    else:
        words = sys.argv[1]
        org = sys.argv[2]
        ans = sys.argv[3]
        ac = AC(words)
        ac.search(org)
        ac.out_f(ans)

