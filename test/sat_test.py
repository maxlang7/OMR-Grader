import unittest
import json
import grader as g
from wand.image import Image

class ExampleImageTests(unittest.TestCase):
    #turn both to true to see images.
    verbose_mode = False
    debug_mode = verbose_mode

    def test_page1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),52)        
        self.assertEqual(list(data['answer']['bubbled'].values()), 'B C A A C A A B B D D D C'.split(' ') +
                                                                    'B B C B B A A D A A B C C'.split(' ') +
                                                                    'B B D D B C C D C A D C A'.split(' ') +
                                                                    'D A C C D D C B B A B D D'.split(' ') )

    def test_page2(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),44)        
        self.assertEqual(list(data['answer']['bubbled'].values()),'A B C C A B A D C'.split(' ') +
                                                    'C B A C D B C C B'.split(' ') +
                                                    'D C D A A D B A D'.split(' ') +
                                                    'B A A D B C C B C'.split(' ') +
                                                    'B C C B D A D D'.split(' ') )
    
    def test_page3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3, 1)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),15)
        self.assertEqual(list(data['answer']['bubbled'].values()), 'C D D'.split(' ') +
                                                    'B C C'.split(' ') +
                                                    'C A -'.split(' ') +
                                                    'A C -'.split(' ') +
                                                    '- A D'.split(' ') )   
    
    def test_page3_box2(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3, 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),5)
        self.assertEqual(list(data['answer']['bubbled'].values()), ['-', '-', '-', 320.0, '-'] )
    
        

    def test_page4(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),30 )
        self.assertEqual(list(data['answer']['bubbled'].values()), 'C B C C B A'.split(' ') +
                                                    'D C B D B D'.split(' ') +
                                                    'D A A B B B'.split(' ') +
                                                    'C B C - C -'.split(' ') +
                                                    'D C C D A A'.split(' ') )

    def test_page5(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5, 1)
        data = json.loads(jsonData)
        self.assertEqual(len(list(data['answer']['bubbled'].values())),5)
        self.assertEqual(list(data['answer']['bubbled'].values()), [6.0, 58.6, 9.0, 0.625, '-'])
    
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

        self.assertEqual(len(list(data['answer']['bubbled'].values())),5)
        self.assertEqual(list(data['answer']['bubbled'].values()), [3.0, 32.0, 1.5, 8.0, 144] )
   
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
        self.assertEqual(len(list(data['answer']['bubbled'].values())),3)
        self.assertEqual(list(data['answer']['bubbled'].values()), [32.0, 3284.0, 7500.0])
    
    def test_page5a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5, 1)
        data = json.loads(jsonData)
        self.assertEqual(len(list(data['answer']['bubbled'].values())),5)
        self.assertEqual(list(data['answer']['bubbled'].values()), [14.0, 7.0, 11.0, 105.0, 15.0])
        
    
    def test_page5b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5, 1)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['answer']['bubbled'].values())),5)
        self.assertEqual(list(data['answer']['bubbled'].values()), [102.0, 2.0, 60.0, 25.4, '-'])
    
    def test_page5_box2b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5, 2)
        data = json.loads(jsonData)
        self.assertEqual(len(list(data['answer']['bubbled'].values())),3)
        self.assertEqual(list(data['answer']['bubbled'].values()), ['-', 34.0, '-'])
if __name__ == '__main__':
    unittest.main()