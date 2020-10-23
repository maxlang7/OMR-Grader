import unittest
import json
import grader as g
from wand.image import Image

class ExampleImageTests(unittest.TestCase):
    #turn both to true to see images.
    verbose_mode = True
    debug_mode = verbose_mode

    def test_page1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)

        self.assertEqual(list(data['answer']['bubbled'].values())[0:7], ['D', 'C', 'C', 'D', 'C', 'C', 'D'])

    def test_page2(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(list(data['answer']['bubbled'].values())[0:7], ['A', 'B', 'C', 'B', 'D', 'C', 'B'])
    
    def test_page3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3, 2)
        data = json.loads(jsonData)

        self.assertEqual(list(data['answer']['bubbled'].values())[0:8], ['D', 'B', 'A', 'B', 'B', 'C', 'A', 'C'])
        

    def test_page4(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(list(data['answer']['bubbled'].values())[0:7], ['A', 'C', 'A', 'C', 'B', 'D', 'C'])

    def test_page5(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)

        self.assertEqual(list(data['answer']['bubbled'].values())[0:7], ['', '', 'B', 'A', 'C', '', ''])
    
    def test_page1a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertEqual(list(data['answer']['bubbled'].values()), ['D', 'B', 'A', 'A', 'D', 'A', 'D', 'B', 'B', 'D', 'D', 'D', 'A', 'D', 'D', 'A', 'C', 'C', 'A', 'B', 'C', 'B', 'B', 'B', 'C', 'B', 'D', 'D', 'B', 'B', 'C', 'B', 'B', 'A', 'C', 'A', 'B', 'C', 'A', 'A', 'B', 'D', 'D', 'B', 'A', 'B', 'C', 'A', 'C', 'B', 'D', 'A'])
    
    def test_jpgtest(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1a.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertEqual(list(data['answer']['bubbled'].values()), ['D', 'B', 'A', 'A', 'D', 'A', 'D', 'B', 'B', 'D', 'D', 'D', 'A', 'D', 'D', 'A', 'C', 'C', 'A', 'B', 'C', 'B', 'B', 'B', 'C', 'B', 'D', 'D', 'B', 'B', 'C', 'B', 'B', 'A', 'C', 'A', 'B', 'C', 'A', 'A', 'B', 'D', 'D', 'B', 'A', 'B', 'C', 'A', 'C', 'B', 'D', 'A'])

    def test_heictest(self):
        grader = g.Grader()
        with Image(filename='test/images/sat_test1a.heic') as img:  
            img.format = 'jpeg'
            img.save(filename='test/images/sat_test1a.heic_jpeg')
        jsonData = grader.grade('test/images/sat_test1a.heic_jpeg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertEqual(list(data['answer']['bubbled'].values()), ['D', 'B', 'A', 'A', 'D', 'A', 'D', 'B', 'B', 'D', 'D', 'D', 'A', 'D', 'D', 'A', 'C', 'C', 'A', 'B', 'C', 'B', 'B', 'B', 'C', 'B', 'D', 'D', 'B', 'B', 'C', 'B', 'B', 'A', 'C', 'A', 'B', 'C', 'A', 'A', 'B', 'D', 'D', 'B', 'A', 'B', 'C', 'A', 'C', 'B', 'D', 'A'])
    
    def test_page1b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        print(list(data['answer']['bubbled'].values()))

        self.assertEqual(list(data['answer']['bubbled'].values())[0:7], ['A', 'C', 'D', 'D', 'A', 'D', 'D'])
    
    def test_page2a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),44)        
        self.assertEqual(list(data['answer']['bubbled'].values()), 'B B A A D D B D B'.split(' ') +
                                                    'B B B D C C C B B'.split(' ') +
                                                    'A D D B A B B D D'.split(' ') +
                                                    'A C C B B B D A A'.split(' ') +
                                                    'D B C D D B A C'.split(' ') )

    def test_page2b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),44)
        self.assertEqual(list(data['answer']['bubbled'].values()), 'D B C B D C B C A'.split(' ') +
                                                    'D A A D C A D C B'.split(' ') +
                                                    'D A B D C C C A C'.split(' ') +
                                                    'B B B B D B B D B'.split(' ') +
                                                    'B D C D B C D D'.split(' ') )
 
    def test_page3_box2a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3, 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),5)
        self.assertEqual(list(data['answer']['bubbled'].values()), [3.0, 19.0, 12.0, 6.0, 0.25] )
                                                          

    def test_page3a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3, 1)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),15)
        self.assertEqual(list(data['answer']['bubbled'].values()), 'C B A'.split(' ') +
                                                    'A C C'.split(' ') +
                                                    'A D B'.split(' ') +
                                                    'C C B'.split(' ') +
                                                    'D A D'.split(' ') )                                                
    
    def test_page3b_box2b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3, 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),20)
        self.assertEqual(list(data['answer']['bubbled'].values()), '- - - 4'.split(' ') +
                                                    '- - 5 3'.split(' ') +
                                                    '- 5 0 3'.split(' ') +
                                                    '- - - 9'.split(' ') +
                                                    '- 3 6 5'.split(' ') )   
    def test_page3b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3, 1)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),15)
        self.assertEqual(list(data['answer']['bubbled'].values()), 'D B A'.split(' ') +
                                                    'B B B'.split(' ') +
                                                    'C D A'.split(' ') +
                                                    'B B D'.split(' ') +
                                                    'C D B'.split(' ') ) 

    def test_page4a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),30 )
        self.assertEqual(list(data['answer']['bubbled'].values()), 'C B A C C B'.split(' ') +
                                                    'D D A B B D'.split(' ') +
                                                    'B C A B C C'.split(' ') +
                                                    'B C D B C A'.split(' ') +
                                                    'B D C B A B'.split(' ') )

    def test_page4b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),30)
        self.assertEqual(list(data['answer']['bubbled'].values()), 'A C A C B D'.split(' ') +
                                                    'C A A A D C'.split(' ') +
                                                    'A D D B A C'.split(' ') +
                                                    'A A D A B D'.split(' ') +
                                                    'B A D A D B'.split(' ') )
    
    def test_page5_box2a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5, 2)
        data = json.loads(jsonData)
        self.assertEqual(len(list(data['answer']['bubbled'].values())),12)
        self.assertEqual(list(data['answer']['bubbled'].values()), '- - 5 3'.split(' ') +
                                                    '4 4 10 5'.split(' ') +
                                                    '8 7 2 1'.split(' ') )
    
    def test_page5a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5, 1)
        data = json.loads(jsonData)
        self.assertEqual(len(list(data['answer']['bubbled'].values())),20)
        self.assertEqual(list(data['answer']['bubbled'].values()), '- - 3 5'.split(' ') +
                                                    '- - - 8'.split(' ') +
                                                    '- - 3 2'.split(' ') +
                                                    '- 3 2 6'.split(' ') +
                                                    '- - 3 6'.split(' ') )
        
    
    def test_page5b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5, 1)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),20)
        self.assertEqual(list(data['answer']['bubbled'].values()), '- 3 2 3'.split(' ') +
                                                    '- - - 3'.split(' ') +
                                                    '- - 8 1'.split(' ') +
                                                    '3 7 1 5'.split(' ') +
                                                    '- - - -'.split(' ') )
    
    def test_page5_box2b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5, 2)
        data = json.loads(jsonData)
        self.assertEqual(len(list(data['answer']['bubbled'].values())),12)
        self.assertEqual(list(data['answer']['bubbled'].values()), '- - - -'.split(' ') +
                                                    '- - 5 5'.split(' ') +
                                                    '- - - -'.split(' ') )
if __name__ == '__main__':
    unittest.main()