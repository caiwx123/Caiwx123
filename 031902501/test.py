import sys
import unittest


from main import AC



class MyTestCase(unittest.TestCase):
    def test1(self):  # 汉字转拼音
        ac = AC("D:\data\words1.txt")
        x = '我'
        x =ac.c_pinyin(x)
        y = 'wo'
        self.assertEqual(x, y)

    def test2(self):
        ac = AC(r'D:\data\words1.txt')
        ac.search(r'D:\data\org1.txt')
        ac.out_f(r'D:\data\ans.txt')
        f1 = ''
        f2 = ''
        with open(r'D:\data\ans.txt','r', encoding='UTF-8') as file_out:
            f1=file_out.read()
        with open(r'D:\data\ans2.txt','r', encoding='UTF-8') as file_out:
            f2=file_out.read()
        self.assertEqual(f1, f2)

if __name__ == '__main__':
    unittest.main()
