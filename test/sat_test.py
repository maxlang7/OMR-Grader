import unittest
import json
import grader as g

class ExampleImageTests(unittest.TestCase):
    debug_mode = True #turn both to true to see images.
    verbose_mode = True

    def test_page1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['D', 'C', 'C', 'D', 'C', 'C', 'D'])

    def test_page2(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['A', 'B', 'C', 'B', 'D', 'C', 'B'])
    
    def test_page3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3, 2)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:8], ['D', 'B', 'A', 'B', 'B', 'C', 'A', 'C'])
        

    def test_page4(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['A', 'C', 'A', 'C', 'B', 'D', 'C'])

    def test_page5(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])
    
    def test_page1a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertEqual(data['answer']['bubbled'], ['D', 'B', 'A', 'A', 'D', 'A', 'D', 'B', 'B', 'D', 'D', 'D', 'A', 'D', 'D', 'A', 'C', 'C', 'A', 'B', 'C', 'B', 'B', 'B', 'C', 'B', 'D', 'D', 'B', 'B', 'C', 'B', 'B', 'A', 'C', 'A', 'B', 'C', 'A', 'A', 'B', 'D', 'D', 'B', 'A', 'B', 'C', 'A', 'C', 'B', 'D', 'A'])
        
    def test_page1b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        print(data['answer']['bubbled'])

        self.assertEqual(data['answer']['bubbled'][0:7], ['A', 'C', 'D', 'D', 'A', 'D', 'D'])
    
    def test_page2a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(data['answer']['bubbled']),44)        
        self.assertEqual(data['answer']['bubbled'], 'B B A A D D B D B'.split(' ') +
                                                    'B B B D C C C B B'.split(' ') +
                                                    'A D D B A B B D D'.split(' ') +
                                                    'A C C B B B D A A'.split(' ') +
                                                    'D B C D D B A C'.split(' ') )

    def test_page2b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(data['answer']['bubbled']),44)
        self.assertEqual(data['answer']['bubbled'], 'D B C B D C B C A'.split(' ') +
                                                    'D A A D C A D C B'.split(' ') +
                                                    'D A B D C C C A C'.split(' ') +
                                                    'B B B B D B B D B'.split(' ') +
                                                    'B D C D B C D D'.split(' ') )
 
    def test_page3a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3, 1)
        data = json.loads(jsonData)

        self.assertEqual(len(data['answer']['bubbled']),9)
        self.assertEqual(data['answer']['bubbled'], 'C B A'.split(' ') +
                                                    'A C C'.split(' ') +
                                                    'A D B'.split(' ') )
                                                    

    def test_page3_box2a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3, 2)
        data = json.loads(jsonData)

        self.assertEqual(len(data['answer']['bubbled']),15)
        self.assertEqual(data['answer']['bubbled'], 'C B A'.split(' ') +
                                                    'A C C'.split(' ') +
                                                    'A D B'.split(' ') +
                                                    'C C B'.split(' ') +
                                                    'D A D'.split(' ') )                                                
    
    def test_page3b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3, 2)
        data = json.loads(jsonData)

        self.assertEqual(len(data['answer']['bubbled']),15)
        self.assertEqual(data['answer']['bubbled'], 'D B A'.split(' ') +
                                                    'B B B'.split(' ') +
                                                    'C D A'.split(' ') +
                                                    'B B D'.split(' ') +
                                                    'C D B'.split(' ') )

    def test_page4a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(data['answer']['bubbled']),30 )
        self.assertEqual(data['answer']['bubbled'], 'C B A C C B'.split(' ') +
                                                    'D D A B B D'.split(' ') +
                                                    'B C A B C C'.split(' ') +
                                                    'B C D B C A'.split(' ') +
                                                    'B D C B A B'.split(' ') )

    def test_page4b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(data['answer']['bubbled']),30)
        self.assertEqual(data['answer']['bubbled'], 'A C A C B D'.split(' ') +
                                                    'C A A A D C'.split(' ') +
                                                    'A D D B A C'.split(' ') +
                                                    'A A D A B D'.split(' ') +
                                                    'B A D A D B'.split(' ') )
    
    def test_page5a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])
    
    def test_page5b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])
if __name__ == '__main__':
    unittest.main()