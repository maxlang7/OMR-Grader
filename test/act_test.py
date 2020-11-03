import unittest
import json
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
import grader as g
from wand.image import Image

class ExampleActTests(unittest.TestCase):
    #turn both to true to see images.
    verbose_mode = False
    debug_mode = verbose_mode

    def test_act_page1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/act_test1.JPG', self.debug_mode, self.verbose_mode, 1.0, 'act', 1)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),215)        
        self.assertEqual(list(data['answer']['bubbled'].values()), 'B C A A C A A B B D D D C'.split(' ') +
                                                                    'B B C B B A A D A A B C C'.split(' ') +
                                                                    'B B D D B C C D C A D C A'.split(' ') +
                                                                    'D A C C D D C B B A B D D'.split(' ') )
    def test_act_page1a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/act_test1a.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        
        self.assertEqual(len(list(data['answer']['bubbled'].values())),215)        
        self.assertEqual(list(data['answer']['bubbled'].values()), 'B C A A C A A B B D D D C'.split(' ') +
                                                                    'B B C B B A A D A A B C C'.split(' ') +
                                                                    'B B D D B C C D C A D C A'.split(' ') +
                                                                    'D A C C D D C B B A B D D'.split(' ') )    
    def test_act_page1b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/act_test1b.jpeg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertEqual(len(list(data['answer']['bubbled'].values())),215)        
        self.assertEqual(list(data['answer']['bubbled'].values()), 'D C B D A D D A B C C D D'.split(' ') +
                                                                    'C D D C B C A C A D A B C'.split(' ') +
                                                                    'B D D C D B A B C A D D B'.split(' ') +
                                                                    'A C C C A B D D B B D B A'.split(' ') )
    
    def test_act_page1c(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/act_test1c.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertEqual(len(list(data['answer']['bubbled'].values())),215)        
        self.assertEqual(list(data['answer']['bubbled'].values()), 'D C B D A D D A B C C D D'.split(' ') +
                                                                    'C D D C B C A C A D A B C'.split(' ') +
                                                                    'B D D C D B A B C A D D B'.split(' ') +
                                                                    'A C C C A B D D B B D B A'.split(' ') )        
if __name__ == '__main__':
    unittest.main()